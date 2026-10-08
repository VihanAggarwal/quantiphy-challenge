import math

import numpy as np
import pytest

from qp.geometry import match_depth, name_score, solve
from qp.spec import DepthEntry, Obs, Quantity, QuestionSpec, RoleTrack
from synth import (Body, Camera, ballistic, circular, depth_entries, frame_times, render_video,
                   static, track)

CAM = Camera()
FPS = 30.0
T = frame_times(3.0, FPS)
DT = np.round(np.arange(0.0, 3.01, 0.1), 3)   # dense depth_info times for exact 3D tests


def Q(kind, objs, **kw):
    return Quantity(kind=kind, objects=list(objs), **kw)


def spec(target, prior, depth=(), is_3d=False):
    return QuestionSpec(qid=7, target=target, prior=prior, depth=list(depth), is_3d=is_3d)


def rel(a, b):
    return abs(a - b) / abs(b)


def run(sp, tracks):
    ans = solve(sp, tracks, CAM.size, FPS)
    assert ans.qid == 7
    return ans


# ---------------------------------------------------------------- 2D scenes (depth 10 m)

Z = 10.0
PERSON = Body("person", static([1.0, 0.5, Z]), size=1.8, angle=math.pi / 2)
CAR = Body("car", static([-2.0, 1.0, Z]), size=4.5)
BALL = Body("ball", ballistic([-3.0, -2.0, Z], [2.0, -4.0, 0.0], [0.0, 9.8, 0.0]), size=0.22)
SLIDER = Body("puck", ballistic([-3.0, 1.0, Z], [1.5, -0.5, 0.0], [1.0, 0.6, 0.0]), size=0.3)
WALKER = Body("walker", ballistic([-3.0, 1.5, Z], [1.25, 0.0, 0.0]), size=1.7, angle=math.pi / 2)
ORBIT = Body("moon", circular([0.0, 0.0, Z], 2.0, 1.3), size=0.2)
SIGN_A = Body("sign a", static([-2.5, 0.0, Z]), size=0.6)
SIGN_B = Body("sign b", static([1.5, 0.8, Z]), size=0.6)

HEIGHT_PRIOR = Q("size", ["person"], dimension="height", value_si=1.8)


def _p(*bodies_roles, noise=0.0, **kw):
    return [track(b, r, T, CAM, noise_px=noise, seed=i, **kw) for i, (b, r) in enumerate(bodies_roles)]


CASES_2D = {
    "size->size": (Q("size", ["car"], dimension="length", unit="cm"), HEIGHT_PRIOR,
                   [(PERSON, "prior"), (CAR, "target")], 450.0),
    "size->speed@t": (Q("speed", ["ball"], time=1.0, unit="cm/s"), HEIGHT_PRIOR,
                      [(PERSON, "prior"), (BALL, "target")], BALL.speed(1.0) * 100),
    "size->mean speed (orbit)": (Q("speed", ["moon"], unit="m/s"), HEIGHT_PRIOR,
                                 [(PERSON, "prior"), (ORBIT, "target")], 2.0 * 1.3),
    "size->avg velocity window": (Q("speed", ["puck"], window=[1.0, 2.0], unit="m/s"), HEIGHT_PRIOR,
                                  [(PERSON, "prior"), (SLIDER, "target")],
                                  float(np.linalg.norm(SLIDER.pos(2.0) - SLIDER.pos(1.0)))),
    "size->accel@t": (Q("acceleration", ["puck"], time=1.5, unit="cm/s^2"), HEIGHT_PRIOR,
                      [(PERSON, "prior"), (SLIDER, "target")], math.hypot(1.0, 0.6) * 100),
    "size->accel whole track": (Q("acceleration", ["puck"], unit="m/s^2"), HEIGHT_PRIOR,
                                [(PERSON, "prior"), (SLIDER, "target")], math.hypot(1.0, 0.6)),
    "size->displacement": (Q("displacement", ["puck"], window=[0.5, 2.0], unit="m"), HEIGHT_PRIOR,
                           [(PERSON, "prior"), (SLIDER, "target")],
                           float(np.linalg.norm(SLIDER.pos(2.0) - SLIDER.pos(0.5)))),
    "size->path length (orbit)": (Q("path_length", ["moon"], unit="m"), HEIGHT_PRIOR,
                                  [(PERSON, "prior"), (ORBIT, "target")], 2.0 * 1.3 * T[-1]),
    "size->distance@t": (Q("distance", ["ball", "car"], time=1.0, unit="m"), HEIGHT_PRIOR,
                         [(PERSON, "prior"), (BALL, "target"), (CAR, "target2")],
                         float(np.linalg.norm(BALL.pos(1.0) - CAR.pos(1.0)))),
    "size->final distance": (Q("distance", ["ball", "car"], time=math.inf, unit="m"), HEIGHT_PRIOR,
                             [(PERSON, "prior"), (BALL, "target"), (CAR, "target2")],
                             float(np.linalg.norm(BALL.pos(T[-1]) - CAR.pos(T[-1])))),
    "size->distance static (median)": (Q("distance", ["sign a", "sign b"], unit="m"), HEIGHT_PRIOR,
                                       [(PERSON, "prior"), (SIGN_A, "target"), (SIGN_B, "target2")],
                                       float(np.linalg.norm(SIGN_A.pos(0) - SIGN_B.pos(0)))),
    "mean speed prior->size": (Q("size", ["car"], unit="m"), Q("speed", ["walker"], value_si=1.25),
                               [(WALKER, "prior"), (CAR, "target")], 4.5),
    "speed@t prior->size": (Q("size", ["person"], dimension="height", unit="m"),
                            Q("speed", ["ball"], time=0.5, value_si=BALL.speed(0.5)),
                            [(BALL, "prior"), (PERSON, "target")], 1.8),
    "gravity prior track->size": (Q("size", ["person"], dimension="height", unit="cm"),
                                  Q("acceleration", ["gravity"], value_si=9.8, axis="vertical"),
                                  [(BALL, "prior"), (PERSON, "target")], 180.0),
    "gravity on target->horizontal speed": (Q("speed", ["ball"], axis="horizontal", unit="m/s"),
                                            Q("acceleration", ["gravity"], value_si=9.8),
                                            [(BALL, "target")], 2.0),
    "accel prior->speed@t": (Q("speed", ["puck"], time=2.0, unit="km/h"),
                             Q("acceleration", ["puck"], value_si=math.hypot(1.0, 0.6)),
                             [(SLIDER, "prior"), (SLIDER, "target")], SLIDER.speed(2.0) * 3.6),
    "distance prior->size": (Q("size", ["car"], unit="mm"),
                             Q("distance", ["sign a", "sign b"],
                               value_si=float(np.linalg.norm(SIGN_A.pos(0) - SIGN_B.pos(0)))),
                             [(SIGN_A, "prior"), (SIGN_B, "prior2"), (CAR, "target")], 4500.0),
}


