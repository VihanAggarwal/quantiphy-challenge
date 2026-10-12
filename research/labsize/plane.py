"""Table plane per view: orientation from the rectified table top (rect + corners), scale from depth_info
anchors (each anchor alone, so their spread shows how consistent the depth readings are), then metric
lengths of segments lying on the plane (ray-plane intersection). Test inputs only."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import rect  # noqa: E402
from corners import frame, refine, table_mask  # noqa: E402

C = (640.0, 360.0)


def table_plane(video, rough, front, f):
    fr = frame(video)
    m = table_mask(fr)
    cr, _, st = refine(fr, m, rough, front=front)
    X = rect.parallelogram(cr, f, C)
    n = np.cross(X[1] - X[0], X[3] - X[0])
    n /= np.linalg.norm(n)
    if n @ X[0] > 0:
        n = -n  # normal toward the camera (up for a table seen from above)
    return cr, X, n


def unit_ray(uv, f):
    d = rect.rays(np.atleast_2d(uv), f, C)
    return d / np.linalg.norm(d, axis=1, keepdims=True)


def anchor_scale(X, n, uv, r, f, h=0.0, R=0.0):
    """Scale of the unit-scale plane X so that the anchor (pixel uv at range r; a ball: front-surface range,
    centre R further and R above the plane; else a point h above the plane) lies on it."""
    d = unit_ray(uv, f)[0]
    P = (r + R) * d
    return float((n @ P - (R if R else h)) / (n @ X[0]))


def on_plane(uv, X, n, s, f):
    """3D points (camera frame) where the rays through pixels uv meet the plane at scale s."""
    d = rect.rays(np.atleast_2d(uv), f, C)
    k = s * (n @ X[0]) / (d @ n)
    return d * k[:, None]


def seg_len(a, b, X, n, s, f):
    P = on_plane([a, b], X, n, s, f)
    return float(np.linalg.norm(P[1] - P[0]))
