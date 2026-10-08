"""Synthetic scenes for geometry / CV tests: true metric motion -> RoleTracks (+ optional mp4).

Camera frame: x right, y down, z forward (metres); pinhole camera with the principal point at
the image centre. A 2D scene is a 3D scene whose objects stay at one depth. Each Body carries
a fronto-parallel segment of length `size` centred on its position (its measured extent);
boxes and rendered discs treat the body as a ball of diameter `size`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import numpy as np

from qp.spec import DepthEntry, Obs, RoleTrack

Vec = Callable[[float], np.ndarray]


@dataclass
class Camera:
    width: int = 854
    height: int = 480
    fov_deg: float = 60.0               # horizontal field of view

    @property
    def f(self) -> float:
        return (self.width / 2) / math.tan(math.radians(self.fov_deg) / 2)

    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)

    def project(self, P) -> np.ndarray:
        P = np.atleast_2d(np.asarray(P, float))
        return np.column_stack([self.f * P[:, 0] / P[:, 2] + self.width / 2,
                                self.f * P[:, 1] / P[:, 2] + self.height / 2])


@dataclass
class Body:
    name: str
    pos: Vec                            # metric position at time t (camera frame)
    size: float = 0.5                   # metres
    angle: float = 0.0                  # extent direction in the image plane (0 = horizontal)
    color: tuple[int, int, int] = (0, 0, 255)   # BGR, for render_video

    def vel(self, t: float, h: float = 1e-4) -> np.ndarray:
        return (self.pos(t + h) - self.pos(t - h)) / (2 * h)

    def acc(self, t: float, h: float = 1e-3) -> np.ndarray:
        return (self.pos(t + h) - 2 * self.pos(t) + self.pos(t - h)) / h ** 2

    def range(self, t: float) -> float:
        return float(np.linalg.norm(self.pos(t)))

    def speed(self, t: float) -> float:
        return float(np.linalg.norm(self.vel(t)))

    def mean_speed(self, t0: float, t1: float, n: int = 2001) -> float:
        return float(np.mean([self.speed(t) for t in np.linspace(t0, t1, n)]))


def static(p) -> Vec:
    p = np.asarray(p, float)
    return lambda t: p.copy()


def ballistic(p0, v0=(0, 0, 0), a=(0, 0, 0)) -> Vec:
    """p0 + v0 t + a t^2 / 2 (linear motion when a = 0; gravity is a = (0, 9.8, 0))."""
    p0, v0, a = (np.asarray(x, float) for x in (p0, v0, a))
    return lambda t: p0 + v0 * t + 0.5 * a * t * t


def circular(centre, radius: float, omega: float, phase: float = 0.0) -> Vec:
    """Uniform circle in the fronto-parallel plane z = centre[2]."""
    c = np.asarray(centre, float)
    return lambda t: c + radius * np.array([math.cos(omega * t + phase), math.sin(omega * t + phase), 0.0])


def frame_times(duration: float, fps: float) -> np.ndarray:
    return np.arange(int(round(duration * fps))) / fps


def track(body: Body, role: str, times, cam: Camera, noise_px: float = 0.0, seed: int = 0,
          point: bool = True, extent: bool = True, box: bool = False, source: str = "synth") -> RoleTrack:
    """RoleTrack of `body` at `times` with optional Gaussian pixel noise on every coordinate."""
    rng = np.random.default_rng(seed)
    d = 0.5 * body.size * np.array([math.cos(body.angle), math.sin(body.angle), 0.0])
    obs = []
    for t in np.asarray(times, float):
        P = body.pos(t)
        uv = cam.project(P)[0]
        ends = cam.project([P - d, P + d])
        half = cam.f * body.size / P[2] / 2
        jit = lambda n: rng.normal(0.0, noise_px, n) if noise_px else np.zeros(n)  # noqa: E731
        obs.append(Obs(
            t=float(t),
            point=(uv + jit(2)).tolist() if point else None,
            extent=(ends + jit(4).reshape(2, 2)).tolist() if extent else None,
            box=(np.r_[uv - half, uv + half] + jit(4)).tolist() if box else None,
        ))
    return RoleTrack(role=role, object=body.name, obs=obs, source=source)


def depth_entries(body: Body, times=None, name: str | None = None) -> list[DepthEntry]:
    """Euclidean camera range of `body` at `times` (None: one untimed entry, range at t=0)."""
    name = name or body.name.replace(" ", "_")
    if times is None:
        return [DepthEntry(object=name, distance_m=body.range(0.0))]
    return [DepthEntry(object=name, distance_m=body.range(float(t)), time=float(t)) for t in times]


def render_video(path: str, bodies: list[Body], cam: Camera, duration: float, fps: float,
                 background: tuple[int, int, int] = (40, 40, 40)) -> int:
    """Write an mp4 with each body drawn as a filled disc of its projected diameter; returns
    the number of frames. Frame i is at t = i / fps (match track(..., frame_times(...)))."""
    import cv2

    writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), fps, cam.size)
    if not writer.isOpened():
        raise RuntimeError(f"cannot open video writer for {path}")
    times = frame_times(duration, fps)
    for t in times:
        img = np.full((cam.height, cam.width, 3), background, np.uint8)
        for b in sorted(bodies, key=lambda b: -b.pos(t)[2]):  # far first
            P = b.pos(t)
            u, v = cam.project(P)[0]
            r = max(1, int(round(cam.f * b.size / P[2] / 2)))
            cv2.circle(img, (int(round(u)), int(round(v))), r, b.color, -1, lineType=cv2.LINE_AA)
        writer.write(img)
    writer.release()
    return len(times)
