"""Soccer ball diameter from camera b (table-corner calibration, independent of any stated depth).
silhouette ~95 x 97 px centred (600.5, 318) in bx frame 20."""
import sys, numpy as np, cv2
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0034/scripts')
from calib_b import fit, backproject
import geom
def bisect(g, a, b):
    for _ in range(60):
        m = (a + b) / 2
        if g(a) * g(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
for f in (680, 692, 705, 711):
    cam = fit(f=f)
    def ext(Rcm):
        P, Cw = backproject(cam, [[600.5, 318]], Rcm)
        Pc = cam['R'] @ P[0] + cam['t']          # camera coords (cm)
        geom.CX, geom.CY = 640.0, 360.0
        w, h, m = geom.extents(Pc / 100, Rcm / 100, f)
        return w, h
    Rw = bisect(lambda r: ext(r)[0] - 95, 3, 20); Rh = bisect(lambda r: ext(r)[1] - 97, 3, 20)
    # tennis ball check at rest (b-left ball 32 px wide x ~30 high at (467,289)): predicted width for R=3.35
    print(f'f={f}: soccer D from width {2*Rw:.1f} cm, from height {2*Rh:.1f} cm')
