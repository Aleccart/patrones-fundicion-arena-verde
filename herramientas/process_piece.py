import sys, os, json, time, argparse
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from matplotlib.colors import LightSource
from hfcast import *

ap = argparse.ArgumentParser()
ap.add_argument('--mesh', required=True)
ap.add_argument('--outdir', required=True)
ap.add_argument('--tag', required=True)
ap.add_argument('--name', required=True)
ap.add_argument('--orient', default='auto')
ap.add_argument('--pitch', type=float, default=0.4)
ap.add_argument('--a', type=float, default=3.0)
ap.add_argument('--acope', type=float, default=4.5)
ap.add_argument('--draft', type=float, default=3.0)
ap.add_argument('--rin', type=float, default=3.0)
ap.add_argument('--dkeep', type=float, default=24.0)
ap.add_argument('--shrink', type=float, default=0.013)
ap.add_argument('--nrisers', type=int, default=0)
ap.add_argument('--riserf', type=float, default=1.2)
ap.add_argument('--revolve', action='store_true')
A = ap.parse_args()
os.makedirs(A.outdir, exist_ok=True)
T0 = time.time()
tanA = np.tan(np.radians(A.draft))


def log(*a):
    print('[%5.1fs]' % (time.time() - T0), *a, flush=True)


def prepare(Vo, p):
    mn = Vo.reshape(-1, 3).min(axis=0)
    mx = Vo.reshape(-1, 3).max(axis=0)
    zmin = mn[2]
    H0 = mx[2] - zmin
    margin = A.a + (H0 + A.acope + A.a) * tanA + A.dkeep / 2 + (A.rin + A.a) + 12
    x0, y0 = mn[0] - margin, mn[1] - margin
    nx = int(np.ceil((mx[0] + margin - x0) / p))
    ny = int(np.ceil((mx[1] + margin - y0) / p))
    return dict(mn=mn, mx=mx, zmin=zmin, zback=zmin - A.acope, H0=H0, x0=x0, y0=y0, nx=nx, ny=ny)


def hf_blank(Vo, p):
    g = prepare(Vo, p)
    # z-buffer con doble resolucion y reduccion por maximo: la pieza nunca se subestima mas de p/2
    top0 = zbuffer(Vo, p / 2, g['x0'], g['y0'], 2 * g['nx'], 2 * g['ny'])
    top0 = top0.reshape(g['nx'], 2, g['ny'], 2).max(axis=(1, 3))
    a_eff = A.a + p / 2 + 0.35
    rev = None
    if A.revolve:
        ii_, jj_ = np.where(top0 > -BIG / 2)
        rev = (g['x0'] + (ii_.mean() + 0.5) * p, g['y0'] + (jj_.mean() + 0.5) * p)
    T2, closed, _ = build_topmap(top0, p, a_eff, A.draft, A.rin, A.dkeep, revolve=rev, grid=(g['x0'], g['y0']))
    Tf, rpx = dilate_hf(T2, p, a_eff, A.draft, g['zback'])
    g.update(top0=top0, T2=T2, closed=closed, Tf=Tf)
    foot = Tf > g['zback']
    g['vol'] = float(np.clip(Tf - g['zback'], 0, None)[foot].sum() * p * p)
    g['height'] = float(Tf[foot].max() - g['zback'])
    return g


V = read_stl(A.mesh)
log('malla', len(V), 'triangulos; volumen pieza %.2f cm3' % (signed_volume(V) / 1e3))

# ---- orientacion
cands = ['+z', '-z', '+x', '-x', '+y', '-y']
scores = {}
if A.orient == 'auto':
    for c in cands:
        g = hf_blank(V @ ROT[c].T, 1.0)
        scores[c] = (g['vol'], g['height'])
        log('orientacion', c, 'bruto %.1f cm3, altura %.1f mm' % (g['vol'] / 1e3, g['height']))
    orient = min(scores, key=lambda c: scores[c][0])
else:
    orient = A.orient
log('orientacion elegida:', orient)
Vo = V @ ROT[orient].T

