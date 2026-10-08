"""qp.dense_track on synthetic videos (tests/synth.py): known trajectories, scale change, occlusion,
annotator-like noisy sparse anchors; sizes re-measured by segmentation; the annotation layer."""

import math

import cv2
import numpy as np
import pytest

from qp import dense_track as dt
from qp.claude_annotate import Annotation
from qp.geometry import solve
from qp.spec import Obs, Quantity, QuestionSpec, RoleTrack
from synth import Body, Camera, ballistic, frame_times, render_video, track

FPS = 30.0
CAM = Camera(640, 360, 60.0)


def _render(tmp_path, bodies, duration=3.0, name="v.mp4"):
    path = str(tmp_path / name)
    n = render_video(path, bodies, CAM, duration, FPS, background=(40, 40, 40))
    return path, n


def _truth(body, n):
    return {i: CAM.project(body.pos(i / FPS))[0] for i in range(n)}


def _drawn(body, n):
    """Centres as render_video draws them: rounded to a pixel index, i.e. index + 0.5 in the
    continuous coordinates of the annotations (up to 0.7 px off the true trajectory)."""
    return {i: np.round(CAM.project(body.pos(i / FPS))[0]) + 0.5 for i in range(n)}


def _shape_errors(path_px, drawn):
    """|dense - drawn| after removing the constant offset (which the noisy anchors set)."""
    d = np.array([np.asarray(p) - drawn[f] for f, p in path_px.items()])
    return np.linalg.norm(d - d.mean(axis=0), axis=1)


def _sparse(body, frames, noise, seed=0):
    return track(body, "prior", [f / FPS for f in frames], CAM, noise_px=noise, seed=seed, box=True,
                 extent=False).obs


def _dense(path, obs, n):
    frames = [int(round(o.t * FPS)) for o in obs]
    win = dt.decode(path, set(range(min(frames), max(frames) + 1)))
    return dt.dense_motion(win, obs, FPS)


def _errors(path_px, truth):
    return np.array([np.linalg.norm(np.asarray(p) - truth[f]) for f, p in path_px.items()])


def test_linear_motion_tracked_within_a_pixel(tmp_path):
    ball = Body("ball", ballistic([-1.2, -0.3, 6.0], [0.8, 0.2, 0.0]), size=0.35, color=(30, 60, 220))
    path, n = _render(tmp_path, [ball])
    obs = _sparse(ball, range(2, n - 2, 7), noise=1.5)
    got, info = _dense(path, obs, n)
    assert got is not None, info
    assert len(got) >= 0.9 * (obs[-1].t - obs[0].t) * FPS          # one point per frame
    shape = _shape_errors(got, _drawn(ball, n))
    assert np.median(shape) < 0.25 and shape.max() < 0.75, (np.median(shape), shape.max())
    err = _errors(got, _truth(ball, n))                             # + rendering rounding + anchor noise
    assert np.median(err) < 0.8 and err.max() < 1.5, (np.median(err), err.max())
    # much better than the annotator's own points
    sparse_err = [np.linalg.norm(np.asarray(o.point) - CAM.project(ball.pos(o.t))[0]) for o in obs]
    assert np.median(err) < 0.5 * np.median(sparse_err)


def test_scale_change_keeps_the_reference_point(tmp_path):
    # approaching the camera: the disc grows from ~12 to ~32 px across
    ball = Body("ball", ballistic([-0.8, 0.1, 6.0], [0.3, 0.0, -1.2]), size=0.2, color=(40, 200, 230))
    path, n = _render(tmp_path, [ball])
    obs = _sparse(ball, range(1, n - 1, 6), noise=1.0, seed=1)
    got, info = _dense(path, obs, n)
    assert got is not None, info
    err = _errors(got, _truth(ball, n))
    assert np.median(err) < 0.6 and err.max() < 1.3, (np.median(err), err.max())


