# simulation_0242: template tracking of torsos (frames 0-48), pixel speeds and row positions.
import cv2, numpy as np
cap = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0242.mp4')
fr = []
while True:
    ok, f = cap.read()
    if not ok: break
    fr.append(f)
fr = fr[:49]
boxes = {'brown': (290, 360, 190, 80), 'white': (740, 470, 230, 90), 'rabbit': (1048, 735, 85, 60)}
res = {}
for name, (x, y, w, h) in boxes.items():
    pos = [(x, y)]
    tmpl = fr[0][y:y + h, x:x + w]
    cx, cy = x, y
    for i in range(1, len(fr)):
        sx0, sy0 = max(cx - 40, 0), max(cy - 30, 0)
        sea = fr[i][sy0:cy + h + 30, sx0:cx + w + 40]
        r = cv2.matchTemplate(sea, tmpl, cv2.TM_CCOEFF_NORMED)
        _, mv, _, ml = cv2.minMaxLoc(r)
        # subpixel parabola
        px, py = ml
        dx = 0.0
        if 0 < px < r.shape[1] - 1:
            a, b_, c = r[py, px - 1], r[py, px], r[py, px + 1]; dx = 0.5 * (a - c) / (a - 2 * b_ + c)
        cx, cy = sx0 + px, sy0 + py
        pos.append((cx + dx, cy))
        if i % 12 == 0:  # refresh template to follow pose changes
            tmpl = fr[i][cy:cy + h, cx:cx + w]
    pos = np.array(pos, float)
    t = np.arange(len(pos)) / 24.0
    k, b0 = np.polyfit(t, pos[:, 0], 1)
    res[name] = k
    print(f'{name}: px speed {k:.1f} px/s  x0={pos[0,0]:.0f} x48={pos[-1,0]:.0f}  row range {pos[:,1].min():.0f}-{pos[:,1].max():.0f}')
print('ratio white/brown %.3f rabbit/brown %.3f' % (res['white'] / res['brown'], res['rabbit'] / res['brown']))