# ---- bruto fino
p = A.pitch
g = hf_blank(Vo, p)
zback = g['zback']
ztop = g['Tf'][g['Tf'] > zback].max()
B = terrain_mesh(g['Tf'], p, g['x0'], g['y0'], zback)
_ar = 0.5 * np.linalg.norm(np.cross(B[:, 1] - B[:, 0], B[:, 2] - B[:, 0]), axis=1)
B = B[_ar > 1e-9]
log('bruto: %d triangulos' % len(B))
bb0, bb1 = B.reshape(-1, 3).min(axis=0), B.reshape(-1, 3).max(axis=0)
volB = signed_volume(B)
areaB = mesh_area(B)
volP = signed_volume(Vo)

# recentrar: x,y al centro del bruto en el plano de particion, z = 0 en la cara plana
back = B[np.all(np.abs(B[:, :, 2] - zback) < 0.01, axis=1)]
cx = (back[:, :, 0].min() + back[:, :, 0].max()) / 2
cy = (back[:, :, 1].min() + back[:, :, 1].max()) / 2
off = np.array([cx, cy, zback])
Bc = B - off
Vc = Vo - off
S = 1.0 + A.shrink

# ---- comprobaciones
q = np.round(Bc.reshape(-1, 3), 6)
uq, inv = np.unique(q, axis=0, return_inverse=True)
faces_idx = inv.reshape(-1, 3)
e = np.sort(np.concatenate([faces_idx[:, [0, 1]], faces_idx[:, [1, 2]], faces_idx[:, [2, 0]]]), axis=1)
_, cnt = np.unique(e, axis=0, return_counts=True)
manifold = bool((cnt == 2).all())
chi = len(uq) - len(cnt) + len(faces_idx)
nrm = np.cross(Bc[:, 1] - Bc[:, 0], Bc[:, 2] - Bc[:, 0])
ar = 0.5 * np.linalg.norm(nrm, axis=1)
nn = nrm / np.maximum(2 * ar, 1e-12)[:, None]
flat_back = (nn[:, 2] < -0.99) & (np.abs(Bc[:, :, 2].mean(axis=1)) < 0.05)
nonflat = (np.abs(nn[:, 2]) < 0.99)
bad = nonflat & (nn[:, 2] < np.sin(np.radians(0.7 * A.draft)))
under = (nn[:, 2] < -0.02) & ~flat_back
draft_bad_area = float(ar[bad].sum() / ar.sum())
under_area = float(ar[under].sum() / ar.sum())
rng = np.random.default_rng(1)
n_s = 600000
tri_s = rng.choice(len(Bc), n_s, p=ar / ar.sum())
r1, r2 = rng.random(n_s), rng.random(n_s)
sw = r1 + r2 > 1
r1[sw], r2[sw] = 1 - r1[sw], 1 - r2[sw]
Ssamp = Bc[tri_s, 0] + r1[:, None] * (Bc[tri_s, 1] - Bc[tri_s, 0]) + r2[:, None] * (Bc[tri_s, 2] - Bc[tri_s, 0])
tree = cKDTree(Ssamp)
_dd, _ii = tree.query(Vc.reshape(-1, 3))
dmin = float(_dd.min())
_w = np.argsort(_dd)[:3]
log('vertices de la pieza con menos sobremetal:', [(np.round(Vc.reshape(-1, 3)[k], 1).tolist(), round(float(_dd[k]), 2)) for k in _w])
_P = Vo.reshape(-1, 3)
_ix = np.clip(np.floor((_P[:, 0] - g['x0']) / p).astype(int), 0, g['nx'] - 1)
_iy = np.clip(np.floor((_P[:, 1] - g['y0']) / p).astype(int), 0, g['ny'] - 1)
violaciones = int((_P[:, 2] > g['Tf'][_ix, _iy] + 1e-6).sum())
log('pieza contenida en el bruto:', violaciones == 0, '(vertices fuera: %d)' % violaciones)
log('malla cerrada:', manifold, '| Euler', chi, '| area con salida insuficiente %.3f %% | contrasalidas %.3f %% | sobremetal minimo comprobado %.2f mm' % (100 * draft_bad_area, 100 * under_area, dmin))

