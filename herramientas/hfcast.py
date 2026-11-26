import sys, os, json, struct, argparse, time
import numpy as np
from scipy import ndimage as ndi

# Patron de fundicion en arena (plano de particion plano, un solo sentido de extraccion) a partir de una malla.
# Modelo "campo de alturas": el bruto es {z_atras <= z <= T(x,y)}; T se obtiene del mapa de alturas de la pieza
# (z-buffer), rellenando huecos pequenos y dilatando con el elemento estructurante
#   h(r) = sqrt(a^2 - r^2) si r <= a;  h(r) = -(r - a)/tan(salida) si r > a
# (sobremetal a en todas las caras, salida exacta, borde convexo redondeado con R = a).
BIG = 1.0e4

ROT = {
    '+z': np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], float),
    '-z': np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]], float),
    '+x': np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], float),
    '-x': np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]], float),
    '+y': np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], float),
    '-y': np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float),
}


def read_stl(p):
    d = open(p, 'rb').read()
    n = struct.unpack('<I', d[80:84])[0]
    dt = np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
    return np.frombuffer(d, dtype=dt, count=n, offset=84)['v'].astype(float)


def write_stl(p, V, name='hfcast'):
    V = np.asarray(V, float)
    cr = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0])
    nn = cr / np.maximum(np.linalg.norm(cr, axis=1), 1e-12)[:, None]
    dt = np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
    rec = np.zeros(len(V), dtype=dt)
    rec['n'] = nn
    rec['v'] = V
    open(p, 'wb').write(bytes(bytearray(name.encode()[:80].ljust(80, b' '))) + struct.pack('<I', len(V)) + rec.tobytes())


def signed_volume(V):
    return np.einsum('ij,ij->i', V[:, 0], np.cross(V[:, 1], V[:, 2])).sum() / 6.0


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return (x * x + y * y) <= r * r


def zbuffer(V, p, x0, y0, nx, ny):
    """mapa de alturas maximas por columna (centros de celda), -BIG donde no hay pieza"""
    top = np.full((nx, ny), -BIG)
    x, y, z = V[:, :, 0], V[:, :, 1], V[:, :, 2]
    ax, ay = x[:, 1] - x[:, 0], y[:, 1] - y[:, 0]
    bx, by = x[:, 2] - x[:, 0], y[:, 2] - y[:, 0]
    det = ax * by - ay * bx
    ok = np.abs(det) > 1e-12
    idx = np.where(ok)[0]
    i0 = np.ceil((x[idx].min(axis=1) - x0) / p - 0.5).astype(int)
    i1 = np.floor((x[idx].max(axis=1) - x0) / p - 0.5).astype(int)
    j0 = np.ceil((y[idx].min(axis=1) - y0) / p - 0.5).astype(int)
    j1 = np.floor((y[idx].max(axis=1) - y0) / p - 0.5).astype(int)
    w = np.maximum(i1 - i0 + 1, 0)
    h = np.maximum(j1 - j0 + 1, 0)
    cnt = w * h
    keep = cnt > 0
    idx, i0, j0, w, h, cnt = idx[keep], i0[keep], j0[keep], w[keep], h[keep], cnt[keep]
    # procesar por bloques para limitar memoria
    start = 0
    n = len(idx)
    cum = np.cumsum(cnt)
    LIM = 6_000_000
    while start < n:
        base = cum[start - 1] if start > 0 else 0
        end = np.searchsorted(cum, base + LIM, side='right')
        end = max(end, start + 1)
        sl = slice(start, end)
        c = cnt[sl]
        tri = np.repeat(idx[sl], c)
        loc = np.arange(c.sum()) - np.repeat(np.cumsum(c) - c, c)
        ww = np.repeat(w[sl], c)
        ii = np.repeat(i0[sl], c) + loc % ww
        jj = np.repeat(j0[sl], c) + loc // ww
        cx = x0 + (ii + 0.5) * p
        cy = y0 + (jj + 0.5) * p
        xt0, yt0, zt0 = x[tri, 0], y[tri, 0], z[tri, 0]
        d = det[tri]
        u = ((cx - xt0) * by[tri] - (cy - yt0) * bx[tri]) / d
        v = (ax[tri] * (cy - yt0) - ay[tri] * (cx - xt0)) / d
        eps = 1e-9
        ins = (u >= -eps) & (v >= -eps) & (u + v <= 1 + eps)
        zz = zt0 + u * (z[tri, 1] - zt0) + v * (z[tri, 2] - zt0)
        m = ins & (ii >= 0) & (ii < nx) & (jj >= 0) & (jj < ny)
        np.maximum.at(top, (ii[m], jj[m]), zz[m])
        start = end
    return top


