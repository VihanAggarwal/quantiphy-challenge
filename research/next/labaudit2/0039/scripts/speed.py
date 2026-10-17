"""v(1.0) and displacement 1.0->1.5 s of the white ball on the 25 fps capture clock.
Capture index: video k -> k (k<=11), k+1 (12..35), k+2 (>=36); the drop between video 35/36 is seen as a double step
in the ball track (the drop near video 11/12 falls while the ball is at rest; assumed from the regular 25->24 pattern).
t=1.0 s = capture 25 = video 24.  t=1.5 s = capture 37 (dropped; interpolated between video 35 and 36) or 38 (= video 36).
Routes:
 A  plane: ball centre on the plane 2 cm above the table (VP plane, h = 0.1724 +- 2 %), 3D quadratic fit in capture time.
 B  stated anchors: surface range linear in capture time between (cap25, 1.014) and (cap37|38, 0.737), along the
    (smoothed or raw) clicked ray.
 C  size: centre range = f D / (w - b), D = 4 cm, blur b fitted to the anchors (surface + 2 cm).
Label-style: P(25) = 1.014 * ray(click25), P(26) = r_est(26) * ray(click26), v = |P26 - P25| * 25."""
import numpy as np, json
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0039'
F, CX, CY = 711.0, 640.0, 360.0
pl = json.load(open(f'{OUT}/plane.json')); n = np.array(pl['n_vp']); H0 = pl['h_vp']
T = json.load(open(f'{OUT}/track2.json'))
R = 0.02
def ray(u, v): r = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return r / np.linalg.norm(r)
def cap(k): return k if k <= 11 else (k + 1 if k <= 35 else k + 2)
res = {}
for rend in ['0039', '0039s']:
    tr = {int(k): v for k, v in T[rend].items()}
    ks = list(range(21, 41)); cs = np.array([cap(k) for k in ks], float)
    U = np.array([tr[k]['cf'][0] for k in ks]); V = np.array([tr[k]['cf'][1] for k in ks]); W = np.array([tr[k]['w'] for k in ks], float)
    # smoothed pixel track (quadratic in capture index)
    pu = np.polyfit(cs, U, 2); pv = np.polyfit(cs, V, 2)
    su = lambda c: np.polyval(pu, c); sv = lambda c: np.polyval(pv, c)
    print(f'=== {rend}: pixel residual sd u {np.std(U - su(cs)):.2f} v {np.std(V - sv(cs)):.2f} px; smooth px cap25 ({su(25):.1f},{sv(25):.1f}) cap26 ({su(26):.1f},{sv(26):.1f})')
    out = {}
    # Route A
    for hf in (0.98, 1.0, 1.02):
        H = H0 * hf
        P = np.array([(H - R) / (n @ ray(u, v)) * ray(u, v) for u, v in zip(U, V)])
        co = [np.polyfit(cs, P[:, j], 2) for j in range(3)]
        vel = lambda c: np.array([np.polyval(np.polyder(co[j]), c) for j in range(3)])
        pos = lambda c: np.array([np.polyval(co[j], c) for j in range(3)])
        lin = [np.polyfit(cs, P[:, j], 1)[0] for j in range(3)]
        vA = np.linalg.norm(vel(25)) * 25 * 100; vfd = np.linalg.norm(pos(26) - pos(25)) * 2500
        vlin = np.linalg.norm(lin) * 2500
        # smooth-track plane points (smoothed pixels)
        Ps = lambda c: (H - R) / (n @ ray(su(c), sv(c))) * ray(su(c), sv(c))
        vsm = np.linalg.norm(Ps(26) - Ps(25)) * 2500
        rr = lambda c: np.linalg.norm(pos(c)) - R
        d37 = np.linalg.norm(pos(37) - pos(25)) * 100; d38 = np.linalg.norm(pos(38) - pos(25)) * 100
        print(f' A h x{hf}: v(25) quad-deriv {vA:.1f}, quad fwd 25->26 {vfd:.1f}, linear-fit speed {vlin:.1f}, smooth-pixel fwd {vsm:.1f} cm/s;'
              f' surface range fit cap25 {rr(25):.4f} cap37 {rr(37):.4f} cap38 {rr(38):.4f}; disp 25->37 {d37:.2f} 25->38 {d38:.2f}; |a| {np.linalg.norm([2*co[j][0] for j in range(3)])*625*100:.1f} cm/s2')
        if hf == 1.0: out['A'] = dict(v_quad=vA, v_fwd=vfd, v_lin=vlin, v_smooth_px=vsm, d37=d37, d38=d38)
    # Route B: stated anchors
    for c15 in (37, 38):
        rs = lambda c: 1.014 + (0.737 - 1.014) * (c - 25) / (c15 - 25)
        # smoothed clicks
        Pb = lambda c: rs(c) * ray(su(c), sv(c))
        vB = np.linalg.norm(Pb(26) - Pb(25)) * 2500
        # raw clicks (video 24 / 25)
        Pr25 = 1.014 * ray(tr[24]['cf'][0], tr[24]['cf'][1]); Pr26 = rs(26) * ray(tr[25]['cf'][0], tr[25]['cf'][1])
        vBr = np.linalg.norm(Pr26 - Pr25) * 2500
        # displacement with stated depths at both ends
        if c15 == 38: p15 = (tr[36]['cf'][0], tr[36]['cf'][1])
        else: p15 = ((tr[35]['cf'][0] + tr[36]['cf'][0]) / 2, (tr[35]['cf'][1] + tr[36]['cf'][1]) / 2)
        dB = np.linalg.norm(0.737 * ray(*p15) - Pr25) * 100
        dBs = np.linalg.norm(0.737 * ray(su(c15), sv(c15)) - 1.014 * ray(su(25), sv(25))) * 100
        print(f' B t1.5=cap{c15}: v fwd smoothed clicks {vB:.1f}, raw clicks {vBr:.1f}; displacement raw clicks {dB:.2f}, smoothed {dBs:.2f}')
        out[f'B{c15}'] = dict(v_smooth=vB, v_raw=vBr, d_raw=dB, d_smooth=dBs)
    # Route C: size-based range
    for c15, k15 in ((38, 36),):
        # centre range = surface + R; w = F*D/rc + b -> fit b from the two anchors (least squares)
        rc25, rc15 = 1.014 + R, 0.737 + R
        b = np.mean([tr[24]['w'] - F * 0.04 / rc25, tr[k15]['w'] - F * 0.04 / rc15])
        rc = lambda w: F * 0.04 / (w - b)
        pw = np.polyfit(cs, W, 2); sw = lambda c: np.polyval(pw, c)
        Pc = np.array([rc(w) * ray(u, v) for u, v, w in zip(U, V, W)])
        co = [np.polyfit(cs, Pc[:, j], 2) for j in range(3)]
        vC = np.linalg.norm([np.polyval(np.polyder(co[j]), 25) for j in range(3)]) * 2500
        Pcs = lambda c: rc(sw(c)) * ray(su(c), sv(c))
        vCs = np.linalg.norm(Pcs(26) - Pcs(25)) * 2500
        lin = [np.polyfit(cs, Pc[:, j], 1)[0] for j in range(3)]
        print(f' C blur b {b:.2f} px: v(25) quad-deriv {vC:.1f}, smooth fwd {vCs:.1f}, linear-fit speed {np.linalg.norm(lin)*2500:.1f}; range at cap25 {rc(sw(25)):.4f} cap26 {rc(sw(26)):.4f}')
        out['C'] = dict(v_quad=vC, v_smooth=vCs)
        # label-style with stated r25 and r26 = 1.014 + (rc(26) - rc(25)) (size-based increment)
        r26 = 1.014 + (rc(sw(26)) - rc(sw(25)))
        vL = np.linalg.norm(r26 * ray(tr[25]['cf'][0], tr[25]['cf'][1]) - 1.014 * ray(tr[24]['cf'][0], tr[24]['cf'][1])) * 2500
        print(f'   label-style (stated r25, size increment to r26 {r26:.4f}, raw clicks) {vL:.1f}')
        out['C']['v_label'] = vL
    res[rend] = out
json.dump(res, open(f'{OUT}/speed.json', 'w'), indent=1)
