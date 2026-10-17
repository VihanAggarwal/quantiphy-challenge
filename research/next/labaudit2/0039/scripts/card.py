"""Credit card (prior 85.6 mm) as a scale check: corners from the x-render median, ranges from the table plane."""
import numpy as np, json, cv2
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0039'
F, CX, CY = 711.0, 640.0, 360.0
pl = json.load(open(f'{OUT}/plane.json')); n = np.array(pl['n_vp']); H = pl['h_vp']
def ray(u, v): return np.array([(u - CX) / F, (v - CY) / F, 1.0])
def onp(u, v, h=H): r = ray(u, v); return h / (n @ r) * r
med = cv2.imread(f'{OUT}/png/med_0039x.png').astype(float)
# dark-blue card mask: B channel > R channel + 15 and V < 120 within the region
roi = med[525:560, 505:635]
b, g, r = roi[..., 0], roi[..., 1], roi[..., 2]
m = ((b > r + 10) & (roi.mean(-1) < 110)) | ((r > 150) & (g > 150) & (b < 120))  # blue body or yellow sticker
m = m.astype(np.uint8)
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
n_, lab, st, cen = cv2.connectedComponentsWithStats(m); k = 1 + np.argmax(st[1:, 4]); blob = (lab == k).astype(np.uint8)
cnt = max(cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0], key=cv2.contourArea)
poly = cv2.approxPolyDP(cnt, 2.0, True)[:, 0, :] + [505, 525]
print('card polygon', poly.tolist())
rect = cv2.minAreaRect(cnt.astype(np.float32)); print('minAreaRect', rect)
ys, xs = np.nonzero(blob); print('x extent', xs.min() + 505, xs.max() + 505, 'y extent', ys.min() + 525, ys.max() + 525, 'centre', xs.mean() + 505, ys.mean() + 525)
# extreme points: leftmost, rightmost
pts = cnt[:, 0, :] + [505, 525]
L = pts[pts[:, 0] == pts[:, 0].min()].mean(0); Rr = pts[pts[:, 0] == pts[:, 0].max()].mean(0)
for hf in (0.98, 1.0, 1.02):
    PL, PR = onp(*L, H * hf), onp(*Rr, H * hf); C = onp(xs.mean() + 505, ys.mean() + 525, H * hf)
    print(f'h x{hf}: left {L} right {Rr}: plane length {np.linalg.norm(PL-PR)*100:.2f} cm; centre range {np.linalg.norm(C):.4f}')
cr = 0.6867
print('stated-range route: length =', (Rr[0] - L[0]) * cr / F * 100, 'cm  (needs range', 0.0856 * F / (Rr[0] - L[0]), ')')