# ---- mazarota(s)
ps = 0.8
sub = max(1, int(round(ps / p)))
Tfs = g['Tf'][::sub, ::sub]
pcs = p * sub
H_all = ztop - zback
nzs = int(np.ceil(H_all / pcs)) + 3
zs = zback + (np.arange(nzs) + 0.5) * pcs
mask3 = (zs[None, None, :] <= Tfs[:, :, None]) & (zs[None, None, :] >= zback)
mask3 = np.pad(mask3, 1)
edt = ndi.distance_transform_edt(mask3, sampling=pcs)[1:-1, 1:-1, 1:-1]
rmax = float(edt.max())
hot = edt >= 0.85 * rmax
hot2 = hot.any(axis=2)
hi, hj = np.where(hot2)
foot_s = Tfs > zback
# geodesico sobre la huella
from skimage.graph import MCP_Geometric
cost = np.where(foot_s, 1.0, 1e6)


def geod(starts):
    m = MCP_Geometric(cost, fully_connected=True)
    c, _ = m.find_costs(starts)
    c = np.where(foot_s, c * pcs, np.inf)
    return c


cxh, cyh = hi.mean(), hj.mean()
k = np.argmin((hi - cxh) ** 2 + (hj - cyh) ** 2)
risers = [(int(hi[k]), int(hj[k]))]
Lf = 4.5 * (2 * rmax)
while len(risers) < (A.nrisers or 4):
    d = geod(risers)
    far = np.where(np.isfinite(d), d, 0).copy()
    if A.nrisers == 0 and far.max() <= Lf:
        break
    i, j = np.unravel_index(np.argmax(far), far.shape)
    # mover al punto mas grueso cercano (radio 8 mm)
    r = int(8 / pcs)
    i0, i1, j0, j1 = max(i - r, 0), min(i + r + 1, far.shape[0]), max(j - r, 0), min(j + r + 1, far.shape[1])
    th = (Tfs[i0:i1, j0:j1] - zback)
    ii, jj = np.unravel_index(np.argmax(np.where(foot_s[i0:i1, j0:j1], th, -1)), th.shape)
    risers.append((i0 + ii, j0 + jj))
dgeo = geod(risers)
dfar = float(np.where(np.isfinite(dgeo), dgeo, 0).max())
rxy = [(g['x0'] + (i + 0.5) * pcs - cx, g['y0'] + (j + 0.5) * pcs - cy) for i, j in risers]
log('radio inscrito maximo %.1f mm; distancia de alimentacion %.0f mm; mazarotas: %d; distancia geodesica maxima %.0f mm' % (rmax, Lf, len(risers), dfar))

# dimensionado
foot_f = g['Tf'] > zback
X = (g['x0'] + (np.arange(g['nx']) + 0.5) * p - cx)[:, None]
Y = (g['y0'] + (np.arange(g['ny']) + 0.5) * p - cy)[None, :]
Db = 40.0
for _ in range(4):
    contact = 0.0
    for (rx, ry) in rxy:
        contact += float(((((X - rx) ** 2 + (Y - ry) ** 2) <= (Db / 2) ** 2) & foot_f).sum() * p * p)
    Mc = volB / (areaB - contact)
    Mr_req = A.riserf * Mc
    Dm = Mr_req / 0.2143
    Hr = 1.5 * Dm
    Db = Dm + Hr * np.tan(np.radians(A.draft))
Dt = Dm - Hr * np.tan(np.radians(A.draft))
Db, Dt, Hr = float(np.ceil(Db)), float(np.ceil(Dt)), float(np.ceil(Hr))
R1, R2 = Db / 2, Dt / 2
s_ = np.hypot(Hr, R1 - R2)
Vr = np.pi / 3 * Hr * (R1 ** 2 + R1 * R2 + R2 ** 2)
Ar = np.pi * (R1 + R2) * s_ + np.pi * R2 ** 2
Mr = Vr / Ar
Mc0 = volB / areaB
nR = len(risers)
yield_ = volB / (volB + nR * Vr)
log('modulo pieza %.3f cm (%.3f descontando huellas); mazarota Ø%.0f->Ø%.0f x %.0f: modulo %.3f cm, relacion %.2f; rendimiento %.0f %%' % (Mc0 / 10, Mc / 10, Db, Dt, Hr, Mr / 10, Mr / Mc, 100 * yield_))

