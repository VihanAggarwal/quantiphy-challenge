"""qp.dense_track on synthetic videos (tests/synth.py): known trajectories, scale change, occlusion,
annotator-like noisy sparse anchors; sizes re-measured by segmentation; the annotation layer."""

import json
import math

import cv2
import numpy as np
import pytest
from synth import Body, Camera, ballistic, frame_times, render_video, track

from qp import dense_track as dt
from qp.claude_annotate import Annotation
from qp.geometry import solve
from qp.spec import Obs, Quantity, QuestionSpec, RoleTrack

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


# --------------------------------------------------------------------------- review regressions


def _textured_video(path, n, r, contrast, speed, fourcc="FFV1", seed=0):
    """A flat disc (radius r, `contrast` grey levels above the mean) moving at `speed` px/frame on a
    static blurred-noise texture (std ~6 grey levels) -> centres (continuous coordinates)."""
    rng = np.random.default_rng(seed)
    W, H = 640, 360
    bg = cv2.GaussianBlur(rng.normal(128, 40, (H, W, 3)).astype(np.float32), (0, 0), 2.0)
    vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*fourcc), FPS, (W, H))
    cs = []
    for i in range(n):
        c = np.array([200.0 + speed * i, 180.0 + 0.3 * speed * i])
        m = np.zeros((H, W), np.uint8)
        cv2.circle(m, (int(round(c[0] * 16)), int(round(c[1] * 16))), int(r * 16), 255, -1, cv2.LINE_AA, shift=4)
        a = m.astype(np.float32)[..., None] / 255
        img = bg * (1 - a) + np.array([128 + contrast, 128 + contrast, 128], np.float32) * a
        vw.write(np.clip(img, 0, 255).astype(np.uint8))
        cs.append(c + 0.5)
    vw.release()
    return cs


def _loose_boxes(cs, r, loose, every=6, noise=1.0, seed=1):
    """Annotator-like anchors: point and a square box `loose` x the disc's diameter, both off by noise."""
    rng = np.random.default_rng(seed)
    out = []
    for f in range(0, len(cs) - every + 1, every):
        c = cs[f] + rng.normal(0, noise, 2)
        h = r * loose
        out.append(Obs(t=f / FPS, point=list(c), box=[c[0] - h, c[1] - h, c[0] + h, c[1] + h]))
    return out


def _disp_error(got, obs, cs):
    fa, fb = int(round(obs[0].t * FPS)), int(round(obs[-1].t * FPS))
    true = np.linalg.norm(cs[fb] - cs[fa])
    return float(np.linalg.norm(np.subtract(got[fb], got[fa])) / true - 1)


@pytest.mark.parametrize("loose", [1.7, 2.4])
def test_loose_boxes_on_a_textured_background_keep_the_displacement(tmp_path, monkeypatch, loose):
    """Whole-box templates of a slowly moving disc on a textured background match the static
    background as much as the disc: every segment lagged alike, the chained path lost 20-67 % of the
    motion and was accepted. Object-weighted templates keep the displacement within 2 %."""
    cs = _textured_video(tmp_path / "t.avi", 90, 14, 25, 1.0)
    obs = _loose_boxes(cs, 14, loose)
    win = dt.decode(str(tmp_path / "t.avi"), set(range(90)))
    got, info = dt.dense_motion(win, obs, FPS)
    assert got is not None, info
    assert info["mask"].get("grabcut", 0) >= 0.8 * len(obs), info["mask"]
    assert abs(_disp_error(got, obs, cs)) < 0.02, (_disp_error(got, obs, cs), info["scale"])
    # control: whole-box templates without the chain-scale check lose far more of the motion
    monkeypatch.setattr(dt, "TEMPLATE_MASK", "none")
    monkeypatch.setattr(dt, "SCALE_Z", 1e9)
    got0, info0 = dt.dense_motion(win, obs, FPS)
    assert got0 is None or _disp_error(got0, obs, cs) < -0.05, info0