@pytest.mark.parametrize("name", list(CASES_2D))
def test_2d_exact(name):
    target, prior, roles, truth = CASES_2D[name]
    ans = run(spec(target, prior), _p(*roles))
    assert ans.method == "2d_scale"
    assert ans.value is not None, ans.flags
    assert rel(ans.value, truth) < 0.01, (ans.value, truth, ans.flags, ans.debug)


def test_2d_gravity_uses_target_track_flag():
    target, prior, roles, _ = CASES_2D["gravity on target->horizontal speed"]
    assert "gravity_from_target_track" in run(spec(target, prior), _p(*roles)).flags


def test_2d_gravity_uses_free_flight_only():
    # ball held for 0.6 s, thrown (free flight 1.2 s), then resting on the ground for 1.2 s
    fly = ballistic([-3.0, 0.5, Z], [2.0, -5.0, 0.0], [0.0, 9.8, 0.0])
    path = lambda t: fly(min(max(t - 0.6, 0.0), 1.2))  # noqa: E731
    ball = Body("ball", path, size=0.24)
    sp = spec(Q("size", ["person"], dimension="height", unit="m"), Q("acceleration", ["gravity"], value_si=9.8))
    for noise in (0.0, 1.0):
        ans = run(sp, [track(ball, "prior", T, CAM, noise_px=noise, seed=5), track(PERSON, "target", T, CAM)])
        assert "parabolic_segment" in ans.flags and rel(ans.value, 1.8) < (0.01 if noise == 0 else 0.1)


def test_2d_box_fallback():
    ball = Body("ball", static([0.5, 0.0, Z]), size=0.5)
    sp = spec(Q("size", ["car"], dimension="width", unit="m"),
              Q("size", ["ball"], dimension="diameter", value_si=0.5))
    tracks = [track(ball, "prior", T, CAM, extent=False, box=True),
              track(CAR, "target", T, CAM, extent=False, box=True)]  # synth box = ball of diameter `size`
    ans = run(sp, tracks)
    assert rel(ans.value, 4.5) < 0.01 and "size_from_box" in ans.flags


def test_2d_point_from_box():
    sp = spec(Q("speed", ["ball"], time=1.0, unit="m/s"), HEIGHT_PRIOR)
    boxes = track(BALL, "target", T, CAM, point=False, extent=False, box=True)
    ans = run(sp, [track(PERSON, "prior", T, CAM), boxes])
    assert rel(ans.value, BALL.speed(1.0)) < 0.01 and "point_from_box" in ans.flags


# ---------------------------------------------------------------- 3D scenes

