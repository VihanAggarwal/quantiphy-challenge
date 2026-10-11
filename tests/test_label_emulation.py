"""Blender label emulation in qp.geometry (solve(label_emulation=True); off by default).

Simulation labels: speed s_i = |p_i - p_{i-1}| * fps at frame i = round(t * fps), acceleration
(s_i - s_{i-1}) * fps (backward difference of the speed magnitude, scored as its absolute value)."""
import math

import numpy as np
import pytest

from qp import geometry as G
from qp.geometry import solve
from qp.spec import Quantity, QuestionSpec
from synth import Body, Camera, ballistic, depth_entries, frame_times, static, track

CAM = Camera()
FPS = 30.0
T = frame_times(3.0, FPS)
Z = 10.0
PERSON = Body("person", static([1.0, 0.5, Z]), size=1.8, angle=math.pi / 2)
CAR = Body("car", static([-2.0, 1.0, Z]), size=4.5)
HEIGHT = Quantity(kind="size", objects=["person"], dimension="height", value_si=1.8)
# from rest along x: the backward difference lags the instantaneous speed by half a frame
SLED = Body("sled", ballistic([-4.0, 1.0, Z], [0.0, 0.0, 0.0], [2.0, 0.0, 0.0]), size=0.5)
# projectile: the label's acceleration is tangential, far below g near the apex
BALL = Body("ball", ballistic([-3.0, -1.0, Z], [2.0, -4.0, 0.0], [0.0, 9.8, 0.0]), size=0.22)


def label_speed(body: Body, t: float, fps: float = FPS) -> float:
    i = round(t * fps)
    return float(np.linalg.norm(body.pos(i / fps) - body.pos((i - 1) / fps)) * fps)


def label_accel(body: Body, t: float, fps: float = FPS) -> float:
    i = round(t * fps)
    return abs(label_speed(body, i / fps, fps) - label_speed(body, (i - 1) / fps, fps)) * fps


def spec(target, prior, depth=(), is_3d=False):
    return QuestionSpec(qid=3, target=target, prior=prior, depth=list(depth), is_3d=is_3d)


def rel(a, b):
    return abs(a - b) / abs(b)


def both(sp, tracks):
    off = solve(sp, tracks, CAM.size, FPS)
    on = solve(sp, tracks, CAM.size, FPS, label_emulation=True)
    return off, on


def test_default_is_off():
    assert G.LABEL_EMULATION is False
    sp = spec(Quantity("speed", ["sled"], time=0.5, unit="m/s"), HEIGHT)
    tracks = [track(PERSON, "prior", T, CAM), track(SLED, "target", T, CAM)]
    default = solve(sp, tracks, CAM.size, FPS)
    off = solve(sp, tracks, CAM.size, FPS, label_emulation=False)
    assert default.value == off.value and "label_emulated" not in default.flags
    assert rel(default.value, SLED.speed(0.5)) < 0.005   # instantaneous, unchanged


def test_speed_target_backward_difference():
    sp = spec(Quantity("speed", ["sled"], time=0.5, unit="m/s"), HEIGHT)
    off, on = both(sp, [track(PERSON, "prior", T, CAM), track(SLED, "target", T, CAM)])
    label = label_speed(SLED, 0.5)                     # 2 * (0.5 - 1/60) = 0.967 m/s
    assert rel(label, SLED.speed(0.5)) > 0.03          # the convention matters here (3.3%)
    assert "label_emulated" in on.flags and rel(on.value, label) < 0.002, (on.value, label)
    assert rel(off.value, SLED.speed(0.5)) < 0.002


def test_speed_frame_is_rounded():
    # t = 0.51 s at 30 fps is frame 15 (t = 0.5 s): the label belongs to that frame
    sp = spec(Quantity("speed", ["sled"], time=0.51, unit="m/s"), HEIGHT)
    _, on = both(sp, [track(PERSON, "prior", T, CAM), track(SLED, "target", T, CAM)])
    assert rel(on.value, label_speed(SLED, 0.5)) < 0.002


