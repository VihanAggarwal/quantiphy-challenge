import cv2, numpy as np
def frames(vid, y0=0, y1=None, x0=0, x1=None, n=None):
    c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
    out = []
    while True:
        ok, f = c.read()
        if not ok: break
        out.append(f[y0:y1, x0:x1].copy())
        if n and len(out) >= n: break
    return np.array(out)