# ---- huecos rellenados / conservados
lab, nl = ndi.label(~(g['top0'] > -BIG / 2))
border = set(np.unique(np.concatenate([lab[0, :], lab[-1, :], lab[:, 0], lab[:, -1]])))
holes_f, holes_k = [], []
for l in range(1, nl + 1):
    if l in border:
        continue
    area_l = (lab == l).sum() * p * p
    dia = 2 * np.sqrt(area_l / np.pi)
    kept = bool(g['closed'][lab == l].mean() < 0.5)
    (holes_k if kept else holes_f).append(round(float(dia), 1))
log('huecos pasantes (proyeccion): rellenados', sorted(holes_f), '| conservados', sorted(holes_k))

# ---- islas de arena en el bruto (huecos conservados)
lab2, n2 = ndi.label(~foot_f)
brd2 = set(np.unique(np.concatenate([lab2[0, :], lab2[-1, :], lab2[:, 0], lab2[:, -1]])))
islas = []
for l in range(1, n2 + 1):
    if l in brd2:
        continue
    m_ = lab2 == l
    din = float(2 * ndi.distance_transform_edt(m_, sampling=p).max())
    ring = ndi.binary_dilation(m_, iterations=3) & ~m_ & foot_f
    hh = float((g['Tf'][ring] - zback).mean()) if ring.any() else 0.0
    islas.append(dict(d_min_mm=round(din, 1), h_mm=round(hh, 1), esbeltez=round(hh / din, 2) if din > 0 else None))
log('islas de arena (huecos conservados):', islas)

# ---- salidas
tag = A.tag
Bs = Bc * S
write_stl(os.path.join(A.outdir, '%s_patron_3grados_x%.3f.stl' % (tag, S)), Bs, 'patron fundicion')
write_stl(os.path.join(A.outdir, '%s_bruto_sin_contraccion.stl' % tag), Bc, 'bruto fundido esperado')
# forma de mazarota
N = 72
ang = np.linspace(0, 2 * np.pi, N, endpoint=False)
b_ = np.stack([R1 * np.cos(ang), R1 * np.sin(ang), np.zeros(N)], axis=1)
t_ = np.stack([R2 * np.cos(ang), R2 * np.sin(ang), np.full(N, Hr)], axis=1)
tr = []
for i in range(N):
    j = (i + 1) % N
    tr += [(b_[i], b_[j], t_[j]), (b_[i], t_[j], t_[i]), (np.array([0, 0, 0.0]), b_[j], b_[i]), (np.array([0, 0, Hr]), t_[i], t_[j])]
tr = np.array(tr)
if signed_volume(tr) < 0:
    tr = tr[:, ::-1, :]
write_stl(os.path.join(A.outdir, '%s_mazarota_forma.stl' % tag), tr, 'forma de mazarota')

# ---- figura de comprobacion
def slice_mesh(Vm, axis, val):
    d = Vm[:, :, axis] - val
    segs = []
    sel = (d.min(axis=1) < 0) & (d.max(axis=1) > 0)
    for tri_, dd in zip(Vm[sel], d[sel]):
        pts = []
        for a_, b2 in ((0, 1), (1, 2), (2, 0)):
            if dd[a_] * dd[b2] < 0:
                t = dd[a_] / (dd[a_] - dd[b2])
                pts.append(tri_[a_] + t * (tri_[b2] - tri_[a_]))
        if len(pts) == 2:
            segs.append(pts)
    return segs


