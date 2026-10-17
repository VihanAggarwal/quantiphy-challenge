"""Pencil bag in camera a (ax renders): top edge (first non-black row) and bottom edge (dark SAM outline / shadow
minimum) per column; height profile -> depth ratio between the bag's ends."""
import cv2, numpy as np, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0034/scripts')
from frames import read
X = read('ax')
for fi in (0, 5, 10, 15):
    im = X[fi]; V = im.max(2).astype(int)
    xs, tops, bots = [], [], []
    for x in range(548, 672, 4):
        col = V[400:500, x]; nz = np.nonzero(col > 30)[0]
        if not len(nz): continue
        top = 400 + nz.min()
        seg = col[top - 400 + 25: top - 400 + 60]
        bot = top + 25 + int(np.argmin(seg))
        xs.append(x); tops.append(top); bots.append(bot)
    xs, tops, bots = map(np.array, (xs, tops, bots)); h = bots - tops
    sel = (xs >= 560) & (xs <= 660)
    pt = np.polyfit(xs[sel], tops[sel], 1); pb = np.polyfit(xs[sel], bots[sel], 1); ph = np.polyfit(xs[sel], h[sel], 1)
    print(f'frame {fi}: top slope {pt[0]*100:.1f} px/100px, bottom slope {pb[0]*100:.1f} px/100px, '
          f'height at x=560 {np.polyval(ph,560):.1f}, at x=660 {np.polyval(ph,660):.1f}, ratio {np.polyval(ph,560)/np.polyval(ph,660):.3f}')
    if fi == 0:
        print(' x   ', ' '.join(f'{v:4d}' for v in xs)); print(' top ', ' '.join(f'{v:4d}' for v in tops)); print(' bot ', ' '.join(f'{v:4d}' for v in bots)); print(' h   ', ' '.join(f'{v:4d}' for v in h))
