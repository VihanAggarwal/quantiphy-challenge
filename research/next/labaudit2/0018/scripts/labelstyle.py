"""Label-style values for the 0018 family under the clock reading T_label = T_clip + 2.0 s (capture clock),
i.e. 3.0 s -> capture c25 = video v24 (all objects held), 3.4 s -> c35 = v34 (all four falling).
Clicked centres: x-matte centroids (checked by eye on zoomed crops); held centres by eye at v24.
Depth (surface Z at the click), by route:
  soccer : stated range 2.80 at the held click -> Z 2.749 (gravity fit of the fall: centre Z 2.85 -> surface 2.76)
  box    : 0062 white-box size (L 19-20, W 6.9-7.5 on 51.9 x 20 px) -> 2.45-2.74; floor landing (front-bottom edge y 602) -> 2.57
  tennis : floor contact from fall/rebound parabola intersection (bottom y ~638) -> centre 2.24, surface 2.21;
           fall gravity 2.07 (surface 2.04); rebound gravity 2.51 (surface 2.48)
  pine   : floor landing (bottom y ~698) -> 1.84 centre, surface ~1.80; near-person torso 1.80
Floor: h = 0.875 m, zero pitch (soccer contact + stated range; checked on both persons' feet)."""
import sys, json
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0018/scripts')
from common import *
R = json.load(open(OUT + 'track_refined.json'))
rng = np.random.default_rng(0)
def P(u, v, z): return z * ray(u, v)
held = dict(box=(480.5, 264.0), soccer=(542.6, 263.4), tennis=(763.5, 249.0), pine=(870.0, 250.0))
Zr = dict(box=(2.50, 2.74), soccer=(2.72, 2.78), tennis=(2.04, 2.38), pine=(1.76, 1.86))
Zc = dict(box=2.61, soccer=2.749, tennis=2.21, pine=1.80)
cur = {('box', 'soccer'): 87, ('box', 'pine'): 159, ('box', 'tennis'): 133, ('tennis', 'soccer'): 74, ('pine', 'soccer'): 132, ('pine', 'tennis'): 69}
print('== distances at 3.0 s (v24, held)')
for (a, b), c in cur.items():
    d0 = np.linalg.norm(P(*held[a], Zc[a]) - P(*held[b], Zc[b]))
    ds = []
    for _ in range(4000):
        ua = np.array(held[a]) + rng.normal(0, 2, 2); ub = np.array(held[b]) + rng.normal(0, 2, 2)
        za = rng.uniform(*Zr[a]) + rng.normal(0, 0.02); zb = rng.uniform(*Zr[b]) + rng.normal(0, 0.02)
        if b == 'soccer' or a == 'soccer':
            pass
        ds.append(np.linalg.norm(P(*ua, za) - P(*ub, zb)))
    ds = np.array(ds) * 100
    # route split for tennis depth
    extra = ''
    if 'tennis' in (a, b):
        o = a if b == 'tennis' else b
        vals = [np.linalg.norm(P(*held['tennis'], zt) - P(*held[o], Zc[o])) * 100 for zt in (2.21, 2.04, 2.48)]
        extra = f"  tennis routes floor/fallgrav/rebound: {vals[0]:.1f}/{vals[1]:.1f}/{vals[2]:.1f}"
    if 'box' in (a, b):
        o = a if b == 'box' else b
        vals = [np.linalg.norm(P(*held['box'], zb) - P(*held[o], Zc[o])) * 100 for zb in (2.67, 2.57)]
        extra += f"  box routes size0062/landing: {vals[0]:.1f}/{vals[1]:.1f}"
    print(f"{a:6s}-{b:6s} central {d0*100:6.1f}  MC median {np.median(ds):6.1f} [10-90%: {np.percentile(ds,10):5.1f}-{np.percentile(ds,90):5.1f}]  current {c}  cur/central={c/(d0*100):.2f}{extra}")

def cap(v): return v + (v >= 12) + (v >= 36)
print('\n== v(3.4 s): forward difference c35->c36 (v34->v35); sensitivity c34->c35 and c36->c37 (c37 missing: midpoint of v35/v36 on the fall parabola)')
curv = dict(box=60, soccer=(23.4, 27.6, 25.2), tennis=55, pine=35)
for name in ['box', 'soccer', 'tennis', 'pine']:
    tr = {cap(int(v)): (r['mx'], r['my']) for v, r in R[name].items()}
    # fall parabola for interpolation of c37
    cs = sorted(c for c in tr if 34 <= c <= 38 + (name in ('box', 'soccer')) * 2)
    cs = [c for c in cs if not (name in ('tennis', 'pine') and c >= 38)]
    py = np.polyfit(cs, [tr[c][1] for c in cs], 2); px = np.polyfit(cs, [tr[c][0] for c in cs], 1)
    if 37 not in tr:
        tr[37] = (np.polyval(px, 37), np.polyval(py, 37))
    out = []
    for c0 in (34, 35, 36):
        (u0, v0), (u1, v1) = tr[c0], tr[c0 + 1]
        vals = []
        for _ in range(4000):
            z0 = rng.uniform(*Zr[name]); z1 = z0 + rng.normal(0, 0.02); z0 = z0 + rng.normal(0, 0.02)
            e = rng.normal(0, 2, 4)
            vals.append(25 * np.linalg.norm(P(u1 + e[0], v1 + e[1], z1) - P(u0 + e[2], v0 + e[3], z0)))
        cen = 25 * np.linalg.norm(P(u1, v1, Zc[name]) - P(u0, v0, Zc[name]))
        out.append((c0, cen, np.median(vals), np.percentile(vals, 10), np.percentile(vals, 90), np.hypot(u1 - u0, v1 - v0)))
    # physical: derivative of the fall parabola at c35 (instantaneous) with centre depth
    zc = {'box': 2.64, 'soccer': 2.84, 'tennis': 2.24, 'pine': 1.84}[name]
    vy35 = np.polyval(np.polyder(py), 35); vx35 = px[0]
    phys = 25 * np.hypot(vy35, vx35) * zc / F
    s = '  '.join(f"c{c0}->{c0+1}: step {st:4.1f}px central {cen*100:5.0f} MC {m*100:5.0f} [{lo*100:4.0f}-{hi*100:4.0f}]" for c0, cen, m, lo, hi, st in out)
    print(f"{name:7s} {s}\n        physical |v(c35)| = {phys*100:5.0f} cm/s (parabola slope {vy35:.1f} px/cf at centre Z {zc})  current {curv[name]}")
