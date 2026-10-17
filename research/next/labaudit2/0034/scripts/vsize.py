"""Vertical extent of each tennis ball in camera a (ax render): top = upper edge of the yellow ball (S>60 & V>90 run),
bottom = dark SAM outline row (min V) just under the ball. Median over the 7 columns around the centroid."""
import cv2, numpy as np, json, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0034/scripts')
from frames import read
O = '/home/user/quantiphy-challenge/research/next/labaudit2/0034/'
def vext(im, cx, cy):
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(int)
    tops, bots = [], []
    for x in range(int(cx) - 3, int(cx) + 4):
        S = hsv[:, x, 1]; V = hsv[:, x, 2]; H = hsv[:, x, 0]
        y0 = int(cy)
        ball = (S > 60) & (V > 90) & (H >= 22) & (H <= 45)
        # top: walk up from centre while ball pixels (allow 2-px gaps)
        y = y0; gap = 0
        while y > y0 - 60:
            if ball[y - 1]: gap = 0
            else:
                gap += 1
                if gap > 2: break
            y -= 1
        top = y + gap
        # bottom: darkest row in [y0+20, y0+50] (SAM outline), refined to the first row with V<45 going down
        seg = V[y0 + 20:y0 + 50]
        yb = y0 + 20 + int(np.argmin(seg))
        tops.append(top); bots.append(yb)
    return float(np.median(tops)), float(np.median(bots))
if __name__ == '__main__':
    X = read('ax'); T = json.load(open(O + 'track_ax.json'))
    res = {'L': [], 'R': []}
    for i in range(len(X)):
        row = [i]
        for b in 'LR':
            d = T[b][i]; t, bt = vext(X[i], d['cx'], d['cy'])
            res[b].append(dict(f=i, top=t, bot=bt, h=bt - t, cx=d['cx'], cy=d['cy'], mid=(t + bt) / 2))
            row += [b, round(d['cx'], 1), t, bt, bt - t]
        print(*row)
    json.dump(res, open(O + 'vsize_ax.json', 'w'))
