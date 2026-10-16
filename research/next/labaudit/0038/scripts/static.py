"""Static rows of 0038, two routes.
Route A: pixel endpoints back-projected at the stated (ToF) range of the object.
Route B: table plane from the rectified table top (76.0 x 60.3), scale s (1 = geometric; s_tof = ToF/plane ratio);
         base on the plane, heights along the plane normal; widths at the axis depth."""
import numpy as np
F, CX, CY = 711.0, 640.0, 360.0
B = '/home/user/quantiphy-challenge/research/next/labaudit/0038'
pl = np.load(f'{B}/plane.npy'); n, d0 = pl[:3], pl[3]
def ray(u, v):
    r = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return r / np.linalg.norm(r)
def P(u, v, rng): return rng * ray(u, v)
def on(u, v, s=1.0, h=0.0):
    r = ray(u, v); return s * (d0 - h) / (n @ r) * r     # plane n.X = d0 (camera above table: n points down-ish in cam frame)
def up_to(base, u, v):
    a = -n; r = ray(u, v)
    A = np.array([[a @ a, -a @ r], [a @ r, -r @ r]]); b = np.array([-(base @ a), -(base @ r)])
    h, t = np.linalg.solve(A, b); return base + h * a, h
print('plane n', n.round(4), 'd0', round(d0, 4))
# --- credit card on plane
card = dict(BL=(525.8, 533.0), BR=(618.3, 534.7), FR=(619.7, 552.0), FL=(518.3, 549.2))
Pc = {k: on(*v) for k, v in card.items()}
L1 = np.linalg.norm(Pc['BR'] - Pc['BL']); L2 = np.linalg.norm(Pc['FR'] - Pc['FL'])
W1 = np.linalg.norm(Pc['FL'] - Pc['BL']); W2 = np.linalg.norm(Pc['FR'] - Pc['BR'])
print(f'card long edges {L1*100:.2f} {L2*100:.2f} short {W1*100:.2f} {W2*100:.2f} (true 8.56 x 5.40)')
cc = np.mean([Pc[k] for k in Pc], 0); print(f'card centre plane range {np.linalg.norm(cc):.4f} vs stated 0.6867 -> ratio {0.6867/np.linalg.norm(cc):.3f}')
# --- objects (pixels read from zooms of median_x)
bot = dict(top=(665, 330.0), bot=(665, 478.5), L=642.0, R=689.5, rng=0.9998)
cup = dict(top=(759, 375.0), bot=(759, 498.5), L=723.5, R=794.5, rimy=381, rng=0.874)
pok = dict(top=(684, 416.5), botF=(690, 500.0), botB=(672, 495.0), rng=0.9035)
print('\nRoute A (stated range, both endpoints at that range)')
hA = np.linalg.norm(P(*bot['top'], bot['rng']) - P(*bot['bot'], bot['rng'])) * 100
print(f'  bottle height {hA:.2f}')
rimA = np.linalg.norm(P(cup['L'], cup['rimy'], cup['rng']) - P(cup['R'], cup['rimy'], cup['rng'])) * 100
print(f'  cup rim diam {rimA:.2f}   (at axis depth, +4.4cm: {np.linalg.norm(P(cup["L"], cup["rimy"], cup["rng"]+.044) - P(cup["R"], cup["rimy"], cup["rng"]+.044))*100:.2f})')
for nm, b in (('front-card foot', pok['botF']), ('back-card foot', pok['botB']), ('mid', (680, 497.5))):
    print(f'  poker height ({nm}) {np.linalg.norm(P(*pok["top"], pok["rng"]) - P(*b, pok["rng"]))*100:.2f}')
print(f'  cup height {np.linalg.norm(P(*cup["top"], cup["rng"]) - P(*cup["bot"], cup["rng"]))*100:.2f}')
# centre-to-centre, centre clicks at stated ranges
cupc = (759, (375 + 498.5) / 2); botc = (665.5, (330 + 478.5) / 2)
dA = np.linalg.norm(P(*cupc, cup['rng']) - P(*botc, bot['rng'])) * 100
print(f'  cup-bottle distance (centre clicks at stated ranges) {dA:.2f}')
for dv in (-20, 20):
    print(f'     click y shifted {dv:+d}px: {np.linalg.norm(P(cupc[0], cupc[1]+dv, cup["rng"]) - P(botc[0], botc[1]+dv, bot["rng"]))*100:.2f}')
print(f'     add +radius to each range (axis-to-axis): {np.linalg.norm(P(*cupc, cup["rng"]+.042) - P(*botc, bot["rng"]+.034))*100:.2f}')
for s in (1.0, 0.6867 / np.linalg.norm(cc)):
    print(f'\nRoute B (plane, s={s:.3f})')
    bb = on(*bot['bot'], s); _, h = up_to(bb, *bot['top']); print(f'  bottle height {h*100:.2f}  (front-base range {np.linalg.norm(bb):.4f}, stated 0.9998)')
    cb = on(*cup['bot'], s); _, h = up_to(cb, *cup['top']); print(f'  cup height {h*100:.2f}  (front-base range {np.linalg.norm(cb):.4f}, stated 0.874)')
    zax = (cb * (np.linalg.norm(cb) + 0.043) / np.linalg.norm(cb))[2]
    print(f'  cup rim diam at axis Z {zax:.3f}: {(cup["R"]-cup["L"]) / F * zax * 100:.2f};  at front Z {cb[2]:.3f}: {(cup["R"]-cup["L"]) / F * cb[2] * 100:.2f}')
    for nm, b in (('front-card foot', pok['botF']), ('back-card foot', pok['botB']), ('mid', (680, 497.5))):
        pb = on(*b, s); _, h = up_to(pb, *pok['top']); print(f'  poker height ({nm}) {h*100:.2f} (foot range {np.linalg.norm(pb):.4f}, stated 0.9035)')
    # axes: front base point pushed back by radius along horizontal ray direction
    def axis(p, r):
        dirh = p - (p @ n) * n * 0; dirh = p / np.linalg.norm(p); return p + r * dirh
    rb = (bot['R'] - bot['L']) / F * bb[2] / 2
    cbot_w = 64 / F * cb[2] / 2
    A_b = axis(bb, rb); A_c = axis(cb, cbot_w)
    print(f'  bottle radius {rb*100:.2f}, cup base radius {cbot_w*100:.2f}')
    dax = np.linalg.norm(A_b - A_c)
    # centres at mid-height: bottle h/2, cup h/2
    hb = up_to(bb, *bot['top'])[1]; hc = up_to(cb, *cup['top'])[1]
    Cb = A_b - n * hb / 2; Cc = A_c - n * hc / 2
    print(f'  cup-bottle: base axis-to-axis {dax*100:.2f}; centroid-to-centroid {np.linalg.norm(Cb-Cc)*100:.2f}; front-surface mid points {np.linalg.norm((bb - n*hb/2) - (cb - n*hc/2))*100:.2f}')
