import sys, json, struct, argparse
import numpy as np

# patron de fundicion para el "Soporte superior de engranes" (prisma 65 x 17 x 27 con esquinas R5)
# la extraccion se hace en Z; la cara plana inferior es el plano de particion (queda arriba en el molde)
ap = argparse.ArgumentParser()
ap.add_argument('--out', required=True)            # prefijo de salida
ap.add_argument('--L', type=float, default=65.0)   # largo (X)
ap.add_argument('--T', type=float, default=17.0)   # espesor (Y)
ap.add_argument('--Hf', type=float, default=27.0)  # alto de la pieza final (Z)
ap.add_argument('--rc', type=float, default=5.0)   # radio de las esquinas verticales
ap.add_argument('--a', type=float, default=3.0)    # sobremetal minimo (laterales y cara lejana)
ap.add_argument('--acope', type=float, default=4.5)  # sobremetal en la cara de particion (queda arriba)
ap.add_argument('--draft', type=float, default=3.0)  # salida en grados
ap.add_argument('--rf', type=float, default=3.0)   # radio en el borde de la cara lejana
ap.add_argument('--shrink', type=float, default=0.013)
ap.add_argument('--n', type=int, default=16)       # puntos por cuarto de arco
A = ap.parse_args()

t = np.tan(np.radians(A.draft))
H = A.acope + A.Hf + A.a          # altura total del bruto (desde el plano de particion)
R = A.rf
sq = np.sqrt(1 + t * t)
Cu = A.a - R * (sq - t)           # centro del empalme (offset), medido desde el contorno final
Cv = H - R


def ring(u, v):
    hx, hy, rc = A.L / 2 + u, A.T / 2 + u, A.rc + u
    pts = []
    cs = [(hx - rc, hy - rc, 0), (-(hx - rc), hy - rc, 90), (-(hx - rc), -(hy - rc), 180), (hx - rc, -(hy - rc), 270)]
    for cx, cy, a0 in cs:
        for k in range(A.n):
            ang = np.radians(a0 + 90.0 * k / A.n)
            pts.append((cx + rc * np.cos(ang), cy + rc * np.sin(ang), v))
    return np.array(pts)


prof = [(A.a + H * t, 0.0)]
a0 = np.arctan(t)
prof.append((Cu + R / sq, Cv + R * t / sq))
for al in np.linspace(a0, np.pi / 2, 11)[1:]:
    prof.append((Cu + R * np.cos(al), Cv + R * np.sin(al)))
rings = [ring(u, v) for u, v in prof]
m = len(rings[0])

tris = []
# paredes
for k in range(len(rings) - 1):
    r0, r1 = rings[k], rings[k + 1]
    for i in range(m):
        j = (i + 1) % m
        tris.append((r0[i], r0[j], r1[j]))
        tris.append((r0[i], r1[j], r1[i]))
# tapas (abanico desde el centro)
c0 = np.array([0, 0, 0.0])
c1 = np.array([0, 0, H])
for i in range(m):
    j = (i + 1) % m
    tris.append((c0, rings[0][j], rings[0][i]))      # fondo, normal hacia -Z
    tris.append((c1, rings[-1][i], rings[-1][j]))    # tapa, normal hacia +Z
V = np.array(tris)


def vol(V):
    return np.einsum('ij,ij->i', V[:, 0], np.cross(V[:, 1], V[:, 2])).sum() / 6.0


if vol(V) < 0:
    V = V[:, ::-1, :]
assert vol(V) > 0


def write_stl(path, V, name='patron'):
    n = len(V)
    cr = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0])
    nn = cr / np.maximum(np.linalg.norm(cr, axis=1), 1e-12)[:, None]
    buf = bytearray(name.encode()[:80].ljust(80, b' '))
    buf += struct.pack('<I', n)
    rec = np.zeros(n, dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))
    rec['n'] = nn
    rec['v'] = V
    buf += rec.tobytes()
    open(path, 'wb').write(bytes(buf))


s = 1.0 + A.shrink
Vp = V * s
write_stl(A.out + '_patron_x%.3f.stl' % s, Vp, 'patron fundicion')
write_stl(A.out + '_bruto_sin_contraccion.stl', V, 'bruto fundido esperado')
info = {
    'H_bruto_mm': H, 'contorno_en_plano_de_particion_mm': [A.L + 2 * (A.a + H * t), A.T + 2 * (A.a + H * t)],
    'radio_esquina_en_particion_mm': A.rc + A.a + H * t,
    'volumen_bruto_mm3': vol(V), 'volumen_patron_mm3': vol(Vp),
    'masa_bruto_g_2.6': vol(V) * 2.6e-3, 'masa_bruto_g_2.68': vol(V) * 2.68e-3,
    'triangulos': int(len(V)), 'bbox_patron': [Vp.reshape(-1, 3).min(axis=0).round(3).tolist(), Vp.reshape(-1, 3).max(axis=0).round(3).tolist()],
    'altura_final_dentro_bruto_mm': [A.acope, A.acope + A.Hf],
}
print(json.dumps(info, indent=1))
# datos para dibujar
nrm = np.cross(Vp[:, 1] - Vp[:, 0], Vp[:, 2] - Vp[:, 0])
nrm = nrm / np.maximum(np.linalg.norm(nrm, axis=1), 1e-12)[:, None]
np.savez(A.out + '_patron.npz', V=Vp, nrm=nrm, th=np.full(len(Vp), np.nan), prof=np.array(prof))
