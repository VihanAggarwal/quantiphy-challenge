import sys, os, numpy as np, json
sys.path.insert(0, os.path.dirname(__file__))
from geom import *
from motion import TRK, cap, uv, HB
def rest(tag, ks): return np.mean([uv(tag, k) for k in ks], axis=0)
for tag in 'osx':
    s0 = rest(tag, range(0, 18)); e0 = rest(tag, range(37, 49))
    S = on_slope(*s0, HB); E = on_plane(*e0, HB)
    # model track: slope plane up to v29, table plane from v32; v30/v31 are skipped (rotating over the foot)
    pts = [S] + [on_slope(*uv(tag, k), HB) for k in range(19, 30)] + [on_plane(*uv(tag, k), HB) for k in range(32, 37)] + [E]
    pl = sum(np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)) * 100
    # foot point: intersection of the slope bottom edge line with the path -> use slope coords at along=0 between v29 and v32
    a29 = slope_coords(on_slope(*uv(tag, 29), HB)); foot_s = BR + e * a29[0] / 100 + ns * HB  # point at the foot (top-surface height)
    leg1 = np.linalg.norm(S - on_slope(*uv(tag, 29), HB)) * 100
    print('%s start px (%.1f,%.1f) range %.3f | end px (%.1f,%.1f) range %.3f | straight %.1f | track polyline %.1f | slope leg S->v29 %.1f, v29->v32 %.1f, v32->E %.1f' % (
        tag, *s0, np.linalg.norm(S), *e0, np.linalg.norm(E), np.linalg.norm(E - S) * 100, pl, leg1,
        np.linalg.norm(on_slope(*uv(tag, 29), HB) - on_plane(*uv(tag, 32), HB)) * 100, np.linalg.norm(on_plane(*uv(tag, 32), HB) - E) * 100))
