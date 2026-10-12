"""Minimal label-procedure emulator for lab distances: a clicked pixel (u, v) and the depth read there are
back-projected with the fixed lab camera (principal point at the image centre, f from qp.claude_annotate.LAB_FOV_DEG,
depth read as Euclidean range like qp.geometry.DEPTH_IS_RANGE; z=True reads it as optical-axis Z instead), and the
label is the Euclidean distance between the two 3D points."""
import math
import numpy as np
from qp import claude_annotate as ca

W, H = 1280, 720


def f_px(width=W, fov=ca.LAB_FOV_DEG):
    return width / 2 / math.tan(math.radians(fov) / 2)


def point(u, v, depth, f=None, z=False, width=W, height=H):
    f = f or f_px(width)
    ray = np.array([(u - width / 2) / f, (v - height / 2) / f, 1.0])
    return depth * ray if z else depth * ray / np.linalg.norm(ray)


def dist(a, b, **kw):
    return float(np.linalg.norm(point(*a, **kw) - point(*b, **kw)))