def test_chain_scale_check_rejects_a_shrunken_chain(tmp_path, monkeypatch):
    """With whole-box templates (the failure above) the chain's scale disagrees with the annotator's
    points by far more than their noise explains: rejected instead of accepted short by > 10 %."""
    cs = _textured_video(tmp_path / "t.avi", 90, 14, 25, 1.0)
    obs = _loose_boxes(cs, 14, 1.7)
    win = dt.decode(str(tmp_path / "t.avi"), set(range(90)))
    monkeypatch.setattr(dt, "TEMPLATE_MASK", "none")
    got, info = dt.dense_motion(win, obs, FPS)
    assert got is None or abs(_disp_error(got, obs, cs)) < 0.05, info
    assert got is None and info["why"] == "scale", info


def test_textured_background_through_a_lossy_codec(tmp_path):
    """The reviewer's setting (mp4v): accepted tracks keep the displacement within 3 % (the codec's
    smearing of a noise texture costs ~1 %), never the 20 % shortfall of whole-box templates."""
    cs = _textured_video(tmp_path / "t.mp4", 90, 14, 25, 1.0, fourcc="mp4v")
    obs = _loose_boxes(cs, 14, 1.7)
    got, info = dt.dense_motion(dt.decode(str(tmp_path / "t.mp4"), set(range(90))), obs, FPS)
    assert got is None or abs(_disp_error(got, obs, cs)) < 0.03, (info.get("scale"), info.get("why"))


def test_chain_scale_measures_the_slope_with_the_prior_noise():
    rng = np.random.default_rng(0)
    chain = np.c_[np.linspace(0, 100, 11), np.linspace(0, 30, 11)]
    refs = 5.0 + 1.1 * chain + rng.normal(0, 0.1, chain.shape)        # over-regular annotator points
    beta, se, u = dt.chain_scale(chain, refs, sig=2.0)
    assert beta == pytest.approx(1.1, abs=0.01)
    x = (chain - chain.mean(0)) @ u
    assert se == pytest.approx(2.0 / math.sqrt(x @ x))                 # prior noise, not the 0.1 scatter
    assert dt.chain_scale(chain[:1], refs[:1], 2.0)[1] == math.inf


def _occluded_car_video(path, n, v_car, v_bike, seed=0):
    """A 160 x 50 px 'car' with a disc 'cyclist' riding faster in front of its lower half."""
    W, H = 640, 360
    rng = np.random.default_rng(seed)
    bg = cv2.GaussianBlur(rng.normal(90, 25, (H, W, 3)).astype(np.float32), (0, 0), 3.0).astype(np.uint8)
    vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"FFV1"), FPS, (W, H))
    cars = []
    for i in range(n):
        car, bike = np.array([450.0 - v_car * i, 180.0]), np.array([470.0 - v_bike * i, 195.0])
        img = bg.copy()
        x0, y0 = int(round(car[0] - 80)), int(round(car[1] - 25))
        cv2.rectangle(img, (x0, y0), (x0 + 159, y0 + 49), (40, 200, 230), -1)
        cv2.rectangle(img, (x0 + 30, y0 + 5), (x0 + 70, y0 + 20), (60, 60, 60), -1)
        cv2.circle(img, (int(round(bike[0])), int(round(bike[1]))), 16, (200, 60, 40), -1, cv2.LINE_AA)
        vw.write(img)
        cars.append(car)
    vw.release()
    return cars


def test_drift_onto_a_passing_occluder_is_rejected(tmp_path):
    """simulation_0060's yellow car: the template (the car's size, borrowed from another track) also
    holds a faster cyclist and the path slides along the car (+40-80 % displacement) while the
    annotator's points stay ~12 px off it - within 0.35 x the 160 px car (the old tolerance), far
    beyond an annotator's few pixels: rejected by the residual (a chain longer than the annotator's
    points is no template lag, so the chain-scale check leaves it to the residual)."""
    cars = _occluded_car_video(tmp_path / "c.avi", 60, 1.0, 3.0)
    rng = np.random.default_rng(2)
    obs = [Obs(t=f / FPS, point=list(cars[f] + rng.normal(0, 1.0, 2))) for f in range(0, 60, 5)]
    win = dt.decode(str(tmp_path / "c.avi"), set(range(60)))
    got, info = dt.dense_motion(win, obs, FPS, lambda f: (160.0, 50.0))
    assert got is None and info["why"] == "residual", info
    assert info["scale"][0][0] < 0.8                                        # the chain spans far more
    assert info["resid_tol"] == pytest.approx(dt.RESID_TOL * dt.ANCHOR_SIG) and info["resid_med"] < 0.35 * 160


