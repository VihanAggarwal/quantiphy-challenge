"""Locate moving blobs per frame against a median background. usage: motion.py video_id [thresh]"""
import sys, cv2, numpy as np
vid = sys.argv[1]; th = float(sys.argv[2]) if len(sys.argv) > 2 else 25
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr = []
while True:
    ok, f = c.read()
    if not ok: break
    fr.append(cv2.resize(f, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA).astype(np.int16))
fr = np.array(fr)
bg = np.median(fr[::2], axis=0)
for i in range(0, len(fr), 3):
    d = np.abs(fr[i] - bg).max(axis=2)
    m = (d > th).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    blobs = sorted([(st[k, 4], k) for k in range(1, n)], reverse=True)[:4]
    print(i, [(int(a), tuple(int(v)*2 for v in st[k, :4])) for a, k in blobs])
