import sys, struct, json
import numpy as np

# dimensionado de la mazarota por modulo y forma (tronco de cono) para imprimir
BRUTO = sys.argv[1]       # STL del bruto sin contraccion
OUT = sys.argv[2]         # prefijo de salida
Db, Dt, H = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])

data = open(BRUTO, 'rb').read()
n = struct.unpack('<I', data[80:84])[0]
dt = np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
V = np.frombuffer(data, dtype=dt, count=n, offset=84)['v'].astype(float)
cr = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0])
area = 0.5 * np.linalg.norm(cr, axis=1)
vol = np.einsum('ij,ij->i', V[:, 0], np.cross(V[:, 1], V[:, 2])).sum() / 6.0
A = area.sum()
Mc = vol / A
print('pieza: V = %.1f cm3, A = %.1f cm2, modulo = %.3f cm' % (vol / 1e3, A / 1e2, Mc / 10))

# huella de la mazarota sobre la cara de particion (z = 0): interseccion circulo / contorno de la cara plana
bot = V[np.all(np.abs(V[:, :, 2]) < 1e-6, axis=1)]
xs = bot[:, :, 0].ravel()
ys = bot[:, :, 1].ravel()
hx, hy = np.abs(xs).max(), np.abs(ys).max()
# rectangulo con esquinas redondeadas: radio estimado = hx - (x donde empieza el arco); se usa el rectangulo completo menos las esquinas
step = 0.1
gx, gy = np.meshgrid(np.arange(-hx, hx, step) + step / 2, np.arange(-hy, hy, step) + step / 2)
# radio de esquina tomado del patron: 9.8 para 3 grados (se pasa por argumento opcional)
rc = float(sys.argv[6]) if len(sys.argv) > 6 else 9.8
cx, cy = hx - rc, hy - rc
dx = np.maximum(np.abs(gx) - cx, 0)
dy = np.maximum(np.abs(gy) - cy, 0)
inside_plate = (dx ** 2 + dy ** 2) <= rc ** 2
inside_riser = gx ** 2 + gy ** 2 <= (Db / 2) ** 2
contact = (inside_plate & inside_riser).sum() * step * step
plate_area = inside_plate.sum() * step * step
print('cara de particion: %.1f cm2; huella de la mazarota: %.1f cm2' % (plate_area / 1e2, contact / 1e2))
Mc2 = vol / (A - contact)
print('modulo de la pieza descontando la huella: %.3f cm' % (Mc2 / 10))

# mazarota: tronco de cono, enfriamiento por la pared lateral y la tapa
R1, R2 = Db / 2, Dt / 2
s = np.hypot(H, R1 - R2)
Vr = np.pi / 3 * H * (R1 ** 2 + R1 * R2 + R2 ** 2)
Ar = np.pi * (R1 + R2) * s + np.pi * R2 ** 2
Mr = Vr / Ar
print('mazarota D %.0f -> %.0f x %.0f mm: V = %.1f cm3, modulo = %.3f cm' % (Db, Dt, H, Vr / 1e3, Mr / 10))
print('relacion de modulos: %.2f (sin descontar huella) / %.2f (descontando)' % (Mr / Mc, Mr / Mc2))
print('rendimiento pieza / (pieza + mazarota): %.0f %%' % (100 * vol / (vol + Vr)))
print('masa de la mazarota (2,6 g/cm3): %.0f g; pieza en bruto: %.0f g' % (Vr * 2.6e-3, vol * 2.6e-3))
print('alto de caja superior recomendado >= %.0f mm' % (H + 25))

# STL de la forma de la mazarota (base ancha apoyada en z = 0)
N = 72
tris = []
ang = np.linspace(0, 2 * np.pi, N, endpoint=False)
b = np.stack([R1 * np.cos(ang), R1 * np.sin(ang), np.zeros(N)], axis=1)
t = np.stack([R2 * np.cos(ang), R2 * np.sin(ang), np.full(N, H)], axis=1)
for i in range(N):
    j = (i + 1) % N
    tris.append((b[i], b[j], t[j]))
    tris.append((b[i], t[j], t[i]))
    tris.append((np.array([0, 0, 0.0]), b[j], b[i]))
    tris.append((np.array([0, 0, H]), t[i], t[j]))
T = np.array(tris)
if np.einsum('ij,ij->i', T[:, 0], np.cross(T[:, 1], T[:, 2])).sum() < 0:
    T = T[:, ::-1, :]
cr = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
nn = cr / np.maximum(np.linalg.norm(cr, axis=1), 1e-12)[:, None]
rec = np.zeros(len(T), dtype=dt)
rec['n'] = nn
rec['v'] = T
open(OUT + '_mazarota_forma.stl', 'wb').write(bytes(bytearray(b'forma de mazarota'.ljust(80, b' '))) + struct.pack('<I', len(T)) + rec.tobytes())
json.dump({'Mc_cm': Mc / 10, 'Mc_descontando_cm': Mc2 / 10, 'Mr_cm': Mr / 10, 'Vr_cm3': Vr / 1e3, 'Vc_cm3': vol / 1e3, 'huella_cm2': contact / 1e2},
          open(OUT + '_mazarota.json', 'w'))
print('guardado', OUT + '_mazarota_forma.stl')
