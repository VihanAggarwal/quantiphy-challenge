"""Simple dark/colour-blob tracker for a ball on a plain background, to check time bases.
usage: balltrack.py video x0 y0 [radius_px] -> per-frame centre (full-res px), via template matching."""
import sys, cv2, numpy as np
vid, x0, y0 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
f0 = int(sys.argv[4]) if len(sys.argv) > 4 else 0
R = int(sys.argv[5]) if len(sys.argv) > 5 else 40
cap = cv2.VideoCapture(f'data/QuantiPhy/{vid}.mp4')
frames = []
while True:
    ok, im = cap.read()
    if not ok: break
    frames.append(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32))
bg = np.median(np.stack(frames[::max(1, len(frames)//15)]), axis=0)
x, y = x0, y0
for i in range(f0, len(frames)):
    d = np.abs(frames[i] - bg)
    d = cv2.GaussianBlur(d, (0, 0), 3)
    H, W = d.shape
    xs, ys = int(max(0, x - 4*R)), int(max(0, y - 4*R)); xe, ye = int(min(W, x + 4*R)), int(min(H, y + 6*R))
    sub = d[ys:ye, xs:xe]
    m = sub > max(20, 0.5 * sub.max())
    n, lab, st, cen = cv2.connectedComponentsWithStats(m.astype(np.uint8))
    if n < 2: print(i, 'lost'); continue
    k = 1 + np.argmax(st[1:, 4])
    cx, cy = cen[k][0] + xs, cen[k][1] + ys
    bw, bh = st[k][2], st[k][3]
    print(i, round(cx, 1), round(cy, 1), bw, bh, round(sub.max(), 1))
    x, y = cx, cy
