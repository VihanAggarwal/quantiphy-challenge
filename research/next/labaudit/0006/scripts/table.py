"""Table-top edges in captured_0006 frame 0: column/row profiles of the wood colour, line fits, corners."""
import cv2, numpy as np
D = '/home/user/quantiphy-challenge/research/next/labaudit/0006/'
im = cv2.imread(D + 'frames/0006_f00.png')
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(int)
lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(float)
# wood top: sample a patch in the middle of the top
ref = lab[470:480, 650:700].reshape(-1, 3).mean(0)
dist = np.linalg.norm(lab - ref, axis=2)
R = np.zeros(dist.shape, bool); R[425:522, 370:1000] = True
m = ((dist < 20) & R).astype(np.uint8)
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, l, st, c = cv2.connectedComponentsWithStats(m)
k = 1 + np.argmax(st[1:, 4]); m = (l == k)
print('top blob bbox', st[k])
cv2.imwrite(D + 'tablemask.png', (m * 255).astype(np.uint8))
# back edge: for columns, first row of mask; front edge: last row of top mask (before dark face)
cols = np.arange(st[k][0], st[k][0] + st[k][2])
top = []; bot = []
for x in cols:
    ys = np.where(m[:, x])[0]
    if len(ys) < 3: continue
    top.append((x, ys.min())); bot.append((x, ys.max()))
top = np.array(top); bot = np.array(bot)
rows = np.arange(st[k][1], st[k][1] + st[k][3])
left = []; right = []
for y in rows:
    xs = np.where(m[y])[0]
    if len(xs) < 3: continue
    left.append((xs.min(), y)); right.append((xs.max(), y))
left = np.array(left); right = np.array(right)
def fit(p, xcol=0):
    return np.polyfit(p[:, xcol], p[:, 1 - xcol], 1)
# back edge only on central part
tb = top[(top[:, 0] > 520) & (top[:, 0] < 780)]; pb = fit(tb)
bf = bot[(bot[:, 0] > 430) & (bot[:, 0] < 940)]; pf = fit(bf)
y0, y1 = st[k][1], st[k][1] + st[k][3]
ll = left[(left[:, 1] > y0 + 8) & (left[:, 1] < y1 - 8)]; pl = fit(ll, xcol=1)
rr = right[(right[:, 1] > y0 + 8) & (right[:, 1] < y1 - 8)]; pr = fit(rr, xcol=1)
print('back y=%.4f x+%.2f   front y=%.4f x+%.2f' % (pb[0], pb[1], pf[0], pf[1]))
print('left x=%.4f y+%.2f   right x=%.4f y+%.2f' % (pl[0], pl[1], pr[0], pr[1]))
def inter(ph, pv):  # y=a x+b, x=c y+d
    a, b = ph; c, d = pv
    y = (a * d + b) / (1 - a * c); x = c * y + d; return x, y
C = {'BL': inter(pb, pl), 'BR': inter(pb, pr), 'FR': inter(pf, pr), 'FL': inter(pf, pl)}
for kk, v in C.items(): print(kk, '%.1f %.1f' % v)
np.save(D + 'scripts/corners.npy', np.array([C['BL'], C['BR'], C['FR'], C['FL']]))
