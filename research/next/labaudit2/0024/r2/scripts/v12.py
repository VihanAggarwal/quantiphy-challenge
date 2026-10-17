"""v(1.2) = forward difference capture 30->31 = video 29->30, the frame where the book tips over the slope foot."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from geom import *
from motion import uv, HB
for tag in 'osx':
    P29 = on_slope(*uv(tag, 29), HB); P32 = on_plane(*uv(tag, 32), HB); P33 = on_plane(*uv(tag, 33), HB)
    r29, r32 = np.linalg.norm(P29), np.linalg.norm(P32)
    out = []
    for nm, r30 in [('lin29-32', r29 + (r32 - r29) / 3), ('slope-plane', np.linalg.norm(on_slope(*uv(tag, 30), HB))),
                    ('mid', 0.5 * (r29 + (r32 - r29) / 3) + 0.5 * np.linalg.norm(on_slope(*uv(tag, 30), HB)))]:
        P30 = ray(*uv(tag, 30)) * r30
        phys = np.linalg.norm(P30 - P29) * 2500
        lab = np.linalg.norm(ray(*uv(tag, 30)) * (0.977 + r30 - r29) - ray(*uv(tag, 29)) * 0.977) * 2500
        out.append('%s r30 %.3f phys %.0f label(stated .977 + model dr) %.0f' % (nm, r30, phys, lab))
    print(tag, 'r29 %.3f r32 %.3f |' % (r29, r32), ' | '.join(out))