def test_speed_at_first_frame_keeps_instantaneous():
    moving = Body("puck", ballistic([-3.0, 1.0, Z], [1.5, 0.0, 0.0], [1.0, 0.0, 0.0]), size=0.3)
    sp = spec(Quantity("speed", ["puck"], time=0.0, unit="m/s"), HEIGHT)
    off, on = both(sp, [track(PERSON, "prior", T, CAM), track(moving, "target", T, CAM)])
    assert "label_emulated" not in on.flags and on.value == pytest.approx(off.value)


def test_speed_prior_scales_the_clip():
    # the stated prior is the label (backward difference): with emulation a static target comes out exact
    sp = spec(Quantity("size", ["car"], dimension="length", unit="m"),
              Quantity("speed", ["sled"], time=0.5, value_si=label_speed(SLED, 0.5)))
    off, on = both(sp, [track(SLED, "prior", T, CAM), track(CAR, "target", T, CAM)])
    assert rel(on.value, 4.5) < 0.003, on.value
    assert off.value < 4.5 * 0.975                     # instantaneous prior: every answer ~3% low


def test_acceleration_is_tangential():
    t = 0.55                                           # shortly after the apex (0.41 s)
    sp = spec(Quantity("acceleration", ["ball"], time=t, unit="m/s^2"), HEIGHT)
    off, on = both(sp, [track(PERSON, "prior", T, CAM), track(BALL, "target", T, CAM)])
    label = label_accel(BALL, t)
    assert label < 0.75 * 9.8
    assert rel(off.value, 9.8) < 0.005
    assert "label_emulated" in on.flags and rel(on.value, label) < 0.01, (on.value, label)


def test_acceleration_straight_line_unchanged():
    sp = spec(Quantity("acceleration", ["sled"], time=1.0, unit="m/s^2"), HEIGHT)
    off, on = both(sp, [track(PERSON, "prior", T, CAM), track(SLED, "target", T, CAM)])
    assert rel(on.value, 2.0) < 0.003 and rel(off.value, 2.0) < 0.003


def test_acceleration_tangential_too_small_keeps_norm():
    t = round(0.4082 * FPS) / FPS                     # at the apex the label's acceleration is ~0
    sp = spec(Quantity("acceleration", ["ball"], time=t, unit="m/s^2"), HEIGHT)
    off, on = both(sp, [track(PERSON, "prior", T, CAM), track(BALL, "target", T, CAM)])
    assert "label_emu_tangential_small" in on.flags and on.value == pytest.approx(off.value)


def test_untimed_quantities_unchanged():
    tracks = [track(PERSON, "prior", T, CAM), track(BALL, "target", T, CAM), track(SLED, "target2", T, CAM)]
    for q in (Quantity("speed", ["ball"], unit="m/s"), Quantity("speed", ["ball"], window=[0.5, 1.5], unit="m/s"),
              Quantity("acceleration", ["ball"], unit="m/s^2"), Quantity("displacement", ["ball"], window=[0.2, 1.0])):
        off, on = both(spec(q, HEIGHT), tracks)
        assert on.value == pytest.approx(off.value) and "label_emulated" not in on.flags, q


def test_3d_speed_backward_difference():
    p3 = Body("person", static([1.0, 0.6, 12.0]), size=1.8, angle=math.pi / 2)
    car = Body("car", ballistic([-3.0, 1.0, 12.0], [1.0, 0.0, 2.0], [1.0, 0.0, 4.0]), size=4.5)
    dt = np.round(np.arange(0.0, 3.01, 0.1), 3)
    depth = depth_entries(p3, name="human") + depth_entries(car, dt)
    sp = spec(Quantity("speed", ["car"], time=0.3, unit="m/s"), HEIGHT, depth, is_3d=True)
    off, on = both(sp, [track(p3, "prior", T, CAM), track(car, "target", T, CAM)])
    label = label_speed(car, 0.3)
    assert rel(label, car.speed(0.3)) > 0.015
    assert rel(on.value, label) < 0.005 and rel(off.value, car.speed(0.3)) < 0.005, (on.value, off.value, label)