P3 = Body("person", static([1.0, 0.6, 12.0]), size=1.8, angle=math.pi / 2)
CAR3 = Body("car", static([-2.0, 1.0, 18.0]), size=4.5)
BOAT3 = Body("boat", ballistic([-2.0, 0.5, 11.0], [1.0, 0.0, 1.2]), size=3.6)
CAR_ACC3 = Body("car", ballistic([-3.0, 1.0, 12.0], [1.0, 0.0, 2.0], [1.0, 0.0, 4.0]), size=4.5)
BALL3 = Body("ping pong ball", ballistic([-0.2, -0.1, 1.5], [0.3, 0.2, -1.2], [0.0, 1.0, 0.5]), size=0.04)
FALL3 = Body("ball", ballistic([-2.0, 5.0, 40.0], [1.5, -14.7, 0.8], [0.0, 9.8, 0.0]), size=0.3)  # stays in view
STATIC_DEPTH = depth_entries(P3, name="human") + depth_entries(CAR3)


def _depth_names(*bodies, times=DT):
    return [e for b in bodies for e in depth_entries(b, times)]


CASES_3D = {
    "size->size": (Q("size", ["car"], dimension="length", unit="m"), HEIGHT_PRIOR,
                   [(P3, "prior"), (CAR3, "target")], STATIC_DEPTH, 4.5),
    "size->speed@t radial": (Q("speed", ["boat"], time=1.5, unit="m/s"), HEIGHT_PRIOR,
                             [(P3, "prior"), (BOAT3, "target")],
                             depth_entries(P3, name="human") + _depth_names(BOAT3), BOAT3.speed(1.5)),
    "mean speed prior->size": (Q("size", ["boat"], dimension="length", unit="m"),
                               Q("speed", ["boat"], value_si=BOAT3.speed(0.0)),
                               [(BOAT3, "prior"), (BOAT3, "target")], _depth_names(BOAT3), 3.6),
    "accel prior->speed@t": (Q("speed", ["car"], time=1.0, unit="m/s"),
                             Q("acceleration", ["car"], value_si=math.hypot(1.0, 4.0)),
                             [(CAR_ACC3, "prior"), (CAR_ACC3, "target")], _depth_names(CAR_ACC3),
                             CAR_ACC3.speed(1.0)),
    "size->displacement radial": (Q("displacement", ["ping pong ball"], window=[1.0, 1.4], unit="cm"),
                                  Q("size", ["ping pong ball"], dimension="diameter", value_si=0.04),
                                  [(BALL3, "prior"), (BALL3, "target")],
                                  depth_entries(BALL3, DT, name="pingpong"),
                                  float(np.linalg.norm(BALL3.pos(1.4) - BALL3.pos(1.0))) * 100),
    "gravity->size": (Q("size", ["person"], dimension="height", unit="m"),
                      Q("acceleration", ["ball"], value_si=9.8, axis="vertical"),
                      [(FALL3, "prior"), (P3, "target")],
                      _depth_names(FALL3) + depth_entries(P3, name="human"), 1.8),
    "size->distance between objects": (Q("distance", ["person", "car"], time=1.0, unit="m"), HEIGHT_PRIOR,
                                       [(P3, "prior"), (P3, "target"), (CAR3, "target2")], STATIC_DEPTH,
                                       float(np.linalg.norm(P3.pos(0) - CAR3.pos(0)))),
}


@pytest.mark.parametrize("name", list(CASES_3D))
def test_3d_exact(name):
    target, prior, roles, depth, truth = CASES_3D[name]
    ans = run(spec(target, prior, depth, is_3d=True), _p(*roles))
    assert ans.value is not None, ans.flags
    assert ans.method == "3d_focal_from_prior", (ans.method, ans.flags)
    assert rel(ans.debug["f_px"], CAM.f) < 0.01
    assert rel(ans.value, truth) < 0.01, (ans.value, truth, ans.flags, ans.debug)


def test_3d_camera_distance_interpolated():
    depth = [DepthEntry("boat", 10.0, 0.0), DepthEntry("boat", 14.0, 2.0), DepthEntry("pier", 18.9)]
    prior = Q("size", ["x"], value_si=1.0)
    ans = run(spec(Q("camera_distance", ["boat"], time=1.0, unit="cm"), prior, depth, True), [])
    assert ans.method == "depth_direct" and ans.value == pytest.approx(1200.0)
    ans = run(spec(Q("camera_distance", ["the pier"], unit="m"), prior, depth, True), [])
    assert ans.value == pytest.approx(18.9)


def test_3d_target_depth_from_prior():
    # target with no depth entry, at the prior's range -> exact via the prior's depth
    r = P3.range(0)
    d = np.array([-0.15, 0.05, 1.0])
    bench = Body("bench", static(d / np.linalg.norm(d) * r), size=2.2)
    ans = run(spec(Q("size", ["bench"], unit="m"), HEIGHT_PRIOR, STATIC_DEPTH, True),
              _p((P3, "prior"), (bench, "target")))
    assert "target_depth_from_prior" in ans.flags and rel(ans.value, 2.2) < 0.01


