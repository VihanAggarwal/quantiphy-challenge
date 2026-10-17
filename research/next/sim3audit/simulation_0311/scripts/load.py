import cv2, numpy as np
def load(vid, gray=False, scale=1.0):
    cap = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_%s.mp4' % vid)
    fr = []
    while True:
        ok, f = cap.read()
        if not ok: break
        if scale != 1.0: f = cv2.resize(f, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        if gray: f = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        fr.append(f)
    return fr
