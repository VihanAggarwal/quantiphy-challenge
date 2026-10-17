"""Credit card corners -> table plane -> side lengths (checks the f / plane scale against the 85.6 x 53.98 mm prior).
Also f from vanishing-point orthogonality of the table edges."""
import numpy as np, json, cv2
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0039'
CX, CY = 640.0, 360.0
pl = json.load(open(f'{OUT}/plane.json'))
cor = {k: np.array(v) for k, v in pl['corners'].items()}
h = lambda p: np.array([p[0], p[1], 1.0])
v1 = np.cross(np.cross(h(cor['FL']), h(cor['FR'])), np.cross(h(cor['BL']), h(cor['BR']))); v1 = v1[:2] / v1[2]
v2 = np.cross(np.cross(h(cor['FL']), h(cor['BL'])), np.cross(h(cor['FR']), h(cor['BR']))); v2 = v2[:2] / v2[2]
fo = np.sqrt(-np.dot(v1 - [CX, CY], v2 - [CX, CY]))
print('VP1', v1, 'VP2', v2, 'f from VP orthogonality', fo)
med = cv2.imread(f'{OUT}/png/med_0039x.png').astype(float)
g = med.mean(-1)
y0, x0 = 520, 505
roi = g[y0:565, x0:640]
m = (roi < 107).astype(np.uint8)
yel = ((med[y0:565, x0:640, 2] > 140) & (med[y0:565, x0:640, 0] < 130)).astype(np.uint8)
m = cv2.morphologyEx(m | yel, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
n_, lab, st, cen = cv2.connectedComponentsWithStats(m); k = 1 + np.argmax(st[1:, 4]); blob = (lab == k).astype(np.uint8)
blob[st[k, 1] + st[k, 3] - 1:, :] = blob[st[k, 1] + st[k, 3] - 1:, :]
cnt = max(cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0], key=cv2.contourArea)
hull = cv2.convexHull(cnt)
for eps in (2, 3, 4, 6):
    q = cv2.approxPolyDP(hull, eps, True)[:, 0, :].astype(float) + [x0 + 0.5, y0 + 0.5]
    if len(q) == 4: break
print('quad (px)', q.round(1).tolist(), 'blob bbox', st[k, :4] + [x0, y0, 0, 0])
for f in (711.0, 722.0, fo):
    for H in (pl['h_vp'],):
        # plane normal for this f from VPs
        K = np.array([[f, 0, CX], [0, f, CY], [0, 0, 1]])
        d1 = np.linalg.inv(K) @ h(v1); d1 /= np.linalg.norm(d1); d2 = np.linalg.inv(K) @ h(v2); d2 /= np.linalg.norm(d2)
        nn = np.cross(d1, d2); nn /= np.linalg.norm(nn); nn = nn if nn[1] > 0 else -nn
        ray = lambda p: np.linalg.inv(K) @ h(p)
        onp = lambda p, d: d / (nn @ ray(p)) * ray(p)
        hs = [.760 / np.linalg.norm(onp(cor['FL'], 1) - onp(cor['FR'], 1)), .760 / np.linalg.norm(onp(cor['BL'], 1) - onp(cor['BR'], 1)),
              .603 / np.linalg.norm(onp(cor['FL'], 1) - onp(cor['BL'], 1)), .603 / np.linalg.norm(onp(cor['FR'], 1) - onp(cor['BR'], 1))]
        Hm = np.mean(hs)
        Q = [onp(p, Hm) for p in q]
        sides = [np.linalg.norm(Q[i] - Q[(i + 1) % 4]) * 100 for i in range(4)]
        diag = [np.linalg.norm(Q[0] - Q[2]) * 100, np.linalg.norm(Q[1] - Q[3]) * 100]
        cen3 = np.mean(Q, 0)
        print(f'f {f:.1f}: heights {np.round(hs,4)} mean {Hm:.4f}; card sides {np.round(sides,2)} cm, diagonals {np.round(diag,2)} (ID-1: 8.56 x 5.40, diag 10.12); card centre range {np.linalg.norm(cen3):.4f} (stated 0.6867)')