def test_occlusion_of_a_few_frames(tmp_path):
    ball = Body("ball", ballistic([-1.5, 0.0, 6.0], [1.0, 0.0, 0.0]), size=0.35, color=(30, 60, 220))
    # a nearer, larger disc crosses in front of the ball for a few frames around t = 1.5 s
    cover = Body("cover", ballistic([0.0, -2.2, 4.0], [0.0, 1.4, 0.0]), size=0.45, color=(200, 200, 200))
    path, n = _render(tmp_path, [ball, cover])
    truth = _truth(ball, n)
    hidden = [i for i in range(n) if np.linalg.norm(truth[i] - CAM.project(cover.pos(i / FPS))[0])
              < CAM.f * (0.45 / 4.0 - 0.35 / 6.0) / 2]
    assert 2 <= len(hidden) <= 10  # the scene really hides the ball for a few frames
    frames = [f for f in range(2, n - 2, 8) if f not in hidden]
    obs = _sparse(ball, frames, noise=1.0, seed=2)
    got, info = _dense(path, obs, n)
    assert got is not None, info
    visible = {f: p for f, p in got.items()
               if np.linalg.norm(truth[f] - CAM.project(cover.pos(f / FPS))[0]) > CAM.f * (0.45 / 4.0 + 0.35 / 6.0) / 2 + 2}
    err = _errors(visible, truth)
    assert np.median(err) < 0.6 and err.max() < 1.2, (np.median(err), err.max())
    assert all(f not in got or np.linalg.norm(np.asarray(got[f]) - truth[f]) < 3.0 for f in hidden)


def test_dense_track_sharpens_the_geometry(tmp_path):
    # projectile under a stated gravity of 9.8 m/s^2 (prior); the target is its speed at t = 1 s
    ball = Body("ball", ballistic([-1.6, -0.9, 6.0], [1.1, -2.5, 0.0], [0.0, 3.0, 0.0]), size=0.25,
                color=(30, 60, 220))
    path, n = _render(tmp_path, [ball], duration=2.0)
    obs = _sparse(ball, range(1, n - 1, 5), noise=1.5, seed=3)
    got, info = _dense(path, obs, n)
    assert got is not None, info
    spec = QuestionSpec(1, target=Quantity("speed", ["ball"], time=1.0, unit="m/s"),
                        prior=Quantity("acceleration", ["ball"], axis="vertical", value_si=3.0))
    true_v = ball.speed(1.0)
    sparse_v = solve(spec, [RoleTrack("prior", "ball", obs)], CAM.size, FPS).value
    dense_v = solve(spec, [RoleTrack("prior", "ball", dt.motion_obs(got, obs, FPS))], CAM.size, FPS).value
    assert abs(dense_v / true_v - 1) < 0.02, (dense_v, true_v)
    assert abs(dense_v / true_v - 1) < abs(sparse_v / true_v - 1)


def test_guards_reject_a_track_that_jumps_objects(tmp_path):
    a = Body("a", ballistic([-1.5, -0.5, 6.0], [1.0, 0.0, 0.0]), size=0.3, color=(30, 60, 220))
    b = Body("b", ballistic([1.5, 0.6, 6.0], [-1.0, 0.0, 0.0]), size=0.3, color=(30, 60, 220))
    path, n = _render(tmp_path, [a, b])
    oa, ob = _sparse(a, range(2, n - 2, 8), 0.5), _sparse(b, range(2, n - 2, 8), 0.5)
    mixed = [oa[k] if k % 2 == 0 else ob[k] for k in range(len(oa))]   # annotator alternates objects
    got, info = _dense(path, mixed, n)
    assert got is None and info["why"] in ("cover", "residual"), info
    # point-only anchors with nothing to size the object (no boxes, no blob): left alone
    flat = [Obs(t=o.t, point=[20.0 + 0.1 * k, 20.0]) for k, o in enumerate(oa)]
    got, info = _dense(path, flat, n)
    assert got is None and info["why"] == "no_size"


