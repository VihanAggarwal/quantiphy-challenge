"""Shared helpers for the 0022 round-2 audit: frames read in memory only, camera model, capture clock."""
import cv2, numpy as np
ROOT = '/home/user/quantiphy-challenge'
B = f'{ROOT}/research/next/labaudit2/0022'
VID = {'o': f'{ROOT}/data/QuantiPhy/captured_0022.mp4', 's': f'{ROOT}/data/QuantiPhy/captured_0022s.mp4',
       'x': f'{ROOT}/data/QuantiPhy/captured_0022x.mp4'}
F, CX, CY = 711.0, 640.0, 360.0

def frames(tag):
    c = cv2.VideoCapture(VID[tag]); out = []
    while True:
        ok, f = c.read()
        if not ok: break
        out.append(f)
    return np.array(out)

def ray(u, v, f=F):
    r = np.array([(u - CX) / f, (v - CY) / f, 1.0]); return r / np.linalg.norm(r)

def cap_of_video(k, drop12=True):
    """video frame -> 25 fps capture frame (drops after video frames 11 and 35)."""
    k = np.asarray(k)
    return k + ((k >= 12) if drop12 else 0) + (k >= 36)
