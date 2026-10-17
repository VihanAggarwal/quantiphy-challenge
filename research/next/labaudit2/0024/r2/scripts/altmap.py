"""Robustness: label-style values under the alternative clock (no drop before video 12: t=1.0 -> video 25, t=1.2 -> video 30)
and under the main clock (t=1.0 -> video 24, t=1.2 -> video 29), with the tip model for the 3D track."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from geom import *
from motion import uv
from tipmodel import solve, top_centre
R1, R2 = 1.0685, 0.977
for tag in 'osx':
    P = {k: top_centre(*solve(*uv(tag, k))[0]) for k in range(22, 34)}
    rr = {k: np.linalg.norm(P[k]) for k in P}
    s = tag
    for nm, (k1, k2) in {'main': (24, 29), 'alt': (25, 30)}.items():
        out = []
        for kk, Rs in [(k1, R1), (k2, R2)]:
            phys = np.linalg.norm(P[kk + 1] - P[kk]) * 2500
            off = np.linalg.norm(ray(*uv(tag, kk + 1)) * (Rs + rr[kk + 1] - rr[kk]) - ray(*uv(tag, kk)) * Rs) * 2500
            rint = Rs + (R2 - R1) / (k2 - k1)
            itp = np.linalg.norm(ray(*uv(tag, kk + 1)) * rint - ray(*uv(tag, kk)) * Rs) * 2500
            out.append('v%d->%d model %.0f, stated+offset %.0f, stated+lin %.0f' % (kk, kk + 1, phys, off, itp))
        s += ' | %s: ' % nm + ' ; '.join(out)
    print(s)