def test_3d_prior_without_depth_uses_scene_median():
    # prior has no depth entry but sits at the scene's median range; target has its own depth
    others = [Body(n, static(p), size=1.0)
              for n, p in (("tree", [3, 0, 9]), ("pole", [-3, 0, 15]), ("rock", [0, 1, 30]))]
    med = float(np.median([b.range(0) for b in others + [CAR3]]))
    d = np.array([0.1, 0.05, 1.0])
    ball = Body("ball", static(d / np.linalg.norm(d) * med), size=0.25)
    depth = [e for b in others for e in depth_entries(b)] + depth_entries(CAR3)
    ans = run(spec(Q("size", ["car"], unit="m"), Q("size", ["ball"], value_si=0.25), depth, True),
              _p((ball, "prior"), (CAR3, "target")))
    assert ans.method == "3d_focal_assumed_depth" and "prior_depth_assumed_scene_median" in ans.flags
    assert rel(ans.value, 4.5) < 0.01


def test_3d_no_prior_track_default_focal():
    ans = run(spec(Q("size", ["car"], unit="m"), HEIGHT_PRIOR, STATIC_DEPTH, True), _p((CAR3, "target")))
    assert ans.method == "3d_default_focal" and {"no_prior_track", "default_focal"} <= set(ans.flags)
    assert rel(ans.value, 4.5) < 0.01   # true camera is 60 deg, the default


def test_3d_implausible_focal_falls_back():
    tracks = _p((P3, "prior"), (CAR3, "target"))
    ans = run(spec(Q("size", ["car"], unit="m"), Q("size", ["person"], value_si=0.05), STATIC_DEPTH, True),
              tracks)  # 0.05 m person -> ~2 deg FOV
    assert "f_implausible" in ans.flags and ans.method == "3d_default_focal" and ans.value > 0


def test_3d_without_depth_falls_back_to_2d():
    ans = run(spec(Q("size", ["car"], unit="m"), HEIGHT_PRIOR, [], True), _p((PERSON, "prior"), (CAR, "target")))
    assert ans.method == "2d_scale" and "3d_without_depth" in ans.flags and rel(ans.value, 4.5) < 0.01


# ---------------------------------------------------------------- noise robustness

NOISY_2D = ["size->size", "size->speed@t", "size->accel@t", "mean speed prior->size",
            "gravity prior track->size", "size->path length (orbit)", "size->distance@t"]
NOISY_3D = ["size->size", "size->speed@t radial", "mean speed prior->size", "accel prior->speed@t"]


@pytest.mark.parametrize("noise", [1.0, 2.0])
@pytest.mark.parametrize("name", NOISY_2D)
def test_2d_noisy(name, noise):
    target, prior, roles, truth = CASES_2D[name]
    ans = run(spec(target, prior), _p(*roles, noise=noise))
    assert rel(ans.value, truth) < 0.10, (ans.value, truth)


@pytest.mark.parametrize("noise", [1.0, 2.0])
@pytest.mark.parametrize("name", NOISY_3D)
def test_3d_noisy(name, noise):
    target, prior, roles, depth, truth = CASES_3D[name]
    ans = run(spec(target, prior, depth, True), _p(*roles, noise=noise))
    assert rel(ans.value, truth) < 0.10, (ans.value, truth)


def test_outlier_obs_rejected():
    tracks = _p((PERSON, "prior"), (BALL, "target"), noise=1.0)
    for i in (20, 31, 47):
        tracks[1].obs[i].point = [tracks[1].obs[i].point[0] + 60, tracks[1].obs[i].point[1] - 45]
    ans = run(spec(Q("speed", ["ball"], time=1.0, unit="m/s"), HEIGHT_PRIOR), tracks)
    assert rel(ans.value, BALL.speed(1.0)) < 0.05


def test_sparse_track():
    # a VLM annotator gives ~8 frames; local fits fall back to nearest obs
    times = np.linspace(0, 2.8, 8)
    tracks = [track(PERSON, "prior", times[:2], CAM), track(BALL, "target", times, CAM)]
    ans = run(spec(Q("speed", ["ball"], time=1.2, unit="m/s"), HEIGHT_PRIOR), tracks)
    assert rel(ans.value, BALL.speed(1.2)) < 0.01


# ---------------------------------------------------------------- edge cases

def test_missing_prior_track():
    ans = run(spec(Q("size", ["car"], unit="m"), HEIGHT_PRIOR), _p((CAR, "target")))
    assert ans.value is None and "no_prior_track" in ans.flags


