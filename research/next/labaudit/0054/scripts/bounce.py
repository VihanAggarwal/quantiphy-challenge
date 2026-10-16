"""Green-ball impact timing in a: fit-predicted pixel positions vs observed at n36/n37/n38, and the forward-difference
speed that straddles the bounce (P(n37) on the observed ray at the fit's range) for the label-timing variants."""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ballistic_a as BA
from ballistic_a import tc, F, CX, CY
def ray(u, v):
    d = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return d / np.linalg.norm(d)
for name, tr, frs in (('green', BA.green, list(range(24, 36))), ('white', BA.white, list(range(29, 36)))):
    o = BA.fit(tr, frs, 2.5)
    for n in (35, 36, 37, 38):
        P = o['pos'](tc(n)); u, v = F * P[0] / P[2] + CX, F * P[1] / P[2] + CY
        obs = tr.get(n)
        print('%s n%d t=%.2f predicted (%.1f,%.1f) range %.3f  observed %s' % (name, n, tc(n), u, v, np.linalg.norm(P), obs))
    # straddle variant: P36 from fit (mid-air), P37 = observed ray at fit range at 1.56
    P36 = o['pos'](1.52)
    obs37 = {'green': (340.5, 656.5), 'white': (375.7, 613.7)}[name]
    r37 = np.linalg.norm(o['pos'](1.56))
    P37 = r37 * ray(*obs37)
    print('  %s forward diff n36->n37 (1.52->1.56): %.2f m/s (x25) ; free-flight 1.48->1.52: %.2f ; 1.52->1.56 free: %.2f' % (
        name, np.linalg.norm(P37 - P36) * 25, np.linalg.norm(o['pos'](1.52) - o['pos'](1.48)) * 25, np.linalg.norm(o['pos'](1.56) - o['pos'](1.52)) * 25))
