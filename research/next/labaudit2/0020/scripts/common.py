# Shared helpers for the round 2 audit of family 0020 (frames are read in memory, never dumped)
import cv2, numpy as np, json, os
ROOT = '/home/user/quantiphy-challenge'
D = ROOT + '/research/next/labaudit2/0020/'
VID = {'o': ROOT + '/data/QuantiPhy/captured_0020.mp4',
       's': ROOT + '/data/QuantiPhy/captured_0020s.mp4',
       'x': ROOT + '/data/QuantiPhy/captured_0020x.mp4'}
F = 711.0
CX, CY = 640.0, 360.0
R_JAR = 1.9735   # stated range at t=0.60 s (surface at click)
R_TOY = 2.6300
R_NEAR = 1.58
R_FAR = 3.237

_cache = {}
def frames(r):
    if r in _cache: return _cache[r]
    cap = cv2.VideoCapture(VID[r]); out = []
    while True:
        ok, im = cap.read()
        if not ok: break
        out.append(im)
    _cache[r] = out
    return out

def cap_index(k, drops=(12, 36)):
    """video frame k -> capture frame index (25 fps clock); drops = first video frame after each dropped capture frame"""
    k = np.asarray(k)
    c = k.copy().astype(float)
    for d in drops: c = c + (k >= d)
    return c

def tau(k, drops=(12, 36)):
    return cap_index(k, drops) / 25.0

def ray(u, v, f=F):
    d = np.array([(u - CX) / f, (v - CY) / f, 1.0])
    return d / np.linalg.norm(d)

def backproject(u, v, rng, f=F):
    return rng * ray(u, v, f)

def project(P, f=F):
    P = np.atleast_2d(P)
    return np.c_[f * P[:, 0] / P[:, 2] + CX, f * P[:, 1] / P[:, 2] + CY]
