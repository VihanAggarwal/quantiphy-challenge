"""Second route: same quantities from independent segmentations (original 'a' render and 's' render hue tracks),
lateral (constant stated range) and with the ax size-based range; plus template-matching steps on the original."""
import json, sys, numpy as np, cv2
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0034/scripts')
from geom import ray, R_BALL
from labelstyle import cap, smooth_size, STATED
from frames import read
O = '/home/user/quantiphy-challenge/research/next/labaudit2/0034/'
f = 711
def pts(v, b, route):
    T = json.load(open(O + f'track_{v}.json'))[b]
    uv = np.array([[d['cx'], d['cy']] for d in T]); n = len(uv)
    rc = np.full(n, STATED[b] + R_BALL)
    if route == 'S':
        hs = smooth_size(b); rc = rc * hs[29] / hs
    rays = np.array([ray(u, w, f) for u, w in uv])
    return uv, rays * (rc - R_BALL)[:, None]
for v in ('ax', 'as', 'a'):
    for b in 'LR':
        for route in ('C', 'S'):
            uv, S = pts(v, b, route)
            v12 = np.linalg.norm(S[30] - S[29]) * 25 * 100
            st = 21
            if route == 'S':      # freeze the size-based range before motion onset (rest-phase size noise from the hand)
                S[:st] = S[:st] / np.linalg.norm(S[:st], axis=1)[:, None] * np.linalg.norm(S[st])
            seg = np.linalg.norm(np.diff(S, axis=0), axis=1) * 100
            print(f'{v:3s} {b} {route}: step29->30 {uv[30,0]-uv[29,0]:+.1f}px v1.2 {v12:5.1f} | path from video {st}: {seg[st:].sum():5.1f} (fwd to 37: {seg[st:37].sum():5.1f}, after: {seg[37:].sum():4.1f}) | all {seg.sum():5.1f}')
# template matching on the original render for the 29->30 steps (patch from frame 29 / 30, horizontal search)
A = read('a')
for b, (cx, cy) in (('L', (349.7, 482.6)), ('R', (830.7, 482.3))):
    for k in (28, 29, 30, 31):
        T = json.load(open(O + 'track_a.json'))[b]
        x0, y0 = int(T[k]['cx']), int(T[k]['cy'])
        tpl = A[k][y0 - 25:y0 + 25, x0 - 25:x0 + 25]
        x1 = int(T[k + 1]['cx']); y1 = int(T[k + 1]['cy'])
        win = A[k + 1][y1 - 45:y1 + 45, x1 - 60:x1 + 60]
        r = cv2.matchTemplate(win, tpl, cv2.TM_CCOEFF_NORMED); _, mx, _, loc = cv2.minMaxLoc(r)
        nx = x1 - 60 + loc[0] + 25; ny = y1 - 45 + loc[1] + 25
        print(f'template {b} {k}->{k+1}: dx {nx - x0:+d} dy {ny - y0:+d} (score {mx:.2f}); centroid dx {T[k+1]["cx"]-T[k]["cx"]:+.1f}')
