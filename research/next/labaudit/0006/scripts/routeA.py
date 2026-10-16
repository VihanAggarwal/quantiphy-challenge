"""Route A: toy extents back-projected at the stated range (label-style). f=711, c=(640,360)."""
import numpy as np
f, cx, cy = 711.0, 640.0, 360.0
def P(u, v, R):
    r = np.array([u - cx, v - cy, f]); return R * r / np.linalg.norm(r)
def ext(p, q, R): return 100 * np.linalg.norm(P(*p, R) - P(*q, R))
cases = {
 # frame: (left,right,yc) , (top,bottom,xc)   read from 6x gridded zooms (toy_grid.png)
 'f24 R1.402': ((576.8, 632.7, 140), (114.5, 165.3, 605), 1.402),
 'f25 R1.402': ((572.0, 629.5, 136), (110.0, 162.5, 601), 1.402),
}
for k, ((l, r, yc), (t, b, xc), R) in cases.items():
    w = ext((l, yc), (r, yc), R); h = ext((xc, t), (xc, b), R)
    print('%s: width %.1f px -> %.2f cm ; height(body) %.1f px -> %.2f cm ; +leaves(~5px) %.2f cm' % (k, r - l, w, b - t, h, ext((xc, t - 5), (xc, b), R)))
for f_ in (700, 711, 725):
    f = f_; print('f=%d f24 width %.2f height %.2f' % (f_, ext((576.8, 140), (632.7, 140), 1.402), ext((605, 114.5), (605, 165.3), 1.402)))
f = 711.0
# t=1.2 s (frame 28.8 at 24 fps / frame 30 at 25 fps) with R=1.065 : widths seen 60-65 px (blurred)
for wpx in (55, 60, 65):
    print('t=1.2 R1.065 width %d px -> %.2f cm' % (wpx, ext((591 - wpx / 2, 215), (591 + wpx / 2, 215), 1.065)))
