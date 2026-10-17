"""Audit cross-checks for family simulation_0153 (clips 0149-0153, parking garage).

Independent second routes for the singleton rows in simulation_0150:
  * B1 lettering size: 0150 (f from depth_info) vs 0153 camera (different camera,
    scale from blue-tire camera height h and the far-wall base row, f-free).
  * Pillar spacing: 0150 (f*h = 3724 from the B1 depth) vs 0153 (f*h from the blue tire).
Run: .venv/bin/python research/next/sim3audit/simulation_0153/crosscheck.py
"""
import cv2
import numpy as np

D = '/home/user/quantiphy-challenge/data/QuantiPhy/'


def frame(clip, i):
    cap = cv2.VideoCapture(D + f'simulation_{clip}.mp4')
    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    ok, im = cap.read()
    assert ok
    return im


def yellow_bbox(im, x0, x1, y0, y1):
    sub = im[y0:y1, x0:x1].astype(int)
    yel = sub[:, :, 2] - sub[:, :, 0]
    m = yel > 0.5 * yel.max()
    ys, xs = np.nonzero(m)
    return xs.min() + x0, xs.max() + x0, ys.min() + y0, ys.max() + y0


def base_row(im, x0, x1, y0, y1):
    """Row of the dark contact shadow line at a pillar/wall base (min of column mean)."""
    g = im[y0:y1, x0:x1].astype(float).mean(axis=(1, 2))
    return y0 + int(np.argmin(g))


# ---------------- simulation_0150 (camera A, aisle view) ----------------
im50 = frame('0150', 41)                       # car gone
bx0, bx1, by0, by1 = yellow_bbox(im50, 850, 1100, 400, 620)
w50, h50 = bx1 - bx0, by1 - by0                # ~181 x 167 px
Z_B1 = 23.44                                   # depth_info, sign ~on optical axis
for f in (2606.0, 2666.7):                     # agent f (wall+tire) and Blender default
    print(f'0150 B1 f={f:.0f}: W={w50 * Z_B1 / f:.3f}  H={h50 * Z_B1 / f:.3f}')
v0_50, fh50 = 539.4, 3724.0                    # horizon, f*h (B1 wall base v=698.3 at 23.44 m)
vm = base_row(im50, 300, 330, 740, 800)        # mid pillar front face base (~771.5)
vf = base_row(im50, 470, 500, 680, 730)        # far pillar front face base (~704)
print('0150 pillar fronts Z:', fh50 / (vm - v0_50), fh50 / (vf - v0_50),
      'c-c =', fh50 / (vf - v0_50) - fh50 / (vm - v0_50))

# ---------------- simulation_0153 (camera B = 0152 camera, corridor view) ----------------
im53 = frame('0153', 0)
v0_53 = 539.2                                  # corridor VP row (light strips)
# camera height from the blue tire (prior 0.369 m): hub v=895.0, bottom v=948.7 (frame 41)
R = 0.369 / 2
h53 = R * (948.7 - v0_53) / (948.7 - 895.0)
print(f'0153 camera height h = {h53:.3f} m')
cx0, cx1, cy0, cy1 = yellow_bbox(im53, 860, 1080, 460, 600)
w53, hh53 = cx1 - cx0, cy1 - cy0               # ~69 x 65 px
v_wall = 599.3                                 # far wall base (50% crossing at centre columns)
print(f'0153 far B1 (f-free): W={w53 * h53 / (v_wall - v0_53):.3f}  H={hh53 * h53 / (v_wall - v0_53):.3f}')
fh53 = 2666.7 * h53                            # f from blue tire + depth_info ~2651-2667
rows = [base_row(im53, 1700, 1740, 800, 850), base_row(im53, 1470, 1500, 710, 750),
        base_row(im53, 1340, 1360, 670, 700)]
Z = [fh53 / (v - v0_53) for v in rows]
print('0153 right pillar fronts rows', rows, 'Z', np.round(Z, 2), 'c-c', np.round(np.diff(Z), 2))
