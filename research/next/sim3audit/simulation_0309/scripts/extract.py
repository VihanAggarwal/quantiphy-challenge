import cv2, sys, numpy as np
vids = sys.argv[1].split(',')
idx = [int(x) for x in sys.argv[2].split(',')]
for v in vids:
    c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{v}.mp4')
    i = 0
    while True:
        ok, f = c.read()
        if not ok: break
        if i in idx:
            cv2.imwrite(f'frames/{v}_{i:03d}.png', f)
            small = cv2.resize(f, (f.shape[1]//3, f.shape[0]//3))
            cv2.imwrite(f'frames/{v}_{i:03d}_s.png', small)
        i += 1
