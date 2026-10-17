"""Label-style emulation for the motion rows of family 0006 (capture c = video + 1 for video 12-35).
t=1.0 s -> c25 = v24; t=1.2 s -> c30 = v29; c31 = v30; c32 = v31; c33 = v32 (first frame on the table)."""
import numpy as np
from common import F, CX, CY, ray
from ballistic import fit, model, dn
rng = np.random.default_rng(0)
C = {24: (606.3, 142.5), 29: (580.5, 224.0), 30: (571.0, 283.0), 31: (560.5, 367.0), 32: (550.0, 446.0), 33: (533.0, 435.0)}
R25, R30 = 1.402, 1.065
def P(v, R, d=(0, 0)): return R * ray(C[v][0] + d[0], C[v][1] + d[1])
def zfac(v): return ray(*C[v])[2]
print('== displacement 1.0->1.2 s (stated ranges at the clicks v24 and v29)')
print('  range model: %.1f cm' % (100 * np.linalg.norm(P(29, R30) - P(24, R25))))
Zp = lambda v, Zd: np.array([(C[v][0] - CX) * Zd / F, (C[v][1] - CY) * Zd / F, Zd])
print('  if the stated values were Z-depths: %.1f cm' % (100 * np.linalg.norm(Zp(29, R30) - Zp(24, R25))))
for dv in ((24, 29), (25, 29), (24, 28), (25, 30)):
    pass
# alternative click centres (yellow-only centroid) at v29
alt = R30 * ray(589.3, 223.6)
print('  yellow-only centre at v29: %.1f cm' % (100 * np.linalg.norm(alt - P(24, R25))))
print('  MC (3 px clicks): ', end='')
d = [np.linalg.norm(R30 * ray(*(np.array(C[29]) + rng.normal(0, 3, 2))) - R25 * ray(*(np.array(C[24]) + rng.normal(0, 3, 2)))) for _ in range(20000)]
print('median %.1f, 10-90%% %.1f-%.1f cm' % tuple(100 * np.percentile(d, [50, 10, 90])))

print('\n== v at 1.2 s: 25*|P(c31)-P(c30)|, P(c30) at the stated 1.065 m')
# R(c31) routes
rr = R30 + (R30 - R25) / 5
print('  route a, linear range extrapolation: R31 = %.4f' % rr)
Z30 = R30 * zfac(29)
for Zc33 in (0.866, 0.889, 0.92):
    Z31 = Z30 + (Zc33 - Z30) / 3
    print('  route c, Z linear c30 -> table contact c33 (Z %.3f): R31 = %.4f' % (Zc33, Z31 / zfac(30)))
fits = []
for vids in (list(range(25, 32)), list(range(26, 32)), list(range(26, 31))):
    o, s = fit(vids, lambda v: v + 1, True, verbose=False)
    R31 = np.linalg.norm(model(o['p'], np.array([0.04]))[0])
    fits.append((vids, R31, o))
    print('  route b, ballistic fit v%d-v%d with stated ranges: R31 = %.4f (model R30 %.3f), physical |V|(1.2) %.2f, fit FD %.2f, Vz %.2f, apex %.3f'
          % (vids[0], vids[-1], R31, o['R30'], o['v30'], o['fd30'], o['V'][2], o['tapex']))
for R31 in (rr, 0.990, 1.000, 1.010, 1.020, 1.040, 1.065):
    print('  R31 %.3f -> label-style %.2f m/s' % (R31, 25 * np.linalg.norm(P(30, R31) - P(29, R30))))
# label needed for 2.1
for R31 in np.arange(0.95, 1.12, 0.005):
    v = 25 * np.linalg.norm(P(30, R31) - P(29, R30))
    if abs(v - 2.1) < 0.03: print('  label 2.1 needs R31 ~ %.3f (ToF error %+.1f cm vs route a)' % (R31, 100 * (R31 - rr)))
print('  MC (clicks 3 px both frames, R31 = route a/b/c spread 0.993-1.003, ToF sigma at c31 of 2/3/4 cm; c30 range fixed as stated):')
ans = np.array([2.1, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8])
def score(a, L):
    e = np.abs(a - L) / L
    return np.where(e < 0.05, 1.0, np.clip(1 - e, 0, 1))
for sig in (0.02, 0.03, 0.04):
    vals = []
    for _ in range(20000):
        R31 = rng.uniform(0.993, 1.003) + rng.normal(0, sig)
        a = R30 * ray(*(np.array(C[29]) + rng.normal(0, 3, 2)))
        b = R31 * ray(*(np.array(C[30]) + rng.normal(0, 3, 2)))
        vals.append(25 * np.linalg.norm(b - a))
    vals = np.array(vals)
    sc = [score(x, vals).mean() for x in ans]
    print('   sigma %.0f cm: median %.2f, 10-90%% %.2f-%.2f; expected score for answers %s: %s'
          % (100 * sig, np.median(vals), *np.percentile(vals, [10, 90]), ans, np.round(sc, 3)))

print('\n== v at first desk impact')
for (va, vb), lab in (((31, 32), 'c32->c33 (last airborne -> first on table)'), ((32, 33), 'c33->c34 (first on table -> bounce)')):
    for Za, Zb in ((0.925, 0.889), (0.925, 0.866), (0.94, 0.90), (0.91, 0.87)):
        if (va, vb) == (32, 33): Za, Zb = Zb, Zb - 0.0
        pa = Zp(va, Za); pb = Zp(vb, Zb)
        print('  %s Z %.3f/%.3f: %.2f m/s' % (lab, Za, Zb, 25 * np.linalg.norm(pb - pa)))
# physical: fit with ranges; impact when the toy centre is r above the table plane (camera 0.174 m above top, front=60.3 cm; 76 cm alt)
for vids, R31, o in fits:
    for h, r in ((0.174, 0.05), (0.174, 0.045), (0.22, 0.05)):
        ts = np.arange(0.0, 0.25, 0.0005)
        X = model(o['p'], ts); y = X @ dn
        k = np.argmax(y >= h - r)
        V = o['p'][3:6] + 9.8 * dn * ts[k]
        print('  physical (fit v%d-v%d, cam %.3f above top, r %.3f): impact t=%.3f s, Z %.3f, |V| %.2f (vertical %.2f)'
              % (vids[0], vids[-1], h, r, 1.2 + ts[k], X[k, 2], np.linalg.norm(V), V @ dn))