def test_a_chain_longer_than_under_read_anchors_is_kept(tmp_path):
    """simulation_0196's bubble: a slow object the annotator saw at a fraction of the resolution and
    read as equal steps of half its true motion. The chain (and optical flow, and the ground truth)
    say otherwise; a longer chain is no template lag, and its residuals are small in the pixels the
    annotator saw: kept, with the chain's scale (the annotator's points barely constrain it)."""
    cs = _textured_video(tmp_path / "t.avi", 90, 24, 40, 0.5)
    rng = np.random.default_rng(3)
    seen = 0.2                                                               # the annotator saw 128 x 72
    obs = [Obs(t=f / FPS, point=list(cs[0] + 0.5 * (cs[f] - cs[0]) + rng.normal(0, 0.3 / seen, 2)))
           for f in range(0, 85, 12)]                                        # reads half the motion
    win = dt.decode(str(tmp_path / "t.avi"), set(range(90)))
    got, info = dt.dense_motion(win, obs, FPS, lambda f: (48.0, 48.0), seen_scale=seen)
    assert got is not None, info
    assert info["scale"][0][0] < 0.7 and info["scale"][0][2] < 1.01        # chain kept at its own scale
    assert abs(_disp_error(got, obs, cs)) < 0.05, _disp_error(got, obs, cs)


def test_residual_tolerance_is_in_the_annotators_pixels(tmp_path):
    ball = Body("ball", ballistic([-1.2, -0.3, 6.0], [0.8, 0.2, 0.0]), size=0.35, color=(30, 60, 220))
    path, n = _render(tmp_path, [ball])
    obs = _sparse(ball, range(2, n - 2, 7), noise=1.0)
    win = dt.decode(path, set(range(n)))
    for seen in (1.0, 0.25):
        got, info = dt.dense_motion(win, obs, FPS, seen_scale=seen)
        assert got is not None and info["resid_tol"] == pytest.approx(dt.RESID_TOL * dt.ANCHOR_SIG / seen)


def test_borrowed_sizes_only_from_boxes_framing_the_track():
    obs = [Obs(t=0.1 * k, point=[100.0 + 10 * k, 50.0]) for k in range(6)]     # x = 100 + 100 t
    boxes = [(0.2, (40.0, 20.0), (121.0, 52.0)),     # around the track's point at t = 0.2: kept
             (0.3, (40.0, 20.0), (300.0, 50.0)),     # another object of the same name: dropped
             (0.4, (40.0, 20.0), (140.0, 59.0)),     # centre 9 px below (> 0.35 x 20): dropped
             (2.0, (40.0, 20.0), (300.0, 50.0))]     # long after the track: dropped
    assert dt.borrowed_sizes(obs, boxes) == [(0.2, (40.0, 20.0))]
    assert dt.borrowed_sizes([Obs(t=0.0, box=[0, 0, 4, 4])], boxes) == []


def test_grabcut_is_deterministic_whatever_the_global_rng():
    """GrabCut seeds its colour models by k-means on OpenCV's global RNG: without a fixed seed the
    extent of this fuzzy textured disc varied by ~1.4 % with whatever ran before (and the first draw
    was cached)."""
    rng = np.random.default_rng(5)
    bg = cv2.GaussianBlur(rng.normal(110, 40, (80, 80, 3)).astype(np.float32), (0, 0), 1.2)
    obj = cv2.GaussianBlur(rng.normal(140, 40, (80, 80, 3)).astype(np.float32), (0, 0), 1.2) * [0.6, 1.0, 1.0]
    m = np.zeros((80, 80), np.float32)
    cv2.circle(m, (40, 40), 18, 1.0, -1, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), 2.0)[..., None]
    img = np.clip(bg * (1 - m) + obj * m, 0, 255).astype(np.uint8)
    got, weights = set(), set()
    for k in range(5):
        cv2.setRNGSeed(1000 + 7 * k)   # other OpenCV work in the process
        e, _ = dt.grabcut_extent(img, [21.0, 21.0, 59.0, 59.0], "diameter", "ball")
        got.add(None if e is None else round(dt._length(e), 6))
        cv2.setRNGSeed(77 + k)
        w, how = dt.template_weight(img, (39.5, 39.5), (39, 39))
        weights.add((how, None if w is None else float(w.sum())))
    assert len(got) == 1 and None not in got and len(weights) == 1