def test_prior_found_by_name_when_role_missing():
    tracks = _p((PERSON, "other"), (CAR, "target"))
    prior = Q("size", ["the person"], dimension="height", value_si=1.8)
    ans = run(spec(Q("size", ["car"], unit="m"), prior), tracks)
    assert rel(ans.value, 4.5) < 0.01 and "prior_track_by_name" in ans.flags


def test_single_obs_speed_unsolvable():
    tracks = [track(PERSON, "prior", T, CAM), track(BALL, "target", T[:1], CAM)]
    ans = run(spec(Q("speed", ["ball"], time=0.0, unit="m/s"), HEIGHT_PRIOR), tracks)
    assert ans.value is None and "too_few_obs" in ans.flags


def test_single_obs_size_ok():
    tracks = [track(PERSON, "prior", T[:1], CAM), track(CAR, "target", T[5:6], CAM)]
    assert rel(run(spec(Q("size", ["car"], unit="m"), HEIGHT_PRIOR), tracks).value, 4.5) < 0.01


def test_nan_coords_ignored():
    tracks = _p((PERSON, "prior"), (BALL, "target"))
    for i in range(0, len(T), 7):
        tracks[1].obs[i].point = [math.nan, 3.0]
        tracks[0].obs[i].extent = [[math.nan, 1.0], [2.0, 3.0]]
    tracks[1].obs.append(Obs(t=math.nan, point=[1.0, 2.0]))
    tracks[1].obs.append(Obs(t=1.0))
    ans = run(spec(Q("speed", ["ball"], time=1.0, unit="m/s"), HEIGHT_PRIOR), tracks)
    assert rel(ans.value, BALL.speed(1.0)) < 0.01


def test_unknown_unit_returns_si():
    ans = run(spec(Q("size", ["car"], unit="furlongs"), HEIGHT_PRIOR), _p((PERSON, "prior"), (CAR, "target")))
    assert rel(ans.value, 4.5) < 0.01 and "unknown_unit" in ans.flags


@pytest.mark.parametrize("unit,factor", [("", 1), ("m", 1), ("meters", 1), ("cm", 100), ("mm", 1000),
                                         ("km", 1e-3)])
def test_length_units(unit, factor):
    ans = run(spec(Q("size", ["car"], unit=unit), HEIGHT_PRIOR), _p((PERSON, "prior"), (CAR, "target")))
    assert ans.value == pytest.approx(4.5 * factor, rel=1e-6)


def test_time_outside_track_clamped():
    tracks = _p((PERSON, "prior"), (SLIDER, "target"))
    ans = run(spec(Q("speed", ["puck"], time=10.0, unit="m/s"), HEIGHT_PRIOR), tracks)
    assert "time_outside_track" in ans.flags and rel(ans.value, SLIDER.speed(T[-1])) < 0.01


def test_static_target_speed_is_none_not_zero():
    ans = run(spec(Q("speed", ["car"], unit="m/s"), HEIGHT_PRIOR), _p((PERSON, "prior"), (CAR, "target")))
    assert ans.value is None and "invalid_value" in ans.flags


@pytest.mark.parametrize("bad", [None, 0.0, -1.0, math.nan])
def test_bad_prior_value(bad):
    prior = Q("size", ["person"], value_si=bad)
    ans = run(spec(Q("size", ["car"], unit="m"), prior), _p((PERSON, "prior"), (CAR, "target")))
    assert ans.value is None and "no_prior_value" in ans.flags


def test_garbage_never_raises():
    sp = spec(Q("speed", ["x"], time="soon", window=["a"], unit="m/s"), Q("weird", ["y"], value_si=1.0))
    bad = [RoleTrack("prior", "y", [Obs(t=0.0, point=["a", None], box=[1, 2]), Obs(t="x")]),
           {"role": "target", "object": "x", "obs": [{"t": 0, "point": [1, 2]}, {"t": 1, "point": [5, 2]}]}]
    for args in [(sp, bad, CAM.size, FPS), (sp, None, None, None), (None, [], (0, 0), 0)]:
        ans = solve(*args)
        assert ans.value is None or (math.isfinite(ans.value) and ans.value > 0)
    ans = solve(spec(Q("size", ["car"]), HEIGHT_PRIOR, STATIC_DEPTH, True),
                _p((P3, "prior"), (CAR3, "target")), (0, 0), FPS)
    assert ans.value is None and "bad_image_size" in ans.flags


def test_depth_name_mismatch_borrows_depth():
    depth = depth_entries(P3, name="human") + [DepthEntry("zebra", 18.0)]
    ans = run(spec(Q("size", ["car"], unit="m"), HEIGHT_PRIOR, depth, True), _p((P3, "prior"), (CAR3, "target")))
    assert ans.value is not None and "target_depth_from_prior" in ans.flags and "depth_target" not in ans.debug


# ---------------------------------------------------------------- depth name matching

