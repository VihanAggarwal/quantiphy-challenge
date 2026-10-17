"""Label-style and physical ball speeds for family 0040 on the 25 fps capture clock.
Video frame n -> capture frame c(n) = n + (n>=12) + (n>=36) (one capture frame dropped after video 11 and 35;
the 35->36 step is the double-length one). Clicked centre = capsule centre (occlusion-corrected) or blob centroid.
Ranges: (A) stated surface ranges, linear in capture time between c38 (video 36, t=1.5) and c50 (video 48, t=2.0);
(B) size-based centre range from the blob minor axis (D = 4.0 cm), smoothed by a line in capture time,
and converted to the surface (-2 cm) like the ToF read."""
import json, numpy as np, sys
F, CX, CY = 711.0, 640.0, 360.0
B1 = '/home/user/quantiphy-challenge/research/next/labaudit/0040'
B2 = '/home/user/quantiphy-challenge/research/next/labaudit2/0040'
def cap(n): return n + (n >= 12) + (n >= 36)
def ray(u, v):
    r = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return r / np.linalg.norm(r)
def load(R, mode):
    t1 = {int(k): v for k, v in json.load(open(f'{B1}/track_{R}.json')).items()}
    tc = {int(k): v for k, v in json.load(open(f'{B2}/track_caps_{R}.json')).items()}
    fx = {int(k): v for k, v in json.load(open(f'{B2}/capfixed_{R}.json')).items()}
    out = {}
    for n in range(23, 49):
        u, v = t1[n]['u'], t1[n]['v']
        if mode == 'caps':
            if n in fx and n in (32, 34, 35, 38): u, v = fx[n]
        out[n] = dict(u=u, v=v, minor=t1[n]['minor'])
    return out
def size_range(e):   # centre range from tangential diameter: minor = F*D/(d*cos th)
    r = ray(e['u'], e['v']); return F * 0.04 / (e['minor'] * r[2])
anch = {38: 0.7045, 50: 0.627}
def rng_anchor(c):
    return 0.7045 + (0.627 - 0.7045) * (c - 38) / 12.0
if __name__ == '__main__':
    for R in ('x', 's'):
        for mode in ('caps', 'cent'):
            tr = load(R, mode)
            ns = sorted(tr)
            cs = np.array([cap(n) for n in ns])
            sr = np.array([size_range(tr[n]) for n in ns])
            # size line fit on clean post-bounce frames (video 36-39, 42-48; 40/41 over table, 34/35 occluded)
            sel = [i for i, n in enumerate(ns) if n in (36, 37, 39, 42, 43, 44, 45, 46, 47, 48)]
            p = np.polyfit(cs[sel], sr[sel], 1)
            kcal = np.mean([(anch[c] + 0.02) / np.polyval(p, c) for c in anch])
            def rng_size(c, p=p): return np.polyval(p, c) - 0.02            # raw size-based surface range
            def rng_size_cal(c, p=p, k=kcal): return k * np.polyval(p, c) - 0.02
            if R == 'x' and mode == 'caps':
                print('size ranges per frame (centre):', ' '.join(f'{n}:{s:.3f}' for n, s in zip(ns, sr)))
                print(f'size line at c38 {np.polyval(p,38):.3f} c50 {np.polyval(p,50):.3f}; anchors(centre) {0.7245} {0.647}; cal k={kcal:.3f}')
            for rname, rf in (('anchor', rng_anchor), ('size', rng_size), ('size_cal', rng_size_cal)):
                P = {n: rf(cap(n)) * ray(tr[n]['u'], tr[n]['v']) for n in ns}
                def fd(n0, n1):
                    return np.linalg.norm(P[n1] - P[n0]) / ((cap(n1) - cap(n0)) / 25.0) * 100
                # capture frame 37 (dropped): quadratic through video 34,35,36,37 in capture time
                cc = np.array([cap(n) for n in (34, 35, 36, 37)]); PP = np.array([P[n] for n in (34, 35, 36, 37)])
                co = np.polyfit(cc, PP, 2); P37 = np.array([np.polyval(co[:, j], 37) for j in range(3)])
                v15b = np.linalg.norm(P[36] - P37) * 25 * 100
                # path 1.5 -> 1.9 s: video 36..46 (capture 38..48), and capture-time variant 37.5..47.5
                path = sum(np.linalg.norm(P[n + 1] - P[n]) for n in range(36, 46)) * 100
                print(f'{R} {mode:4s} {rname:8s} v1.4[c35->36]={fd(34,35):6.1f}  v1.4[c34->35]={fd(33,34):6.1f}  '
                      f'v1.5[c38->39]={fd(36,37):5.1f}  v1.5[c37->38]={v15b:5.1f}  [c36->38]/2={fd(35,36):5.1f}  path c38-48={path:5.1f}')