def _job(obs, seen=1.0):
    return dt.Job("motion", obs, FPS, CAM.size, seen, "ball")


def test_motion_cache_key_covers_borrowed_sizes_and_seen_scale():
    obs = [Obs(t=0.1 * k, point=[100.0 + 10 * k, 50.0]) for k in range(6)]
    fid = ("v.mp4", 123)
    base = _job(obs).key(fid, "grabcut", [(0.2, (40.0, 20.0))])
    assert base == _job(list(obs)).key(fid, "grabcut", [(0.2, (40.0, 20.0))])
    assert base != _job(obs).key(fid, "grabcut", [(0.2, (44.0, 20.0))])
    assert base != _job(obs).key(fid, "grabcut", [])
    assert base != _job(obs, 0.5).key(fid, "grabcut", [(0.2, (40.0, 20.0))])


def test_cache_survives_a_corrupt_file_and_concurrent_writers(tmp_path):
    d = tmp_path / "cache"
    d.mkdir()
    (d / "v.json").write_text('{"abc": {"path": nul')                     # truncated write
    c = dt.Cache(d)
    with pytest.warns(UserWarning, match="unreadable"):
        loaded = c.load("/x/v.mp4")
    assert loaded == {}
    assert (d / "v.json.bad").exists() and not (d / "v.json").exists()
    c.mem["/x/v.mp4"]["k1"] = {"path": None}
    other = dt.Cache(d)                                                       # another process
    other.load("/x/v.mp4")
    c.save("/x/v.mp4")
    other.mem["/x/v.mp4"]["k2"] = {"path": None}
    other.save("/x/v.mp4")                                                    # keeps k1
    assert set(json.loads((d / "v.json").read_text())) == {"k1", "k2"}
    assert not list(d.glob("*.tmp"))


def test_corrupt_cache_file_does_not_disable_the_video(tmp_path):
    ball = Body("ball", ballistic([-1.2, -0.3, 6.0], [0.8, 0.2, 0.0]), size=0.35, color=(30, 60, 220))
    path, n = _render(tmp_path, [ball])
    pts = [Obs(t=o.t, point=o.point) for o in _sparse(ball, range(2, n - 2, 7), noise=1.0)]
    sizes = track(ball, "prior", [0.5, 1.0], CAM, box=True).obs
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "v.json").write_text("{")
    a = _annotation(sizes, pts)
    with pytest.warns(UserWarning):
        dt.densify_annotations({7: a}, {7: path}, {7: (FPS, CAM.size, 1.0)}, cache_dir=cache)
    assert "dense_error" not in a.flags and "dense_motion" in a.flags
    assert json.loads((cache / "v.json").read_text())


def test_in_process_run_keeps_the_opencv_thread_count(tmp_path):
    ball = Body("ball", ballistic([-1.2, -0.3, 6.0], [0.8, 0.2, 0.0]), size=0.35, color=(30, 60, 220))
    path, n = _render(tmp_path, [ball])
    a = _annotation(track(ball, "prior", [0.5, 1.0], CAM, box=True).obs,
                    [Obs(t=o.t, point=o.point) for o in _sparse(ball, range(2, n - 2, 7), noise=1.0)])
    before = cv2.getNumThreads()
    cv2.setNumThreads(3)
    try:
        dt.densify_annotations({7: a}, {7: path}, {7: (FPS, CAM.size, 1.0)}, workers=1)
        assert cv2.getNumThreads() == 3
    finally:
        cv2.setNumThreads(before)
