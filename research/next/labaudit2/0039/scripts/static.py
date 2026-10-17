"""Static rows, two routes each.  Pixel features read from intensity profiles of the x-render median (frames 0-9):
 bottle: top silhouette (front rim) y 329.5 at x 664; base front y 477.0 (x 650); width x 642.0-687.5 at row 400
 cup: rim edges x 724.0-794.5 at row 381; top y 375 and bottom y 497.5 at x 759
 poker tower: apex (686, 417); front card foot (701, 500.5); left card foot (662, 494.5)
 object centre clicks: bottle (664.5, 403.5), cup (759.5, 436)
Route A = stated ranges along the clicked rays (label-style); Route B = table plane (VP, h 0.1724 +- 2 %)."""
import numpy as np, json
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0039'
F, CX, CY = 711.0, 640.0, 360.0
pl = json.load(open(f'{OUT}/plane.json')); n = np.array(pl['n_vp']); H0 = pl['h_vp']
def ray(p): r = np.array([(p[0] - CX) / F, (p[1] - CY) / F, 1.0]); return r / np.linalg.norm(r)
def onp(p, H): r = ray(p); return H / (n @ r) * r
def vert_height(base_px, top_px, H):
    """point on the plane at base_px; height of the point on the plane normal through it that projects to top_px's row
    (closest approach of the top ray to the normal line)."""
    B = onp(base_px, H); r = ray(top_px); up = -n
    # solve B + s*up ~ t*r (least squares)
    A = np.c_[up, -r]; s, t = np.linalg.lstsq(A, -B, rcond=None)[0]
    return s
RB, RC, RP = 0.9998, 0.8740, 0.9035
out = {}
# bottle height
bt, bb = (664, 329.5), (650, 477.0)
A1 = np.linalg.norm(RB * ray(bt) - RB * ray((664, 477.0))) * 100
Bh = [vert_height(bb, bt, H0 * f) * 100 for f in (0.98, 1, 1.02)]
print(f'bottle height: A (both clicks at 0.9998) {A1:.2f}; B plane {Bh[0]:.2f}/{Bh[1]:.2f}/{Bh[2]:.2f}; current 21.05/21.04/20.94')
print(f'   base-front plane range {np.linalg.norm(onp(bb, H0)):.4f} vs stated 0.9998')
# cup rim diameter
l, r_ = (724.0, 381), (794.5, 381)
for rng, lab in ((RC, 'front range 0.874'), (None, 'axis range (front + R)')):
    if rng is None:
        # axis horizontal distance: front base point on plane + rim radius
        cb = onp((759, 497.5), H0); rng = np.linalg.norm(cb) + 0.043
    print(f'cup rim: A {lab} {rng:.4f}: {np.linalg.norm(rng * ray(l) - rng * ray(r_)) * 100:.2f} cm')
cbf = onp((759, 497.5), H0); print(f'   cup base-front plane range {np.linalg.norm(cbf):.4f} vs stated 0.874')
for f in (0.98, 1, 1.02):
    cb = onp((759, 497.5), H0 * f); hh = vert_height((759, 497.5), (759, 381), H0 * f)
    # rim edges at the axis depth: axis point = base front + rim radius along the horizontal viewing direction (iterate)
    Rr = 0.043
    for _ in range(5):
        dirh = cb - (cb @ n) * n; dirh /= np.linalg.norm(dirh)
        axis_top = cb + dirh * Rr - n * hh
        # rim plane through axis_top parallel to table; intersect rays of l and r_
        def onrim(p): rr = ray(p); return (axis_top @ n) / (n @ rr) * rr
        Rr = np.linalg.norm(onrim(l) - onrim(r_)) / 2
    print(f'   B plane h x{f}: cup height to row 381 {hh*100:.2f}, rim diameter {2*Rr*100:.2f}')
# cup-bottle distance
pb, pc = (664.5, 403.5), (759.5, 436.0)
dA = np.linalg.norm(RB * ray(pb) - RC * ray(pc)) * 100
print(f'cup-bottle distance A (stated ranges at centre clicks) {dA:.2f}; current 17.99/17.94/17.94')
for dy in (-15, 15):
    print(f'   clicks moved {dy:+d} px vertically: {np.linalg.norm(RB * ray((pb[0], pb[1]+dy)) - RC * ray((pc[0], pc[1]+dy))) * 100:.2f}')
for f in (0.98, 1, 1.02):
    Bb = onp(bb, H0 * f); Cb = onp((759, 497.5), H0 * f)
    def axis(P, R):
        d = P - (P @ n) * n; d /= np.linalg.norm(d); return P + d * R
    ab, ac = axis(Bb, 0.0335), axis(Cb, 0.036)
    # front-surface points at mid height (centre clicks): front base + half height up
    fb = Bb - n * 0.105; fc = Cb - n * 0.075
    print(f'   B plane h x{f}: axis-axis {np.linalg.norm(ab-ac)*100:.2f}; front-surface mid-height points {np.linalg.norm(fb-fc)*100:.2f}')
# poker tower
apex, ff, lf = (686, 417.0), (701, 500.5), (662, 494.5)
for foot, lab in ((ff, 'front-card foot'), (lf, 'left-card foot'), (((ff[0]+lf[0])/2, (ff[1]+lf[1])/2), 'mid feet')):
    a = np.linalg.norm(RP * ray(apex) - RP * ray(foot)) * 100
    b = [vert_height(foot, apex, H0 * f) * 100 for f in (0.98, 1, 1.02)]
    print(f'poker tower ({lab}): A {a:.2f}; B plane {b[0]:.2f}/{b[1]:.2f}/{b[2]:.2f}; foot plane range {np.linalg.norm(onp(foot, H0)):.4f} (stated 0.9035); current 10.42')
# --- cup rim, route B done properly: rim extremes lie in the vertical plane through the cup axis, perpendicular to the
# horizontal viewing direction (rays at row 381 graze the rim plane, so intersecting the rim plane is ill-conditioned)
print('cup rim B (axis-plane intersection):')
for f in (0.98, 1, 1.02):
    cb = onp((759, 497.5), H0 * f)
    for Rb in (0.033, 0.036):
        dirh = cb - (cb @ n) * n; dirh /= np.linalg.norm(dirh)
        ax = cb + dirh * Rb      # axis point at table level
        def onv(p): rr = ray(p); return (ax @ dirh) / (dirh @ rr) * rr
        print(f'   h x{f}, base radius {Rb*100:.1f}: rim diameter {np.linalg.norm(onv(l) - onv(r_))*100:.2f}  (axis range {np.linalg.norm(ax):.4f})')