def test_point_only_track_gets_its_size_from_the_blob(tmp_path):
    ball = Body("ball", ballistic([-1.2, 0.0, 6.0], [0.9, 0.0, 0.0]), size=0.4, color=(30, 60, 220))
    path, n = _render(tmp_path, [ball])
    obs = [Obs(t=o.t, point=o.point) for o in _sparse(ball, range(2, n - 2, 7), noise=1.0, seed=4)]
    got, info = _dense(path, obs, n)
    assert got is not None and "size_from_blob" in info["notes"], info
    err = _errors(got, _truth(ball, n))
    assert np.median(err) < 0.6 and err.max() < 1.3


def test_blob_size_measures_a_disc():
    img = np.full((120, 120), 40, np.uint8)
    cv2.circle(img, (60 * 16, 60 * 16), 12 * 16, 220, -1, cv2.LINE_AA, shift=4)
    d = dt.blob_size(img, (60.0, 60.0), 60)
    assert d == pytest.approx(24, rel=0.25)


def _rect_video(path, rects, size=(480, 320), n=3):
    vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), FPS, size)
    for _ in range(n):
        img = np.full((size[1], size[0], 3), (60, 70, 80), np.uint8)
        for (x0, y0, x1, y1), col in rects:
            cv2.rectangle(img, (x0, y0), (x1 - 1, y1 - 1), col, -1)
        vw.write(img)
    vw.release()
    return str(path)


@pytest.mark.parametrize("method", ["grabcut", "snap"])
def test_size_extents_within_two_percent(tmp_path, method):
    # a 120 x 60 px box (edges at x 100..220, y 80..140) and a disc of diameter 50 px
    path = _rect_video(tmp_path / "r.mp4", [((100, 80, 220, 140), (40, 180, 230))])
    ball = Body("ball", lambda t: np.array([1.0, 0.4, 6.0]), size=50 * 6.0 / CAM.f, color=(30, 60, 220))  # 50 px
    vpath, _ = _render(tmp_path, [ball], duration=0.2, name="b.mp4")
    W, H = 480, 320
    # annotator extents off by +8% / -7%, boxes a little loose
    width = [Obs(t=0.0, extent=[[96.0, 110.0], [225.6, 110.0]], box=[97.0, 78.0, 223.0, 143.0])]
    height = [Obs(t=1 / FPS, extent=[[160.0, 82.0], [160.0, 137.8]], box=[98.0, 79.0, 222.0, 141.0])]
    c = CAM.project(ball.pos(0))[0]
    diam = [Obs(t=0.0, extent=[[c[0] - 27, c[1]], [c[0] + 27, c[1]]], box=[c[0] - 27, c[1] - 27, c[0] + 27, c[1] + 27])]
    for obs, dim, name, want, vid, size in ((width, "width", "box", 120, path, (W, H)),
                                            (height, "height", "box", 60, path, (W, H)),
                                            (diam, "diameter", "ball", 50.5, vpath, CAM.size)):  # AA disc of radius 25
        crops = {int(round(o.t * FPS)): [dt._seg_crop_box(o.box, *size)] for o in obs}
        win = dt.decode(vid, set(), crops)
        new, info = dt.dense_size(win, obs, FPS, dim, name, method=method)
        if method == "snap" and dim == "diameter":
            continue  # snapping keeps the annotator's line: a diameter off-centre is not fixable by it
        assert new is not None, info
        L = math.hypot(*np.subtract(new[0].extent[1], new[0].extent[0]))
        assert L == pytest.approx(want, rel=0.02), (dim, method, L, info)


def test_size_keeps_the_annotators_extent_when_segmentation_is_implausible(tmp_path):
    # the box covers two touching objects of the same colour: the mask is far larger than the extent
    path = _rect_video(tmp_path / "r.mp4", [((100, 80, 400, 140), (40, 180, 230))])
    obs = [Obs(t=0.0, extent=[[100.0, 110.0], [160.0, 110.0]], box=[100.0, 80.0, 160.0, 140.0])]
    win = dt.decode(path, set(), {0: [dt._seg_crop_box(obs[0].box, 480, 320)]})
    new, info = dt.dense_size(win, obs, FPS, "width", "box", method="grabcut")
    assert new is None or new[0].extent == obs[0].extent, info