ENTRIES = [DepthEntry(o, d) for o, d in [
    ("human", 12.0), ("the_pedestal_of_the_central _sculpture_and", 9.46), ("the centeral_sculpture", 9.46),
    ("the_nearest_freestanding_art_display_panel", 11.87), ("pingpong", 1.5), ("soccer_ball", 1.9),
    ("note_book", 0.96), ("desk_left", 0.86), ("desk_right", 0.85), ("yellow_car", 26.2), ("bike", 23.5)]]


@pytest.mark.parametrize("names,expected", [
    (["person"], ["human"]), (["walking pedestrian"], ["human"]), (["woman in yellow"], ["human"]),
    (["central sculpture"], ["the centeral_sculpture"]),
    (["freestanding art display panel"], ["the_nearest_freestanding_art_display_panel"]),
    (["ping pong ball"], ["pingpong"]), (["the soccerball"], ["soccer_ball"]), (["notebook"], ["note_book"]),
    (["desk"], ["desk_left", "desk_right"]), (["bicycle"], ["bike"]), (["", "yellow cars"], ["yellow_car"]),
    (["yoga ball"], None), (["basketball"], None), (["tree"], None),
])
def test_match_depth(names, expected):
    fn = match_depth(names, ENTRIES)
    assert (fn.names if fn else None) == expected


def test_depth_interpolation_and_ties():
    fn = match_depth(["desk"], ENTRIES)
    assert fn(0.0)[0] == pytest.approx((0.86 + 0.85) / 2)
    car = match_depth(["car"], [DepthEntry("car", 17.0, 1.0), DepthEntry("car", 23.0, 2.0)])
    assert car([0.0, 1.5, 3.0]).tolist() == pytest.approx([11.0, 20.0, 29.0])
    assert name_score("human", "person") == 1.0 and name_score("", "x") == 0.0


# ---------------------------------------------------------------- video rendering

def test_render_video(tmp_path):
    import cv2

    cam = Camera(width=160, height=120)
    ball = Body("ball", ballistic([-1.0, 0.0, 5.0], [1.0, 0.0, 0.0]), size=0.6, color=(0, 0, 255))
    path = str(tmp_path / "synth.mp4")
    n = render_video(path, [ball], cam, duration=1.0, fps=20)
    cap = cv2.VideoCapture(path)
    frames = []
    while True:
        ok, img = cap.read()
        if not ok:
            break
        frames.append(img)
    assert len(frames) == n == 20
    img = frames[10].astype(int)
    ys, xs = np.nonzero((img[:, :, 2] > 150) & (img[:, :, 1] < 100))
    tr = track(ball, "target", [10 / 20], cam)
    assert np.hypot(xs.mean() - tr.obs[0].point[0], ys.mean() - tr.obs[0].point[1]) < 1.5


# real validation depth_info strings, split the way a parser might (object = between
# "distance_" and "_camera"); checks which question objects find a depth entry
REAL_DEPTH = {
    "sculpture": ("t=0s, distance_human_camera = 12.26m\nt=1s, distance_human_camera = 10.97m\n"
                  "distance_the_pedestal_of_the_central _sculpture_and_camera = 9.460m\n"
                  "distance_the centeral_sculpture_camera = 9.460m\n"
                  "distance_the_nearest_freestanding_art_display_panel = 11.874m"),
    "street": ("t=0.58s, distance_human_camera = 34.4785m\nt=1.58s, distance_human_camera = 35.6486m\n"
               "t=0.58s, distance_yellow_car_camera = 26.2275m\nt=1.58s, distance_yellow_car_camera = 28.4240m\n"
               "t=0.58s, distance_white_car_camera = 22.7254m\nt=1.58s, distance_white_car_camera = 21.5370m\n"
               "t=0.58s, distance_bike_camera = 23.5534m\nt=1.58s, distance_bike_camera = 23.2262m"),
    "desk": ("t=0s, distance_cup_camera = 1.2100m\nt=0s, distance_note_book_camera = 0.9620m\n"
             "t=0s, distance_desk_left_camera = 0.8690m\nt=0s, distance_desk_right_camera = 0.8520m\n"
             "t=0s, distance_slope_far_camera = 1.3450m\nt=0s, distance_slope_near_camera = 1.1040m\n"),
}


def _parse_depth(text):
    import re
    out = []
    for line in text.splitlines():
        m = re.search(r"(?:t\s*=\s*([\d.]+)\s*s?\s*,\s*)?distance_(.+?)(?:_camera)?\s*=\s*([\d.]+)\s*m", line)
        if m:
            out.append(DepthEntry(m.group(2), float(m.group(3)), float(m.group(1)) if m.group(1) else None))
    return out


