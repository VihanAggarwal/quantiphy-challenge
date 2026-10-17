"""Ball motion on the 25 fps capture clock. Video k -> capture c(k) = k + [k>=12] + [k>=36] (double-length steps at
video 11->12 (push) and 35->36 (rolling; 31 px vs 16 px)). Centre pixel: u = middle of the horizontal extent,
v = top edge + R_px (R_px = 2 cm * F / range, iterated). Range models:
  plane : ray / table-plane intersection 2 cm above the table (camera height h from table.py, or h scaled);
  label : clicked-surface range = stated 0.716 at t=1.4 (capture 35), other frames 0.716 + plane change of surface range.
Smooth track: per-coordinate straight-line fit vs capture time over rolling frames 17..48 (excluding 30-35 where the
ball crosses the white flat card), per render."""
import json, numpy as np, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0038/scripts')
from common import B, F, ray, cap_of_video
T = json.load(open(f'{B}/track.json'))
pl = np.load(f'{B}/plane.npy'); n, h0 = pl[:3], pl[3]
R = 0.02
def centre_px(r):
    return (r['xl'] + r['xr']) / 2, r['top']
def plane_pos(u, top, h):
    rng = 0.74
    for _ in range(6):
        v = top + R * F / rng
        d = ray(u, v); rng = (h - R) / (n @ d)
    return rng, d, v
res = {}
for h in (h0, 0.1728, 0.1766):
  print(f'\n######## camera height h = {h:.4f} m')
  for tag in ('o', 's', 'x'):
    rows = [r for r in T[tag] if r is not None]
    ks = np.array([r['f'] for r in rows]); cs = np.array([cap_of_video(k) for k in ks]); ts = cs / 25.0
    U = np.array([centre_px(r) for r in rows], float)
    PP, RR, DD = [], [], []
    for (u, top) in U:
        rng, d, v = plane_pos(u, top, h); PP.append(rng * d); RR.append(rng); DD.append(d)
    PP = np.array(PP); RR = np.array(RR); DD = np.array(DD)
    sel = (ks >= 17) & ~((ks >= 30) & (ks <= 35))
    # smooth fits in pixel space (u, top) vs capture time, then back-project -> label-style + physical
    pu = np.polyfit(ts[sel], U[sel, 0], 1); pt = np.polyfit(ts[sel], U[sel, 1], 1)
    resid = U[sel, 0] - np.polyval(pu, ts[sel])
    def smooth(t):
        u, top = np.polyval(pu, t), np.polyval(pt, t)
        return plane_pos(u, top, h)
    r35, d35, _ = smooth(35 / 25); r36, d36, _ = smooth(36 / 25)
    s35, s36 = r35 - R, r36 - R            # surface ranges
    # label-style: surface range anchored to the stated 0.716 at capture 35
    L35 = 0.716 * d35; L36 = (0.716 + s36 - s35) * d36
    v_label = np.linalg.norm(L36 - L35) * 25
    v_label_ratio = np.linalg.norm(0.716 * (s36 / s35) * d36 - L35) * 25
    # physical (plane, centre range), smooth velocity at t=1.4
    v_phys = np.linalg.norm(smooth(1.4 + 0.02)[0] * smooth(1.4 + 0.02)[1] - smooth(1.4 - 0.02)[0] * smooth(1.4 - 0.02)[1]) / 0.04
    # physical rescaled so that the plane surface range at t=1.4 equals the stated 0.716
    k14 = 0.716 / s35
    # raw per-frame forward difference from video 34 -> 35 (capture 35 -> 36), label-style ranges
    i34, i35 = list(ks).index(34), list(ks).index(35)
    raw_l = np.linalg.norm((0.716 + (RR[i35] - RR[i34])) * DD[i35] - 0.716 * DD[i34]) * 25
    print(f'[{tag}] u-fit {pu[0]/25:.2f} px/capframe (resid sd {resid.std():.2f}px); plane centre range @1.4 {r35:.4f} -> surface {s35:.4f} (stated 0.716, ratio {0.716/s35:.3f})')
    print(f'      v(1.4) label-style smooth c35->c36: {v_label*100:.2f} (ratio-scaled {v_label_ratio*100:.2f}) | raw clicks v34->v35: {raw_l*100:.2f}'
          f' | physical plane {v_phys*100:.2f}, rescaled to stated {v_phys*k14*100:.2f} cm/s')
    # displacement 0.9 -> 1.4 s
    for ta in (22 / 25, 22.5 / 25, 23 / 25):
        ra, da, _ = smooth(ta)
        La = (0.716 + (ra - R) - s35) * da
        dl = np.linalg.norm(L35 - La)
        dp = np.linalg.norm(r35 * d35 - ra * da)
        print(f'      disp {ta:.2f}->1.40 s: label-style {dl*100:.2f} cm | physical plane {dp*100:.2f}, rescaled {dp*k14*100:.2f}')
    # raw (unsmoothed) displacement using the actual video frames for capture 22/23 (video 21/22) and 35 (video 34)
    for va in (21, 22):
        ia = list(ks).index(va)
        dl = np.linalg.norm(0.716 * DD[i34] - (0.716 + RR[ia] - RR[i34]) * DD[ia])
        print(f'      raw disp video {va}(cap {cap_of_video(va)}) -> video 34 (cap 35): label-style {dl*100:.2f} cm')
