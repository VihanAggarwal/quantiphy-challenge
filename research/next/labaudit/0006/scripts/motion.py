"""Label-style motion checks: displacement 1.0->1.2 s from the stated ranges at the toy centre pixels;
forward-difference speeds on a 3D track whose Z is linear between the label range (f24) and the table landing (f32)."""
import numpy as np
f, cx, cy = 711.0, 640.0, 360.0
cen = {24: (609.0, 145.9), 25: (602.7, 141.3), 26: (598.6, 146.9), 27: (596.1, 161.4), 28: (591.5, 191.6),
       29: (591.3, 224.9), 30: (571.4, 278.6), 31: (566.6, 382.3), 32: (546.9, 463.6)}
def P(u, v, R): r = np.array([u - cx, v - cy, f]); return R * r / np.linalg.norm(r)
def interp(fr):
    a = int(np.floor(fr)); w = fr - a
    if w == 0: return cen[a]
    return tuple((1 - w) * np.array(cen[a]) + w * np.array(cen[a + 1]))
for lab, (fa, fb) in {'24 fps (f24, f28.8)': (24, 28.8), '25 fps indexing (f25, f30)': (25, 30), 'f24,f29': (24, 29)}.items():
    d = np.linalg.norm(P(*interp(fa), 1.402) - P(*interp(fb), 1.065))
    print('displacement %-28s %.1f cm' % (lab, 100 * d))
# 3D track, Z linear from 1.341 (f24) to 0.889 (f32, table contact)
def X(fr):
    u, v = interp(fr); Z = 1.341 + (0.889 - 1.341) * (fr - 24) / 8
    return np.array([(u - cx) * Z / f, (v - cy) * Z / f, Z])
for fps in (24, 25):
    for a in (28, 28.8, 29, 30, 31):
        print('fps %d fd speed %.1f->%.1f: %.2f m/s' % (fps, a, a + 1, np.linalg.norm(X(a + 1) - X(a)) * fps))
# physics: apex ~ f25 (t=1.04), impact between f31 and f32
for tap, timp, vz in ((1.04, 1.30, 1.37), (1.04, 1.333, 1.37), (1.02, 1.333, 1.5)):
    vv = 9.8 * (timp - tap); print('impact: apex %.2f impact %.3f -> vert %.2f, |v| %.2f m/s (vz %.2f)' % (tap, timp, vv, np.hypot(vv, vz), vz))
    v12 = 9.8 * (1.2 - tap); print('   v(1.2) inst: vert %.2f |v| %.2f ; fd(+1/24): %.2f' % (v12, np.hypot(v12, vz), np.hypot(9.8 * (1.2 + 1 / 48 - tap), vz)))