@pytest.mark.parametrize("scene,obj,expected", [
    ("sculpture", "person", 11.615), ("sculpture", "central sculpture", 9.46),
    ("sculpture", "pedestal of the central sculpture", 9.46), ("sculpture", "art display panel", 11.874),
    ("sculpture", "bench seat", None), ("sculpture", "bird", None),
    ("street", "walking pedestrian", 35.0636), ("street", "turning yellow car", 27.3258),
    ("street", "bicycle", 23.3898), ("street", "green car", None), ("street", "trash can", None),
    ("desk", "notebook", 0.962), ("desk", "desk", 0.8605), ("desk", "slope", 1.2245), ("desk", "ball", None),
])
def test_match_real_depth_strings(scene, obj, expected):
    fn = match_depth([obj], _parse_depth(REAL_DEPTH[scene]))
    if expected is None:
        assert fn is None, fn.names
    else:
        t_mid = 1.08 if scene == "street" else 0.5
        assert fn is not None and fn(t_mid)[0] == pytest.approx(expected, rel=1e-3)


# ---------------------------------------------------------------- review regressions

GRAVITY = Q("acceleration", [], value_si=9.8, axis="vertical")   # generic gravity prior, no object


@pytest.mark.parametrize("noise,times", [(0.0, np.linspace(0.2, 2.8, 6)), (1.0, np.linspace(0.2, 2.8, 6)),
                                         (1.0, T)])
def test_gravity_without_prior_track_static_target_is_none(noise, times):
    # the target (a standing person) never falls: its "vertical acceleration" is noise
    ans = run(spec(Q("size", ["person"], dimension="height", unit="m"), GRAVITY),
              [track(PERSON, "target", times, CAM, noise_px=noise, seed=3)])
    assert ans.value is None and {"gravity_from_target_track", "prior_motion_below_noise"} <= set(ans.flags)


def test_gravity_without_prior_track_static_distance_is_none():
    a = Body("passer", static([-2, 1, Z]), 1.6, math.pi / 2)
    b = Body("receiver", static([2, 1, Z]), 1.8, math.pi / 2)
    tracks = [track(a, "target", T, CAM, noise_px=1.0, seed=1), track(b, "target2", T, CAM, noise_px=1.0, seed=2)]
    ans = run(spec(Q("distance", ["passer", "receiver"], time=0.0, unit="m"), GRAVITY), tracks)
    assert ans.value is None and "prior_motion_below_noise" in ans.flags


def test_gravity_without_prior_track_falling_size_target_ok():
    # the size target is itself the falling ball: borrowing its track is right
    ans = run(spec(Q("size", ["ball"], dimension="diameter", unit="cm"), GRAVITY),
              [track(BALL, "target", T, CAM, noise_px=1.0, seed=4)])
    assert "gravity_from_target_track" in ans.flags and rel(ans.value, 22.0) < 0.1


STILL = Body("walker", static([1.0, 1.0, Z]), size=1.7, angle=math.pi / 2)   # tracker locked on a parked object
STATIC_PRIORS = {"mean speed": Q("speed", ["walker"], value_si=1.25),
                 "speed@t": Q("speed", ["walker"], time=1.0, value_si=1.25),
                 "speed window": Q("speed", ["walker"], window=[0.5, 2.5], value_si=1.25),
                 "accel@t": Q("acceleration", ["walker"], time=1.5, value_si=3.0),
                 "gravity": Q("acceleration", ["gravity"], value_si=9.8)}


@pytest.mark.parametrize("noise", [0.0, 0.5, 2.0])
@pytest.mark.parametrize("name", list(STATIC_PRIORS))
def test_static_motion_prior_is_none(name, noise):
    ans = run(spec(Q("size", ["car"], unit="m"), STATIC_PRIORS[name]),
              [track(STILL, "prior", T, CAM, noise_px=noise, seed=1), track(CAR, "target", T, CAM)])
    assert ans.value is None and "prior_motion_below_noise" in ans.flags


def test_static_motion_prior_3d_falls_back_to_default_focal():
    still = Body("car", static([-2.0, 1.0, 18.0]), size=4.5)
    ans = run(spec(Q("size", ["car"], unit="m"), Q("speed", ["car"], value_si=2.0), STATIC_DEPTH, True),
              _p((still, "prior"), (CAR3, "target"), noise=1.0))
    assert ans.method == "3d_default_focal" and "prior_motion_below_noise" in ans.flags
    assert rel(ans.value, 4.5) < 0.05


def test_sparse_noisy_motion_priors_still_accepted():
    times = np.linspace(0.0, 2.9, 8)   # VLM-style: 8 labelled frames with 3 px jitter
    for body, prior in ((WALKER, Q("speed", ["walker"], value_si=1.25)),
                        (BALL, Q("acceleration", ["gravity"], value_si=9.8)),
                        (BALL, Q("speed", ["ball"], time=1.0, value_si=BALL.speed(1.0)))):
        ans = run(spec(Q("size", ["car"], unit="m"), prior),
                  [track(body, "prior", times, CAM, noise_px=3.0, seed=2), track(CAR, "target", T, CAM)])
        assert ans.value is not None and rel(ans.value, 4.5) < 0.1, (prior, ans.flags)


