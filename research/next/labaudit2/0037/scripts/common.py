"""Common helpers for the 0037 round-2 audit. Frames are read in memory from the mp4 (nothing dumped)."""
import cv2, numpy as np
F, CX, CY = 711.0, 640.0, 360.0
VID = '/home/user/quantiphy-challenge/data/QuantiPhy/captured_0037%s.mp4'
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0037'


def frames(r):
    """r in ('', 's', 'x') -> list of BGR frames"""
    cap = cv2.VideoCapture(VID % r)
    out = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        out.append(f)
    return out


def ray(u, v, f=F):
    r = np.array([(u - CX) / f, (v - CY) / f, 1.0])
    return r / np.linalg.norm(r)


def cap(n, drops=(12, 36)):
    """video frame -> capture frame (25 fps): one capture frame dropped before each video index in drops"""
    return n + sum(n >= d for d in drops)
