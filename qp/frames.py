"""Sample frames from a video and encode them for a VLM request."""

from __future__ import annotations

import base64
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class Frame:
    index: int
    time_s: float
    jpeg_b64: str
    width: int
    height: int


def _draw_grid(img: np.ndarray, step: int) -> np.ndarray:
    """Overlay a light pixel-coordinate grid so the model can read off positions."""
    out = img.copy()
    h, w = out.shape[:2]
    for x in range(0, w, step):
        cv2.line(out, (x, 0), (x, h - 1), (0, 255, 255), 1)
        cv2.putText(out, str(x), (x + 2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)
    for y in range(0, h, step):
        cv2.line(out, (0, y), (w - 1, y), (0, 255, 255), 1)
        cv2.putText(out, str(y), (2, y + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)
    return cv2.addWeighted(out, 0.6, img, 0.4, 0)


def sample_frames(path: str, n: int = 16, fps: float | None = None,
                  grid: int = 0, max_side: int = 1024, quality: int = 85) -> list[Frame]:
    """`n` frames evenly spaced over the whole clip (all frames if the clip is shorter).

    Timestamps use the dataset's fps when given (the container fps can be wrong).
    Pixel coordinates in the grid refer to the *resized* frame that is sent.
    """
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise FileNotFoundError(path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = fps or cap.get(cv2.CAP_PROP_FPS) or 30.0
    idxs = sorted(set(np.linspace(0, max(total - 1, 0), num=min(n, max(total, 1))).round().astype(int)))
    frames: list[Frame] = []
    for i in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i))
        ok, img = cap.read()
        if not ok:
            continue
        h, w = img.shape[:2]
        scale = min(1.0, max_side / max(h, w))
        if scale < 1.0:
            img = cv2.resize(img, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)
        if grid:
            img = _draw_grid(img, grid)
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
        frames.append(Frame(int(i), i / fps, base64.b64encode(buf).decode(), img.shape[1], img.shape[0]))
    cap.release()
    if not frames:
        raise RuntimeError(f"no frames decoded from {path}")
    return frames


def video_duration(path: str, fps: float | None = None) -> float:
    cap = cv2.VideoCapture(path)
    total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = fps or cap.get(cv2.CAP_PROP_FPS) or 30.0
    cap.release()
    return total / fps
