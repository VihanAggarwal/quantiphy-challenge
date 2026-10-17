"""Shared helpers for the 0038 round-2 audit: frame loading (in memory only), camera model."""
import cv2, numpy as np
ROOT = '/home/user/quantiphy-challenge'
B = f'{ROOT}/research/next/labaudit2/0038'
VID = {'o': f'{ROOT}/data/QuantiPhy/captured_0038.mp4', 's': f'{ROOT}/data/QuantiPhy/captured_0038s.mp4',
       'x': f'{ROOT}/data/QuantiPhy/captured_0038x.mp4'}
F, CX, CY = 711.0, 640.0, 360.0

def frames(tag):
    c = cv2.VideoCapture(VID[tag]); out = []
    while True:
        ok, f = c.read()
        if not ok: break
        out.append(f)
    return np.array(out)

def ray(u, v):
    r = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return r / np.linalg.norm(r)

def cap_of_video(k):
    """video frame -> 25 fps capture frame (drops after video frames 11 and 35)."""
    return k + (k >= 12) + (k >= 36)