fig, ax = plt.subplots(1, 3, figsize=(20, 7.2), dpi=85, gridspec_kw={'width_ratios': [1.2, 1.2, 1.2]})
a0 = ax[0]
Xm = X[:, 0]
Ym = Y[0, :]
has_p = (g['top0'] > -BIG / 2).T
a0.contour(Xm, Ym, foot_f.T.astype(float), levels=[0.5], colors='royalblue', linewidths=2)
a0.contour(Xm, Ym, has_p.astype(float), levels=[0.5], colors='crimson', linewidths=1.5)
th_ = np.linspace(0, 2 * np.pi, 200)
for n_, (rx, ry) in enumerate(rxy):
    a0.plot(rx + R1 * np.cos(th_), ry + R1 * np.sin(th_), color='darkorange', lw=2)
    a0.plot(rx + R2 * np.cos(th_), ry + R2 * np.sin(th_), color='darkorange', lw=1, ls='--')
    a0.plot([rx], [ry], '+', color='darkorange', ms=12)
    a0.text(rx, ry + R1 + 2, 'M%d' % (n_ + 1), color='darkorange', ha='center', fontsize=9)
a0.set_aspect('equal')
mxx = max(abs(bb0[0] - cx), abs(bb1[0] - cx)) + 8
mxy = max(abs(bb0[1] - cy), abs(bb1[1] - cy)) + 8
a0.set_xlim(-mxx - R1 * 0.2, mxx + R1 * 0.2)
a0.set_ylim(-mxy - R1 * 0.2, mxy + R1 * 0.2)
a0.invert_xaxis()   # vista desde la caja superior (hacia el plano de particion): espejo de la vista desde la cara lejana
a0.set_title('Planta vista desde la caja superior, sin contraccion\nazul: cara plana del bruto | rojo: pieza | naranja: mazarota (base y tope)', fontsize=9)
a0.grid(alpha=0.3)
a0.set_xlabel("x' (mm, crece hacia la izquierda en esta vista)")
a0.set_ylabel("y' (mm)")


def section(axx, plane_axis, val, title):
    # plane_axis 1: corte y = val (x horizontal); 0: corte x = val (y horizontal)
    if plane_axis == 1:
        prof = g['Tf'][:, int(round((val + cy - g['y0']) / p - 0.5))]
        hz = X[:, 0]
    else:
        prof = g['Tf'][int(round((val + cx - g['x0']) / p - 0.5)), :]
        hz = Y[0, :]
    th = np.where(prof > zback, prof - zback, np.nan)
    ok = ~np.isnan(th)
    # relleno por tramos continuos
    idx = np.where(ok)[0]
    if len(idx):
        runs = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
        for r_ in runs:
            xs_ = hz[r_]
            top_ = -th[r_]
            poly = [(xs_[0], 0)] + list(zip(xs_, top_)) + [(xs_[-1], 0)]
            axx.add_patch(Polygon(poly, closed=True, fc='royalblue', alpha=0.22, ec='royalblue', lw=1.5))
    segs = slice_mesh(Vc, 1 if plane_axis == 1 else 0, val)
    for s2 in segs:
        hh = [s2[0][0 if plane_axis == 1 else 1], s2[1][0 if plane_axis == 1 else 1]]
        zz = [-s2[0][2], -s2[1][2]]
        axx.plot(hh, zz, color='crimson', lw=1.2)
    axx.axhline(0, color='k', lw=1)
    for (rx, ry) in rxy:
        c0 = rx if plane_axis == 1 else ry
        d0 = abs((ry if plane_axis == 1 else rx) - val)
        if d0 < R1:
            f1 = np.sqrt(max(R1 ** 2 - d0 ** 2, 0))
            f2 = np.sqrt(max(R2 ** 2 - d0 ** 2, 0)) if d0 < R2 else 0
            axx.add_patch(Polygon([(c0 - f1, 0), (c0 + f1, 0), (c0 + f2, Hr), (c0 - f2, Hr)], closed=True, fc='darkorange', alpha=0.3, ec='darkorange', lw=1.5))
    axx.set_aspect('equal')
    axx.set_title(title, fontsize=9)
    axx.grid(alpha=0.3)
    axx.set_xlabel('mm')


rx0, ry0 = rxy[0]
section(ax[1], 1, ry0, 'Seccion X-Z (y = %.1f), orientacion del molde\ncaja superior arriba (mazarota) | caja inferior abajo' % ry0)
section(ax[2], 0, rx0, 'Seccion Y-Z (x = %.1f)' % rx0)
for axx in (ax[1], ax[2]):
    axx.set_ylim(-(H_all + 6), Hr + 8)
