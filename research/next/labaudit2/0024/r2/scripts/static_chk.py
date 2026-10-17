"""Quick static re-checks: book long edge on the slope at rest (top face) and on the table at rest; slope width."""
import sys, os, numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
from geom import *
from frames import load
from track import teal
for tag in ['', 's', 'x']:
    fr = load(tag)
    med0 = np.median(np.stack(fr[2:17]), axis=0).astype(np.uint8)
    med1 = np.median(np.stack(fr[38:49]), axis=0).astype(np.uint8)
    out = []
    for nm, im, plane in [('slope-rest', med0, 'slope'), ('table-rest', med1, 'table')]:
        m, st, c = teal(im)
        ys, xs = np.nonzero(m); x0, y0 = 480, 330  # ROI origin
        xs = xs + x0; ys = ys + y0
        pts = np.c_[xs, ys].astype(float)
        f = (lambda p: on_slope(p[0], p[1], 0.0146)) if plane == 'slope' else (lambda p: on_plane(p[0], p[1], 0.0146))
        X = np.array([f(p) for p in pts])
        ax = X @ e
        # extent of the top face along the board's bottom-edge direction e (book length direction), trimmed 0.5% each end
        lo, hi = np.percentile(ax, [0.5, 99.5])
        out.append('%s teal extent along e %.1f cm (raw %.1f)' % (nm, (hi - lo) * 100, (ax.max() - ax.min()) * 100))
    print(tag or 'o', ' | '.join(out))