def ball(R, p):
    r = int(np.ceil(R / p))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    rr = np.hypot(xx, yy) * p
    s = np.where(rr <= R, np.sqrt(np.maximum(R * R - rr * rr, 0)), -BIG)
    return s


def pad_for(top, rpx):
    return np.pad(top, rpx, mode='constant', constant_values=-BIG)


def build_topmap(top0, p, a, draft_deg, rin, dkeep, hmax_hint=None, revolve=None, grid=None):
    """de la altura de la pieza (top0) al mapa de alturas del bruto (sin plano de atras).
    devuelve top3 (con extension del cono hacia afuera), top2 (rellena, antes de dilatar), mask de huella de pieza rellena"""
    T = top0
    has = T > -BIG / 2
    pad = 0
    # 1) cierre binario de huecos/entallas menores que dkeep
    R = int(round(dkeep / 2 / p))
    closed = ndi.binary_closing(has, structure=disk(R), border_value=0)
    closed |= has
    # asignar alturas a las columnas rellenas: la altura de la columna con pieza mas cercana
    idxs = ndi.distance_transform_edt(~has, return_indices=True)[1]
    T1 = np.where(closed, T[idxs[0], idxs[1]], -BIG)
    if revolve is not None:
        # engranes: el bruto es la envolvente de revolucion (cono / cilindro de las puntas), sin dientes
        x0g, y0g = grid
        cxr, cyr = revolve
        nx_, ny_ = T.shape
        xs_ = x0g + (np.arange(nx_) + 0.5) * p
        ys_ = y0g + (np.arange(ny_) + 0.5) * p
        Rr = np.hypot(xs_[:, None] - cxr, ys_[None, :] - cyr)
        ri = np.floor(Rr / p).astype(int)
        env = np.full(ri.max() + 1, -BIG)
        np.maximum.at(env, ri[has], T[has])
        valid = env > -BIG / 2
        envf = np.interp(np.arange(len(env)), np.where(valid)[0], env[valid])
        # huella circular hasta el radio exterior de la pieza (se conservan los huecos grandes cerrados)
        r_out = Rr[has].max()
        labc, nc = ndi.label(~closed)
        brd = np.unique(np.concatenate([labc[0, :], labc[-1, :], labc[:, 0], labc[:, -1]]))
        enclosed = (labc > 0) & ~np.isin(labc, brd)
        closed = closed | ((Rr <= r_out) & ~enclosed)
        T2 = np.where(closed, envf[ri], -BIG)
    else:
        # 2) cierre en altura con disco plano (depresiones mas estrechas que dkeep)
        T2 = ndi.grey_closing(T1, footprint=disk(R), mode='constant', cval=-BIG)
        T2 = np.where(closed, np.maximum(T2, T1), -BIG)
    # 3) cierre con bola (rincones concavos con radio rin + a antes de dilatar)
    if rin > 0:
        bb = ball(rin + a, p)
        T2b = ndi.grey_closing(T2, structure=bb, footprint=disk(int(np.ceil((rin + a) / p))), mode='constant', cval=-BIG)
        T2 = np.where(closed, np.maximum(T2b, T2), -BIG)
    return T2, closed, pad


def dilate_hf(T2, p, a, draft_deg, zback):
    t = np.tan(np.radians(draft_deg))
    ztop = T2[T2 > -BIG / 2].max()
    hmax = ztop + a - zback
    rwin = a + hmax * t
    rext = rwin + 2.0 + 3 * p
    rpx = int(np.ceil(rext / p))
    yy, xx = np.mgrid[-rpx:rpx + 1, -rpx:rpx + 1]
    rr = np.hypot(xx, yy) * p
    th = np.radians(draft_deg)
    rs = a * np.cos(th)
    # semiesfera hasta el punto de tangencia con el cono de salida, despues el cono tangente
    s = np.where(rr <= rs, np.sqrt(np.maximum(a * a - np.minimum(rr, rs) ** 2, 0)), a * np.sin(th) - (rr - rs) / t)
    s = np.where(rr <= rext, s, -BIG)
    fp = rr <= rext
    out = ndi.grey_dilation(T2, footprint=fp, structure=s, mode='constant', cval=-BIG)
    return out, rpx


