"""Pinhole helpers for the fixed lab camera (1280x720)."""
import numpy as np
CX, CY = 640.0, 360.0

def ray(u, v, f=711.0):
    d = np.array([(u - CX) / f, (v - CY) / f, 1.0])
    return d / np.linalg.norm(d)

def P(u, v, r, f=711.0, conv='range'):
    d = np.array([(u - CX) / f, (v - CY) / f, 1.0])
    if conv == 'range':
        return r * d / np.linalg.norm(d)
    return r * d  # r is Z

def dist(a, b):
    return float(np.linalg.norm(np.asarray(a) - np.asarray(b)))