def _annotation(obs_prior, obs_target):
    spec = QuestionSpec(7, target=Quantity("speed", ["ball"], time=1.0, unit="m/s"),
                        prior=Quantity("size", ["ball"], dimension="diameter", value_si=0.35))
    return Annotation(spec=spec, tracks=[RoleTrack("prior", "ball", obs_prior, "claude"),
                                         RoleTrack("target", "ball", obs_target, "claude")],
                      direct_answer=1.0, confidence=0.5)


def test_densify_annotations_caches_and_flags(tmp_path, monkeypatch):
    ball = Body("ball", ballistic([-1.2, -0.3, 6.0], [0.8, 0.2, 0.0]), size=0.35, color=(30, 60, 220))
    path, n = _render(tmp_path, [ball])
    pts = [Obs(t=o.t, point=o.point) for o in _sparse(ball, range(2, n - 2, 7), noise=1.0)]
    sizes = track(ball, "prior", [0.5, 1.0], CAM, box=True).obs
    a = _annotation(sizes, pts)
    log = []
    dt.densify_annotations({7: a}, {7: path}, {7: (FPS, CAM.size, 1.0)}, what="motion",
                           cache_dir=tmp_path / "cache", log=log)
    tgt = a.tracks[1]
    assert "dense_motion" in a.flags and tgt.source == "dense", log
    assert sum(o.point is not None for o in tgt.obs) > 3 * len(pts)
    assert a.tracks[0].source == "claude"                                   # size track untouched
    assert log[0][3]["notes"] == ["size_from_other_track"]                  # box size from the prior track
    assert list((tmp_path / "cache").glob("*.json"))
    # second run: served from the cache (no decoding)
    monkeypatch.setattr(dt, "decode", lambda *a, **k: (_ for _ in ()).throw(AssertionError("decoded")))
    b = _annotation(list(sizes), list(pts))
    dt.densify_annotations({7: b}, {7: path}, {7: (FPS, CAM.size)}, what="motion", cache_dir=tmp_path / "cache")
    assert [o.point for o in b.tracks[1].obs] == [o.point for o in tgt.obs]
    # an unreadable video keeps the tracks and flags the annotation
    c = _annotation(list(sizes), list(pts))
    dt.densify_annotations({7: c}, {7: str(tmp_path / "missing.mp4")}, {7: (FPS, CAM.size)})
    assert "dense_error" in c.flags and c.tracks[1].obs == pts


def test_skip_and_kinds(tmp_path):
    ball = Body("ball", ballistic([-1.2, -0.3, 6.0], [0.8, 0.2, 0.0]), size=0.35)
    path, n = _render(tmp_path, [ball])
    pts = _sparse(ball, range(2, n - 2, 7), noise=1.0)
    a = _annotation([], list(pts))
    dt.densify_annotations({7: a}, {7: path}, {7: (FPS, CAM.size)}, skip={(7, "target")})
    assert a.tracks[1].obs == pts and "dense_motion" not in a.flags
    jobs = dt.plan({7: a}, what="both")
    assert [(j[2].role, j[3]) for j in jobs] == [("target", "motion")]


def test_frame_times_match_the_rendered_frames(tmp_path):
    # guards the convention the tests rely on: frame i of render_video is at t = i / fps
    ball = Body("ball", ballistic([-1.0, 0.0, 6.0], [1.0, 0.0, 0.0]), size=0.35)
    path, n = _render(tmp_path, [ball], duration=1.0)
    assert n == len(frame_times(1.0, FPS))
    win = dt.decode(path, {0, n - 1})
    assert sorted(win.work) == [0, n - 1] and win.size == CAM.size


