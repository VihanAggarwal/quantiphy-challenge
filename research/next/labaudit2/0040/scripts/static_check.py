"""Independent pixel re-measurement of the static props on the x-render median (black background):
foreground mask = non-black; extents read from mask rows/columns. Back-projected with the stated ranges."""
import cv2, numpy as np
F, CX, CY = 711.0, 640.0, 360.0
m = cv2.imread('/home/user/quantiphy-challenge/research/next/labaudit/0040/median_x.png').astype(int)
fg = m.sum(-1) > 60
def ray(u, v):
    r = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return r / np.linalg.norm(r)
def dist(a, b, ra, rb=None):
    rb = ra if rb is None else rb; return np.linalg.norm(ra * ray(*a) - rb * ray(*b)) * 100
# cup: columns 730..825, rows above the table top. Width per row above the table (cup stands out against black)
print('cup: row widths (x render, black bg above table line)')
for y in (378, 380, 383, 386, 390, 400, 420, 440):
    xs = np.nonzero(fg[y, 720:840])[0] + 720
    if len(xs): print(f'  y={y}: x {xs.min()}..{xs.max()}  width {xs.max()-xs.min()+1} px')
col = fg[:, 776]; ys = np.nonzero(col[300:470])[0] + 300; print('  cup top at col 776: y=', ys.min())
for y in (378, 380):
    xs = np.nonzero(fg[y, 720:840])[0] + 720
    print(f'  rim diameter from row {y}: {dist((xs.min()-0.5, y), (xs.max()+0.5, y), 0.842):.2f} cm')
# tape: against black above the table? tape top rim rows
print('tape: row widths')
for y in (438, 440, 445, 450):
    xs = np.nonzero(fg[y, 540:640])[0] + 540
    if len(xs): print(f'  y={y}: x {xs.min()}..{xs.max()} width {xs.max()-xs.min()+1}')
print('poker tower: top')
for x in range(676, 700, 3):
    ys = np.nonzero(fg[380:470, x])[0] + 380
    if len(ys): print(f'  x={x}: top y={ys.min()}')
cv2.imwrite('/home/user/quantiphy-challenge/research/next/labaudit2/0040/img/static_zoom.png',
            cv2.resize(m[360:520, 530:830].astype(np.uint8), None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST))
