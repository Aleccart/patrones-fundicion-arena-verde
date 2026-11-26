import sys, os, json, struct
import numpy as np
import cadquery as cq

# STEP -> un STL por solido (teselado fino) + resumen JSON
src, outdir = sys.argv[1], sys.argv[2]
tol = float(sys.argv[3]) if len(sys.argv) > 3 else 0.02
ang = float(sys.argv[4]) if len(sys.argv) > 4 else 0.2
os.makedirs(outdir, exist_ok=True)
base = os.path.splitext(os.path.basename(src))[0]
wp = cq.importers.importStep(src)
solids = wp.solids().vals()
print('solidos', len(solids))
dt = np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
info = []
for i, s in enumerate(solids):
    verts, tris = s.tessellate(tol, ang)
    P = np.array([(v.x, v.y, v.z) for v in verts], dtype=float)
    T = np.array(tris, dtype=int)
    V = P[T]
    cr = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0])
    vol = np.einsum('ij,ij->i', V[:, 0], np.cross(V[:, 1], V[:, 2])).sum() / 6.0
    if vol < 0:
        V = V[:, ::-1, :]
        cr = -cr
        vol = -vol
    nn = cr / np.maximum(np.linalg.norm(cr, axis=1), 1e-12)[:, None]
    rec = np.zeros(len(V), dtype=dt)
    rec['n'] = nn
    rec['v'] = V
    name = '%s_%d.stl' % (base, i)
    path = os.path.join(outdir, name)
    open(path, 'wb').write(bytes(bytearray(b'step2stl'.ljust(80, b' '))) + struct.pack('<I', len(V)) + rec.tobytes())
    bb = s.BoundingBox()
    d = {'archivo': name, 'triangulos': int(len(V)), 'volumen_mm3': float(s.Volume()), 'volumen_malla_mm3': float(vol),
         'caras': len(s.Faces()), 'bbox_min': [round(bb.xmin, 3), round(bb.ymin, 3), round(bb.zmin, 3)],
         'bbox_max': [round(bb.xmax, 3), round(bb.ymax, 3), round(bb.zmax, 3)],
         'dim': [round(bb.xlen, 3), round(bb.ylen, 3), round(bb.zlen, 3)]}
    info.append(d)
    print(json.dumps(d, ensure_ascii=False))
json.dump(info, open(os.path.join(outdir, base + '.json'), 'w'), ensure_ascii=False, indent=1)