def test_cli_rescores_a_cached_run_with_dense_tracks(tmp_path, monkeypatch):
    """scripts/dense_tracks.py on a synthetic cached run: dense CSV written with run_claude's columns,
    the dense speed closer to the truth than the annotator's, run_claude's module state restored."""
    import importlib.util
    import json
    import sys
    from pathlib import Path

    import pandas as pd

    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "scripts"))
    spec_ = importlib.util.spec_from_file_location("dense_tracks_cli", root / "scripts" / "dense_tracks.py")
    cli = importlib.util.module_from_spec(spec_)
    spec_.loader.exec_module(cli)

    ball = Body("ball", ballistic([-1.4, -0.2, 6.0], [1.0, 0.25, 0.0]), size=0.35, color=(30, 60, 220))
    path, n = _render(tmp_path, [ball])
    frames = list(range(2, n - 2, 6))
    rng = np.random.default_rng(5)
    to = lambda p: [round(float(v), 1) for v in p]  # noqa: E731
    obs = []
    for f in frames:
        c = CAM.project(ball.pos(f / FPS))[0] + rng.normal(0, 1.5, 2)
        r = CAM.f * 0.35 / 6.0 / 2
        obs.append({"frame": f, "point": to(c), "extent": None, "box": to([c[0] - r, c[1] - r, c[0] + r, c[1] + r])})
    sizes = [{"frame": f, "point": None, "extent": [to(CAM.project(ball.pos(f / FPS))[0] - [CAM.f * 0.175 / 6, 0]),
                                                   to(CAM.project(ball.pos(f / FPS))[0] + [CAM.f * 0.175 / 6, 0])],
              "box": None} for f in frames[:3]]
    q = lambda kind, **kw: {"kind": kind, "objects": ["ball"], "dimension": kw.get("dimension", ""),  # noqa: E731
                            "time": kw.get("time"), "window": None, "axis": "any",
                            "value_si": kw.get("value_si"), "unit": kw.get("unit", "")}
    parsed = {"questions": [{"qid": 11, "spec": {"target": q("speed", time=1.5, unit="m/s"),
                                                 "prior": q("size", dimension="diameter", value_si=0.35),
                                                 "depth": [], "notes": ""},
                             "tracks": [{"role": "prior", "object": "ball", "obs": sizes},
                                        {"role": "target", "object": "ball", "obs": obs}],
                             "direct_answer": 1.5, "confidence": 0.5}]}
    meta = {"video_id": "synth", "fps": FPS, "video_type": "V2MS", "n_frames_total": n, "scale": 1.0,
            "image_size": list(CAM.size), "frames": frames,
            "questions": [{"qid": 11, "target_unit": "m/s", "prior": "diameter of the ball = 0.35 m", "depth_info": ""}]}
    rec_dir = tmp_path / "runs" / "fake" / "val" / "records"
    rec_dir.mkdir(parents=True)
    (rec_dir / "synth.json").write_text(json.dumps({"video_id": "synth", "status": "ok", "parsed": parsed, "meta": meta}))
    truth = ball.speed(1.5)
    df = pd.DataFrame([{"qid": 11, "video_id": "synth", "video_path": path, "video_type": "V2MS", "fps": FPS,
                        "inference_type": "SD", "question": "What is the speed of the ball at 1.5s in m/s?",
                        "prior": "diameter of the ball = 0.35 m", "depth_info": "", "video_source": "simulation",
                        "category": "S2", "target_unit": "m/s", "answer": truth}])
    monkeypatch.setattr(cli, "load_split", lambda split: df)
    before = (cli.rc.ca.load_annotations, cli.rc.REFINE_PRIORS)
    res = cli.main(["--name", "fake", "--split", "val", "--out-root", str(tmp_path / "runs"), "--workers", "1",
                    "--cache-dir", str(tmp_path / "cache")])
    assert (cli.rc.ca.load_annotations, cli.rc.REFINE_PRIORS) == before
    out = pd.read_csv(tmp_path / "runs" / "fake" / "val_dense.csv")
    assert list(out.columns) == ["id", "parsed_value", "geo_value", "direct_value", "method", "flags", "geo_method"]
    assert "dense_motion" in out["flags"][0] and res.geo_value[0] == pytest.approx(out.geo_value[0])
    sparse = cli.build(df, cli.rc.load_records(rec_dir), "none")
    assert abs(out.geo_value[0] / truth - 1) < 0.02
    assert abs(out.geo_value[0] / truth - 1) <= abs(sparse.geo_value[0] / truth - 1) + 0.002