def march(Tf, p, x0, y0, zback, ztop):
    """malla cerrada del bruto: f = max(z - T(x,y), zback - z) = 0"""
    from skimage import measure
    nx, ny = Tf.shape
    z0 = zback - 2.5 * p
    nz = int(np.ceil((ztop + 2 * p - z0) / p)) + 1
    zs = z0 + np.arange(nz) * p
    Tc = np.clip(Tf, -500, None)
    f = np.empty((nx, ny, nz), dtype=np.float32)
    for k in range(nz):
        f[:, :, k] = np.maximum(zs[k] - Tc, zback - zs[k])
    # nodos en el centro de las celdas: x = x0 + (i+0.5)p
    f[0, :, :] = np.abs(f[0, :, :]) + 1
    f[-1, :, :] = np.abs(f[-1, :, :]) + 1
    f[:, 0, :] = np.abs(f[:, 0, :]) + 1
    f[:, -1, :] = np.abs(f[:, -1, :]) + 1
    verts, faces, _, _ = measure.marching_cubes(f, level=1e-3, spacing=(p, p, p))
    verts = verts + np.array([x0 + 0.5 * p, y0 + 0.5 * p, z0])
    V = verts[faces]
    if signed_volume(V) < 0:
        faces = faces[:, ::-1]
        V = V[:, ::-1, :]
    march.last = (verts, faces)
    return V


def clip_tris(T, zb):
    """recorta triangulos (n,3,3) conservando la parte con z > zb; los vertices nuevos quedan en z = zb"""
    u = T[:, :, 2] - zb
    above = u > 0
    n_above = above.sum(axis=1)
    out = [T[n_above == 3]]
    sel = n_above == 1
    if sel.any():
        Ts, us, ab = T[sel], u[sel], above[sel]
        k = np.argmax(ab, axis=1)
        idx = np.arange(len(Ts))
        a, ua = Ts[idx, k], us[idx, k]
        b, ub = Ts[idx, (k + 1) % 3], us[idx, (k + 1) % 3]
        c, uc = Ts[idx, (k + 2) % 3], us[idx, (k + 2) % 3]
        tb, tc = ua / (ua - ub), ua / (ua - uc)
        pb, pc = a + tb[:, None] * (b - a), a + tc[:, None] * (c - a)
        pb[:, 2] = zb
        pc[:, 2] = zb
        out.append(np.stack([a, pb, pc], axis=1))
    sel = n_above == 2
    if sel.any():
        Ts, us, ab = T[sel], u[sel], above[sel]
        k = np.argmin(ab, axis=1)
        idx = np.arange(len(Ts))
        b, ub = Ts[idx, k], us[idx, k]
        a1, u1 = Ts[idx, (k + 1) % 3], us[idx, (k + 1) % 3]
        a2, u2 = Ts[idx, (k + 2) % 3], us[idx, (k + 2) % 3]
        t1, t2 = u1 / (u1 - ub), u2 / (u2 - ub)
        p1, p2 = a1 + t1[:, None] * (b - a1), a2 + t2[:, None] * (b - a2)
        p1[:, 2] = zb
        p2[:, 2] = zb
        out.append(np.stack([p1, a1, a2], axis=1))
        out.append(np.stack([p1, a2, p2], axis=1))
    return np.concatenate(out)


def terrain_mesh(Tf, p, x0, y0, zback):
    """malla cerrada del bruto: superficie de alturas Tf(x,y) recortada en z = zback + tapa plana inferior"""
    nx, ny = Tf.shape
    xs = x0 + (np.arange(nx) + 0.5) * p
    ys = y0 + (np.arange(ny) + 0.5) * p
    # evitar vertices a menos de 2 micras del plano de recorte (triangulos degenerados)
    Tf = np.where(np.abs(Tf - zback) < 2e-3, zback - 2e-3, Tf)
    U = Tf - zback
    mxc = np.maximum.reduce([U[:-1, :-1], U[1:, :-1], U[1:, 1:], U[:-1, 1:]])
    ii, jj = np.where(mxc > 0)

    def P(i, j):
        return np.stack([xs[i], ys[j], Tf[i, j]], axis=-1)

    T1 = np.stack([P(ii, jj), P(ii + 1, jj), P(ii + 1, jj + 1)], axis=1)
    T2 = np.stack([P(ii, jj), P(ii + 1, jj + 1), P(ii, jj + 1)], axis=1)
    T = np.clip(np.concatenate([T1, T2]), -1e5, None)
    top = clip_tris(T, zback)
    cap = top[:, ::-1, :].copy()
    cap[:, :, 2] = zback
    return np.concatenate([top, cap])


def mesh_area(V):
    return 0.5 * np.linalg.norm(np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0]), axis=1).sum()
