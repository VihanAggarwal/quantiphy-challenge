"""Label-style forward-difference speeds at t = 0.2, 0.4, 0.6, 0.8 s (capture n = 5, 10, 15, 20) on the 25 fps clock.
P(n) = d_stated(n) * u(click_n); P(n+1) = d(n+1) * u(click_{n+1}), d(n+1) from several depth routes:
  anchor-lin : linear interpolation of the stated surface ranges in capture time (n20: extrapolated with the n15-20 slope);
  plane-raw  : d(n) + [plane(n+1) - plane(n)] (raw silhouette centres);
  plane-sm   : same with a local quadratic fit (+-3 frames, capture clock) of the plane range;
  size-sm    : same with the smoothed size range;
  scaled     : the above Delta times the stated/plane ratio at n (ToF scale).
Clicks: x-render silhouette centroid (raw) and a local-quadratic-smoothed centre.
Physical: 3D plane positions (ball centre), local quadratic fit, forward difference n->n+1 and instantaneous at n."""
import numpy as np, json, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0030/scripts')
from depths import cap, unit, plane_pos, size_range, M, ANCH, R
nn = []; P3 = []; px = []; rs = []; rp = []
for k, m in enumerate(M):
    if m is None:
        continue
    n = cap(k); nn.append(n); px.append((m['mx'], m['my']))
    p = plane_pos(m['mx'], m['my']); P3.append(p); rp.append(np.linalg.norm(p)); rs.append(size_range(min(m['el'][1])))
nn = np.array(nn); P3 = np.array(P3); px = np.array(px); rs = np.array(rs); rp = np.array(rp)
an = np.array(sorted(ANCH)); av = np.array([ANCH[a] for a in an])


def lfit(y, n0, half=3, deg=2, at=None):
    sel = np.abs(nn - n0) <= half
    co = np.polyfit(nn[sel] - n0, y[sel], deg)
    return np.polyval(co, (at if at is not None else n0) - n0), co


def anchor_lin(n):
    if n <= an[-1]:
        return float(np.interp(n, an, av))
    return float(av[-1] + (av[-1] - av[-2]) / 5 * (n - an[-1]))


def idx(n):
    w = np.where(nn == n)[0]
    return int(w[0]) if len(w) else None


def click(n, smooth=False):
    if not smooth:
        i = idx(n)
        return px[i]
    return np.array([lfit(px[:, 0], n)[0], lfit(px[:, 1], n)[0]])


out = {}
for t in [0.2, 0.4, 0.6, 0.8]:
    n = int(round(t * 25)); d0 = ANCH[n]
    res = {}
    for sm in [False, True]:
        c0 = click(n, sm); c1 = click(n + 1, sm)
        u0 = unit(*c0); u1 = unit(*c1)
        dr_plane_raw = rp[idx(n + 1)] - rp[idx(n)]
        dr_plane_sm = lfit(rp, n, at=n + 1)[0] - lfit(rp, n)[0]
        dr_size_raw = rs[idx(n + 1)] - rs[idx(n)]
        dr_size_sm = lfit(rs, n, at=n + 1)[0] - lfit(rs, n)[0]
        dr_anchor = anchor_lin(n + 1) - d0
        kscale = d0 / (lfit(rp, n)[0] - R)
        routes = {'anchor-lin': dr_anchor, 'plane-raw': dr_plane_raw, 'plane-sm': dr_plane_sm,
                  'size-raw': dr_size_raw, 'size-sm': dr_size_sm,
                  'plane-sm*k': dr_plane_sm * kscale, 'size-sm*k': dr_size_sm * kscale}
        for name, dr in routes.items():
            v = np.linalg.norm((d0 + dr) * u1 - d0 * u0) * 25 * 100
            tang = np.linalg.norm(d0 * (u1 - u0)) * 25 * 100
            res[f"{'smclick' if sm else 'rawclick'}/{name}"] = (round(v, 1), round(dr * 100, 2), round(tang, 1))
    # physical: plane 3D, local quadratic
    fx = [lfit(P3[:, j], n) for j in range(3)]
    pos_n = np.array([f[0] for f in fx]); pos_n1 = np.array([lfit(P3[:, j], n, at=n + 1)[0] for j in range(3)])
    vel = np.array([f[1][1] for f in fx])  # derivative of quadratic at n0 (per frame)
    res['phys/plane FD'] = round(np.linalg.norm(pos_n1 - pos_n) * 25 * 100, 1)
    res['phys/plane inst'] = round(np.linalg.norm(vel) * 25 * 100, 1)
    raw = P3[idx(n + 1)] - P3[idx(n)]
    res['phys/plane raw FD'] = round(np.linalg.norm(raw) * 25 * 100, 1)
    res['scale k (stated/plane surf)'] = round(kscale, 3)
    out[t] = res
    print(f'\n=== t={t}  n{n}->n{n+1}  d_stated={d0}')
    for kk, vv in res.items():
        print(f'  {kk:28s} {vv}')
json.dump({str(k): v for k, v in out.items()}, open('/home/user/quantiphy-challenge/research/next/labaudit2/0030/label_style.json', 'w'), indent=1)