fig.subplots_adjust(left=0.04, right=0.99, top=0.88, bottom=0.08, wspace=0.12)
fig.suptitle('%s: pieza final (rojo) dentro del bruto fundido (azul) y mazarota (naranja)' % A.name, fontsize=11)
plt.savefig(os.path.join(A.outdir, '%s_comprobacion.png' % tag))
plt.close(fig)

# ---- vistas del bruto desde el campo de alturas
fig = plt.figure(figsize=(18, 11), dpi=80)
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
stc = max(2, int(round(1.2 / p)))
Tcoarse = g['Tf'][::stc, ::stc]
Mc_ = terrain_mesh(Tcoarse, stc * p, g['x0'] - p * (stc - 1) / 2 - cx, g['y0'] - p * (stc - 1) / 2 - cy, zback)
Mc_ = Mc_[Mc_[:, :, 2].max(axis=1) > zback + 1e-6]
Mc_ = Mc_[np.linalg.norm(np.cross(Mc_[:, 1] - Mc_[:, 0], Mc_[:, 2] - Mc_[:, 0]), axis=1) > 1e-9]
Mshow = Mc_.copy()
Mshow[:, :, 2] = Mshow[:, :, 2] - zback
nshow = np.cross(Mshow[:, 1] - Mshow[:, 0], Mshow[:, 2] - Mshow[:, 0])
nshow = nshow / np.maximum(np.linalg.norm(nshow, axis=1), 1e-12)[:, None]
topf = nshow[:, 2] > -0.5
Mshow, nshow = Mshow[topf], nshow[topf]
rr = max(bb1[0] - bb0[0], bb1[1] - bb0[1], bb1[2] - bb0[2]) / 2 * 1.05
for k_, (el, az, ttl) in enumerate([(35, -55, 'iso 1: bruto visto desde la cara lejana (la de abajo en el molde)'), (35, 125, 'iso 2')]):
    a3 = fig.add_subplot(2, 2, k_ + 1, projection='3d')
    el_r, az_r = np.radians(el), np.radians(az)
    vw = np.array([np.cos(el_r) * np.cos(az_r), np.cos(el_r) * np.sin(az_r), np.sin(el_r)])
    lg = vw * 0.8 + np.array([0.3, -0.3, 0.5])
    lg /= np.linalg.norm(lg)
    sh = np.clip(nshow @ lg, 0, 1) * 0.75 + 0.25
    colr = np.stack([sh * 0.62, sh * 0.70, sh * 0.82], axis=1)
    a3.add_collection3d(Poly3DCollection(Mshow, facecolors=colr, edgecolors=(0, 0, 0, 0.05), linewidths=0.1))
    cxm = (Mshow[:, :, 0].min() + Mshow[:, :, 0].max()) / 2
    cym = (Mshow[:, :, 1].min() + Mshow[:, :, 1].max()) / 2
    a3.set_xlim(cxm - rr, cxm + rr)
    a3.set_ylim(cym - rr, cym + rr)
    a3.set_zlim(0, 2 * rr)
    a3.set_box_aspect((1, 1, 1))
    a3.view_init(elev=el, azim=az)
    a3.set_title(ttl, fontsize=10)
    a3.set_xlabel('x', fontsize=8)
    a3.set_ylabel('y', fontsize=8)
    a3.set_zlabel('z (hacia la cara lejana)', fontsize=8)