def test_degenerate_prior_scale_rejected():
    tracks = _p((PERSON, "prior"), (CAR, "target"))
    for o in tracks[0].obs:
        x, y = o.extent[0]
        o.extent = [[x, y], [x, y + 1e-9]]   # a "1.8 m" person 1e-9 px tall
    ans = run(spec(Q("size", ["car"], unit="m"), HEIGHT_PRIOR), tracks)
    assert ans.value is None and "scale_implausible" in ans.flags


BALL_P = Body("purple ball", static([-0.5, 0.2, Z]), size=0.3)
BALL_K = Body("black ball", static([0.8, 0.2, Z]), size=0.3)
CUE = Body("ball", static([0.0, -0.5, Z]), size=0.3)
BALL_PRIOR = Q("size", ["ball"], dimension="diameter", value_si=0.3)
FINAL_GAP = Q("distance", ["purple ball", "black ball"], time=math.inf, unit="cm")


def test_two_object_distance_missing_target2_is_none():
    # second ball not tracked: must not answer with the first ball's own box / extent size
    for kw in ({"extent": False, "box": True}, {}):
        ans = run(spec(FINAL_GAP, BALL_PRIOR), [track(CUE, "prior", T, CAM), track(BALL_P, "target", T, CAM, **kw)])
        assert ans.value is None and "no_target2_track" in ans.flags


def test_two_object_distance_does_not_borrow_generic_prior_track():
    # target2 "black ball" must not resolve to the prior's "ball" track (another instance)
    ans = run(spec(FINAL_GAP, BALL_PRIOR), [track(CUE, "prior", T, CAM), track(BALL_P, "target", T, CAM)])
    assert ans.value is None and "target2_track_by_name" not in ans.flags
    tracks = [track(CUE, "prior", T, CAM), track(BALL_P, "target", T, CAM), track(BALL_K, "other", T, CAM)]
    ans = run(spec(FINAL_GAP, BALL_PRIOR), tracks)   # a well-named spare track is still found
    assert "target2_track_by_name" in ans.flags and rel(ans.value, 130.0) < 0.01


def test_one_object_distance_uses_extent_only():
    sp = spec(Q("distance", ["jump"], unit="m"), HEIGHT_PRIOR)
    ans = run(sp, _p((PERSON, "prior"), (CAR, "target")))
    assert "distance_from_extent" in ans.flags and rel(ans.value, 4.5) < 0.01
    ans = run(sp, [track(PERSON, "prior", T, CAM), track(CAR, "target", T, CAM, extent=False, box=True)])
    assert ans.value is None and "no_target2_track" in ans.flags


def test_gravity_mean_horizontal_speed_uses_free_flight():
    # ball held 0.6 s, free flight 1.2 s (vx = 2 m/s), then at rest 1.2 s; prior gravity on the same ball
    fly = ballistic([-3.0, 0.5, Z], [2.0, -5.0, 0.0], [0.0, 9.8, 0.0])
    ball = Body("ball", lambda t: fly(min(max(t - 0.6, 0.0), 1.2)), size=0.24)
    sp = spec(Q("speed", ["ball"], axis="horizontal", unit="m/s"),
              Q("acceleration", ["ball"], value_si=9.8, axis="vertical"))
    for noise in (0.0, 1.0):
        tracks = [track(ball, role, T, CAM, noise_px=noise, seed=i) for i, role in enumerate(("prior", "target"))]
        ans = run(sp, tracks)
        assert "parabolic_segment" in ans.flags and rel(ans.value, 2.0) < (0.01 if noise == 0 else 0.05)


def test_radial_motion_prior_flags_ill_conditioned_focal():
    # mostly line-of-sight motion: the prior speed hardly depends on f
    boat = Body("boat", ballistic([-0.5, 0.5, 8.0], [0.4, 0.0, 2.0]), size=3.0)
    sp = spec(Q("size", ["boat"], unit="m"), Q("speed", ["boat"], time=1.5, value_si=boat.speed(1.5)),
              _depth_names(boat), True)
    ans = run(sp, _p((boat, "prior"), (boat, "target")))
    assert "f_ill_conditioned" in ans.flags and ans.debug["f_sensitivity"] < 0.3
    assert ans.method == "3d_focal_from_prior" and rel(ans.value, 3.0) < 0.02   # exact data: f kept (60 deg)
    ans = run(spec(*CASES_3D["size->size"][:2], STATIC_DEPTH, True), _p((P3, "prior"), (CAR3, "target")))
    assert "f_ill_conditioned" not in ans.flags and ans.debug["f_sensitivity"] == pytest.approx(1.0, abs=0.01)
