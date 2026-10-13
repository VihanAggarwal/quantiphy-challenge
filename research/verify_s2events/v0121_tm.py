"""Verifier: sub-pixel template tracking of the left ball in the ORIGINAL simulation_0121 after the collision.
Template = left-ball patch at frame 34 (ball separated); NCC search in frames 26-45; parabolic sub-pixel peak."""
import cv2, numpy as np
ROOT = "/home/user/quantiphy-challenge"
SC = 0.012355324074074069
cap = cv2.VideoCapture(f"{ROOT}/data/QuantiPhy/simulation_0121.mp4"); fr = []
while True:
    ok, im = cap.read()
    if not ok: break
    fr.append(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32))
# left ball at f34 roughly x 551-714, y 702-868 (segmented twin bbox); take the left half to avoid the middle ball contact
x0, x1, y0, y1 = 545, 640, 700, 870
tpl = fr[34][y0:y1, x0:x1]
xs = []
for i in range(24, 46):
    win = fr[i][y0 - 10:y1 + 10, x0 - 60:x1 + 40]
    r = cv2.matchTemplate(win, tpl, cv2.TM_CCOEFF_NORMED)
    _, mx, _, loc = cv2.minMaxLoc(r)
    px, py = loc
    dx = 0.0
    if 0 < px < r.shape[1] - 1:
        a, b, c = r[py, px - 1], r[py, px], r[py, px + 1]
        dx = 0.5 * (a - c) / (a - 2 * b + c)
    xs.append((i, px + dx + x0 - 60, mx))
xs = np.array(xs)
for (i, x, m), prev in zip(xs[1:], xs[:-1]):
    print(f"f{int(i):2d} t={i/30:.3f} x={x:8.2f} ncc={m:.3f} backward v={(x - prev[1]) * 30 * SC:+.3f} m/s")
post = xs[(xs[:, 0] >= 29) & (xs[:, 0] <= 40)]
sl = np.polyfit(post[:, 0] / 30, post[:, 1], 1)[0]
print("linear fit frames 29-40:", round(sl, 2), "px/s =", round(abs(sl) * SC, 3), "m/s")