a4 = fig.add_subplot(2, 2, 3)
ls = LightSource(azdeg=315, altdeg=40)
Zh = np.where(g['Tf'] > zback + 0.02, g['Tf'], np.nan)
shade = ls.hillshade(np.nan_to_num(Zh, nan=zback), vert_exag=3, dx=p, dy=p)
shade = np.where(np.isnan(Zh), 1.0, shade)
a4.imshow(shade.T, origin='lower', cmap='gray', extent=[X[0, 0] - p / 2, X[-1, 0] + p / 2, Y[0, 0] - p / 2, Y[0, -1] + p / 2], vmin=0, vmax=1)
a4.set_xlim(-mxx, mxx)
a4.set_ylim(-mxy, mxy)
a4.set_title('Relieve del bruto visto desde la cara lejana (sombreado)', fontsize=10)
a5 = fig.add_subplot(2, 2, 4)
th_map = np.where(foot_f, g['Tf'] - zback, np.nan)
imh = a5.imshow(th_map.T, origin='lower', cmap='viridis', extent=[X[0, 0] - p / 2, X[-1, 0] + p / 2, Y[0, 0] - p / 2, Y[0, -1] + p / 2])
a5.set_xlim(-mxx, mxx)
a5.set_ylim(-mxy, mxy)
plt.colorbar(imh, ax=a5, label='espesor del bruto (mm)', shrink=0.8)
for (rx, ry) in rxy:
    a5.plot(rx + R1 * np.cos(th_), ry + R1 * np.sin(th_), color='white', lw=1.5)
a5.set_title('Espesor del bruto y mazarotas (circulos blancos)', fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(A.outdir, '%s_vistas_patron.png' % tag))
plt.close(fig)

info = dict(tag=tag, name=A.name, orient=orient, scores={k: [round(v[0] / 1e3, 1), round(v[1], 1)] for k, v in scores.items()},
            pieza_dim=[round(float(x), 2) for x in (g['mx'] - g['mn'])], pieza_vol_cm3=round(volP / 1e3, 2),
            bruto_dim=[round(float(x), 2) for x in (bb1 - bb0)], bruto_vol_cm3=round(volB / 1e3, 2), bruto_masa_g_2_6=round(volB * 2.6e-3, 0), bruto_area_cm2=round(areaB / 100, 1),
            patron_dim=[round(float(x) * S, 2) for x in (bb1 - bb0)], triangulos=int(len(B)), cerrada=manifold, euler=int(chi),
            salida_insuficiente_pct=round(100 * draft_bad_area, 3), contrasalidas_pct=round(100 * under_area, 3), sobremetal_min_mm=round(dmin, 2),
            rmax_mm=round(rmax, 1), Lf_mm=round(Lf, 0), n_mazarotas=nR, mazarota_xy=[[round(float(a_), 1), round(float(b2), 1)] for a_, b2 in rxy],
            mazarota=dict(Db=Db, Dt=Dt, H=Hr, vol_cm3=round(Vr / 1e3, 1), masa_g=round(Vr * 2.6e-3, 0), modulo_cm=round(Mr / 10, 3), relacion=round(Mr / Mc, 2)),
            modulo_pieza_cm=round(Mc0 / 10, 3), modulo_pieza_desc_cm=round(Mc / 10, 3), rendimiento_pct=round(100 * yield_, 0),
            altura_bruto_mm=round(H_all, 1), caja_sup_mm=round(Hr + 25, 0), caja_inf_mm=round(H_all + 30, 0),
            huecos_rellenados_mm=sorted(holes_f), huecos_conservados_mm=sorted(holes_k), dist_geodesica_max_mm=round(dfar, 0), islas=islas,
            particion=dict(eje='XYZ'['xyz'.index(orient[1])], lado=('minimo' if orient[0] == '+' else 'maximo'),
                           coord_mm=round(float((V.reshape(-1, 3).min(axis=0) if orient[0] == '+' else V.reshape(-1, 3).max(axis=0))['xyz'.index(orient[1])]), 2)),
            pieza_bbox_original=[np.round(V.reshape(-1, 3).min(axis=0), 2).tolist(), np.round(V.reshape(-1, 3).max(axis=0), 2).tolist()],
            contenida=bool(violaciones == 0), masa_colada_g=round((volB + nR * Vr) * 2.6e-3, 0),
            revolucion=bool(A.revolve), parametros=dict(sobremetal=A.a, sobremetal_particion=A.acope, salida=A.draft, radio_interior=A.rin, hueco_minimo_conservado=A.dkeep, contraccion=A.shrink, paso_malla=A.pitch))
json.dump(info, open(os.path.join(A.outdir, '%s_datos.json' % tag), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(info, ensure_ascii=False, indent=1))
log('listo')
