"""Size-based range check: the book's top face spans the full 20.4 cm along the board edge direction e; its 3D extent
along e (back-projected on the slope top-surface plane) vs the true 20.4 rescales the plane-model range."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from geom import *
from frames import load
from track import teal
from motion import cap
for tag in ['', 'x']:
    fr = load(tag); line = []
    for k in [10, 22, 23, 24, 25, 26, 27, 28, 29]:
        m, st, c = teal(fr[k]); ys, xs = np.nonzero(m); xs = xs + 480; ys = ys + 330
        X = np.array([on_slope(u, v, 0.0146) for u, v in zip(xs, ys)])
        ax = X @ e; lo, hi = np.percentile(ax, [0.5, 99.5]); ext = (hi - lo) * 100
        rm = np.linalg.norm(on_slope(c[0], c[1], 0.0146))
        line.append('v%d ext_e %.1f rng_model %.3f' % (k, ext, rm))
    print(tag or 'o', ' | '.join(line))
