"""qp.claude_verify and scripts/run_claude_verify.py with a fake client (no API traffic)."""

import importlib.util
import json
import math
import re
from pathlib import Path
from types import SimpleNamespace

import cv2
import numpy as np
import pandas as pd
import pytest

from qp import budget
from qp import claude_verify as cvf
from qp.spec import Obs, Quantity, QuestionSpec

ROOT = Path(__file__).resolve().parents[1]
FPS = 10
W, H = 320, 240
R = 10                     # ball radius (px)
VX = 6.0                   # ball speed, px per frame -> 60 px/s; prior 2 m/s -> 1/30 m/px


def _load_script():
    spec = importlib.util.spec_from_file_location("run_claude_verify", ROOT / "scripts" / "run_claude_verify.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rcv = _load_script()


def ball_x(i: int) -> float:
    return 40 + VX * i


def make_video(path: Path, n: int = 30) -> Path:
    vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W, H))
    for i in range(n):
        img = np.full((H, W, 3), 60, np.uint8)
        cv2.circle(img, (int(round(ball_x(i))), 120), R, (255, 255, 255), -1)
        vw.write(img)
    vw.release()
    return path


# --------------------------------------------------------------------------- rendering

def _centroid(img: np.ndarray, colour, near=None, radius: float = 1e9) -> tuple[float, float]:
    """Intensity-weighted centroid (cv2 pixel-index coordinates) of pixels close to `colour`, optionally
    only those within `radius` of `near`."""
    c = np.asarray(colour, float)
    diff = np.abs(img.astype(float) - c).max(axis=2)
    w = np.clip(1 - diff / 160, 0, None)
    ys, xs = np.mgrid[:img.shape[0], :img.shape[1]]
    if near is not None:
        w = w * (np.hypot(xs - near[0], ys - near[1]) <= radius)
    return float((w * xs).sum() / w.sum()), float((w * ys).sum() / w.sum())


@pytest.mark.parametrize("zoom,x0,y0,pt", [(4, 100, 50, (131.5, 77.25)), (3, 0, 0, (20.0, 33.7)),
                                           (2, 37, 12, (60.25, 40.5)), (0.5, 0, 0, (200.0, 150.0))])
def test_cross_marker_lands_on_the_original_coordinate(zoom, x0, y0, pt):
    region = np.zeros((60, 80, 3), np.uint8) if zoom >= 1 else np.zeros((400, 600, 3), np.uint8)
    cv = cvf.make_canvas(region, x0, y0, zoom)
    cvf.draw_cross(cv, *pt, (0, 255, 0), arm=14, gap=7, ring=5)
    u, v = _centroid(cv.img, (0, 255, 0))
    x, y = cv.to_orig(u + 0.5, v + 0.5)   # pixel index -> continuous (pixel centres at +0.5)
    assert x == pytest.approx(pt[0], abs=0.15 / max(zoom, 1)) and y == pytest.approx(pt[1], abs=0.15 / max(zoom, 1))


def test_canvas_transform_roundtrip_and_resize_convention():
    region = np.zeros((10, 10, 3), np.uint8)
    region[4, 6] = 255                     # pixel (x=6, y=4): centre at continuous (6.5, 4.5)
    cv = cvf.make_canvas(region, 200, 300, 4)
    assert cv.to_orig(*cv.to_out(203.25, 301.5)) == pytest.approx((203.25, 301.5))
    u, v = _centroid(cv.img, (255, 255, 255))
    assert cv.to_orig(u + 0.5, v + 0.5) == pytest.approx((206.5, 304.5), abs=0.05)


def test_tick_marks_sit_at_their_labelled_coordinates():
    region = np.zeros((50, 50, 3), np.uint8)
    cv = cvf.make_canvas(region, 120, 80, 4)
    step = cvf.draw_ticks(cv, 50, 50, 36, grid=False)
    assert step == 10
    row = cv.img[cv.mt - 5]                # crosses the major ticks only (minor ticks are 3 px long)
    cols = np.flatnonzero(row.max(axis=1) > 150)
    groups = np.split(cols, np.flatnonzero(np.diff(cols) > 1) + 1)
    centres = [g.mean() + 0.5 for g in groups if len(g)]
    labelled = [cv.to_orig(c, 0)[0] for c in centres]
    assert labelled == pytest.approx([120, 130, 140, 150, 160, 170], abs=0.3)


def _ctx(obs_a, obs_b, use_b="size", qkind="size", window=None):
    spec = QuestionSpec(qid=1, target=Quantity(qkind, ["ball"], "diameter" if qkind == "size" else "", window=window,
                                               unit="cm"),
                        prior=Quantity("speed", ["ball"], value_si=2.0))
    tracks = {"A": cvf.Track("A", "ball", obs_a, uses=[{"qid": 1, "role": "prior", "use": "motion"}]),
              "B": cvf.Track("B", "ball", obs_b, uses=[{"qid": 1, "role": "target", "use": use_b}])}
    q = cvf.QCtx(qid=1, question="What is the diameter of the ball in cm?", prior_text="speed of the ball = 2m/s",
                 depth_info="", category="D2", spec=spec, roles=[["prior", "A"], ["target", "B"]], direct=60.0,
                 confidence=0.5, ann_flags=[])
    return cvf.VideoContext("v", "", FPS, (W, H), 30, "V2SC", "simulation", tracks, [q])


def test_rendered_crop_markers_match_the_listed_numbers():
    pts = [Obs(t=i / FPS, point=[ball_x(i), 120.0]) for i in range(0, 30, 3)]
    ext = [Obs(t=0.6, extent=[[ball_x(6) - R + 0.5, 120.0], [ball_x(6) + R - 0.5, 120.0]], box=[70, 110, 90, 130])]
    ctx = _ctx(pts, ext)
    frame = np.full((H, W, 3), 0, np.uint8)
    plan = cvf.plan_evidence(ctx)
    ev = cvf.render_evidence(ctx, plan, frames={f: frame for f in plan["frames"]})
    crops = [e for e in ev if e["kind"] == "crop"]
    assert crops and all(e["zoom"] in (2, 3, 4) for e in crops)
    lime = cvf.PALETTE[1][1]               # track B is the second track: magenta
    for e in crops:
        x0, y0, x1, y1 = e["region"]
        for what in e["what"]:
            if not what.startswith("B"):
                continue
            for x, y in [tuple(map(float, m)) for m in re.findall(r"\(([-\d.]+), ([-\d.]+)\)", what)]:
                img = cv2.imdecode(np.frombuffer(__import__("base64").b64decode(e["jpeg_b64"]), np.uint8), 1)
                u = cvf.MARGIN_L + (x - x0) * e["zoom"] - 0.5
                v = cvf.MARGIN_T + (y - y0) * e["zoom"] - 0.5
                cu, cv_ = _centroid(img, lime, near=(u, v), radius=6.5)   # the endpoint ring
                assert (cu, cv_) == pytest.approx((u, v), abs=0.6)
                assert x0 <= x <= x1 and y0 <= y <= y1


def test_plan_picks_frames_the_answer_rests_on():
    pts = [Obs(t=i / FPS, point=[ball_x(i), 120.0]) for i in range(30)]
    ext = [Obs(t=f / FPS, extent=[[ball_x(f) - R, 120.0], [ball_x(f) + R + d, 120.0]])
           for f, d in ((2, 0), (10, 1), (20, 30))]
    ctx = _ctx(pts, ext)
    ctx.questions[0].spec.prior.window = [0.5, 2.0]
    picks = cvf.evidence_obs(ctx.tracks["A"], {1: ctx.questions[0]})
    assert [round(o.t * FPS) for o, _ in picks] == [5, 20, 12]          # window ends, then the middle
    picks = cvf.evidence_obs(ctx.tracks["B"], {1: ctx.questions[0]})
    assert [round(o.t * FPS) for o, _ in picks] == [10, 20]             # median length, then the farthest frame
    plan = cvf.plan_evidence(ctx)
    long_ends = [c for c in plan["crops"] if c.frame == 20 and any("B end" in w for w in c.what)]
    assert len(long_ends) == 2                                           # a 50 px extent: one crop per end
    short = [c for c in plan["crops"] if c.frame == 10 and any(w.startswith("B end 1") for w in c.what)]
    assert len(short) == 1 and "end 2" in short[0].what[0]               # a 21 px extent: one crop for both
    assert set(plan["per_track"]["A"]) == {5, 12, 20}


# --------------------------------------------------------------------------- workspace (pass-1 run on a synthetic video)

def _q(kind, objects, dimension="", time=None, window=None, axis="any", value_si=None, unit=""):
    return {"kind": kind, "objects": objects, "dimension": dimension, "time": time, "window": window, "axis": axis,
            "value_si": value_si, "unit": unit}


def _pass1_parsed(diam_px: float = 16.0) -> dict:
    """Pass 1: exact ball points; ball extents `diam_px` wide (the true diameter is 20 px)."""
    pts = [{"frame": i, "point": [ball_x(i), 120.0], "extent": None, "box": None} for i in range(0, 30, 2)]
    ext = [{"frame": f, "point": None, "extent": [[ball_x(f) - diam_px / 2, 120.0], [ball_x(f) + diam_px / 2, 120.0]],
            "box": None} for f in (4, 10, 16)]
    return {"questions": [
        {"qid": 101, "spec": {"target": _q("size", ["ball"], "diameter", unit="cm"),
                              "prior": _q("speed", ["ball"], value_si=2.0), "depth": [], "notes": ""},
         "tracks": [{"role": "prior", "object": "ball", "obs": pts}, {"role": "target", "object": "ball", "obs": ext}],
         "direct_answer": 60.0, "confidence": 0.5},
        {"qid": 102, "spec": {"target": _q("speed", ["ball"], time=1.2, unit="m/s"),
                              "prior": _q("speed", ["ball"], value_si=2.0), "depth": [], "notes": ""},
         "tracks": [{"role": "prior", "object": "ball", "obs": []}, {"role": "target", "object": "ball", "obs": []}],
         "direct_answer": 2.1, "confidence": 0.5}]}


@pytest.fixture
def ws(tmp_path, monkeypatch):
    videos = tmp_path / "videos"
    videos.mkdir()
    make_video(videos / "vid_a.mp4")
    df = pd.DataFrame([("vid_a", "V2SC", "DS", "What is the diameter of the ball in cm?", "speed of the ball = 2m/s", "",
                        200 / 3),
                       ("vid_a", "V2SC", "DD", "What is the speed of the ball at 1.2s in m/s?", "speed of the ball = 2m/s",
                        "", 2.0)],
                      columns=["video_id", "video_type", "inference_type", "question", "ground_truth_prior",
                               "depth_info", "ground_truth_posterior"])
    df.insert(0, "", [101, 102])
    df.insert(3, "fps", FPS)
    csv = tmp_path / "qs.csv"
    df.to_csv(csv, index=False)
    monkeypatch.setattr(rcv.rc, "ROOT", tmp_path)   # no .env from the repo
    monkeypatch.setenv("QP_LEDGER", str(tmp_path / "ledger.jsonl"))
    monkeypatch.setenv("QP_BUDGET_USD", "50")
    monkeypatch.setattr(rcv.rc, "REFINE_PRIORS", False)
    runs = tmp_path / "runs"
    meta = {"video_id": "vid_a", "fps": FPS, "fps_from_container": False, "video_type": "V2SC", "n_frames_total": 30,
            "scale": 1.0, "image_size": [W, H], "frames": list(range(30)), "prompt_version": "v1",
            "questions": [{"qid": 101, "target_unit": "cm", "prior": "speed of the ball = 2m/s", "depth_info": ""},
                          {"qid": 102, "target_unit": "m/s", "prior": "speed of the ball = 2m/s", "depth_info": ""}]}
    rc_rec = {"video_id": "vid_a", "status": "ok", "model": cvf.MODEL, "effort": "high", "config": {},
              "meta": meta, "parsed": _pass1_parsed(), "usage": {}, "usd": 0.0}
    rcv.rc.save_record(runs / "p1" / "qs" / "records", rc_rec)
    return SimpleNamespace(root=tmp_path, videos=videos, csv=csv, runs=runs)


def _rows(ws):
    args = rcv.rc.parse_args(["--csv", str(ws.csv), "--video-dir", str(ws.videos), "--name", "t"])
    return rcv.rc.load_questions(args)[0]


def _ctx_ws(ws):
    df = _rows(ws)
    p1 = rcv.rc.load_records(ws.runs / "p1" / "qs" / "records")
    return cvf.build_contexts(df, p1, refine_priors=False)["vid_a"]


def test_contexts_dedupe_shared_tracks_and_reproduce_pass1(ws):
    ctx = _ctx_ws(ws)
    assert list(ctx.tracks) == ["A", "B"]            # q102 reuses q101's tracks (same object, same obs)
    assert ctx.questions[1].roles == [["prior", "A"], ["target", "A"]]
    uses = {(u["qid"], u["role"], u["use"]) for u in ctx.tracks["A"].uses}
    assert uses == {(101, "prior", "motion"), (102, "prior", "motion"), (102, "target", "motion")}
    p1 = cvf.pass1_answers(ctx)
    assert p1[101]["chosen"][0] == pytest.approx(16 / 30 * 100, rel=1e-3)   # 16 px at 1/30 m/px, in cm
    res = rcv.rc.build_results(_rows(ws), rcv.rc.load_records(ws.runs / "p1" / "qs" / "records"))
    assert res.set_index("id").parsed_value[101] == pytest.approx(p1[101]["chosen"][0])
    assert res.set_index("id").parsed_value[102] == pytest.approx(p1[102]["chosen"][0])


def test_build_request_images_labels_and_schema(ws):
    ctx = _ctx_ws(ws)
    params, meta = cvf.build_request(ctx, effort="medium")
    content = params["messages"][0]["content"]
    images = [b for b in content if b["type"] == "image"]
    labels = [b["text"] for b in content if b["type"] == "text" and b["text"].startswith("[Image")]
    assert len(images) == len(labels) == len(meta["evidence"]) > 0
    assert params["output_config"] == {"effort": "medium", "format": {"type": "json_schema", "schema": cvf.SCHEMA}}
    assert params["max_tokens"] == cvf.default_max_tokens(2, 2)
    text = "\n".join(b["text"] for b in content if b["type"] == "text")
    assert "Track A (cyan)" in text and "Track B (magenta)" in text and "qid=101" in text and "qid=102" in text
    assert "extent (56.0, 120.0)-(72.0, 120.0) = 16.0 px" in text            # frame 4 extent, original pixels
    assert "scale 0.033333 m/px" in text and "geometry answer: 53.33 cm" in text
    for e, lab in zip(meta["evidence"], labels):
        x0, y0, x1, y1 = e["region"]
        assert f"x {x0}-{x1}, y {y0}-{y1}" in lab and f"frame {e['frame']} " in lab
        img = cv2.imdecode(np.frombuffer(__import__("base64").b64decode(images[e["iid"] - 1]["source"]["data"]),
                                         np.uint8), 1)
        assert img.shape[1] == e["width"] and img.shape[0] == e["height"]
    assert meta["frames_shown"] == sorted({e["frame"] for e in meta["evidence"]})
    assert json.loads(json.dumps(meta)) == meta                            # stored as JSON in the record
    _strict(cvf.SCHEMA)


def _strict(node):
    if isinstance(node, dict):
        if node.get("type") == "object":
            assert node["additionalProperties"] is False and set(node["required"]) == set(node["properties"])
        for v in node.values():
            _strict(v)
    elif isinstance(node, list):
        for v in node:
            _strict(v)


def _keep_all(meta, final=None):
    nofix = {"change": [], "kind": None, "objects": None, "dimension": None, "time": None, "window": None, "axis": None}
    return {"tracks": [{"track": t, "action": "keep", "problem": "", "depth_name": None, "obs": []} for t in meta["tracks"]],
            "questions": [{"qid": q["qid"], "verdict": "accept_geometry", "problem": "",
                           "spec_fix": {"target": dict(nofix), "prior": dict(nofix)},
                           "final_answer": final or 1.0, "confidence": 0.5} for q in meta["questions"]]}


def _fixed(meta, diam_px=20.0, final=66.0):
    out = _keep_all(meta)
    frames = meta["frames_shown"]
    out["tracks"][1] = {"track": "B", "action": "replace", "problem": "extent short of the edges", "depth_name": None,
                        "obs": [{"frame": f, "point": None, "box": None,
                                 "extent": [[ball_x(f) - diam_px / 2, 120.0], [ball_x(f) + diam_px / 2, 120.0]]}
                                for f in frames]}
    out["questions"][0].update(verdict="corrected", final_answer=final)
    return out


def _remeasured(meta, diam_px=20.0, motion_shift=0.0):
    """vf2-style: every track kept, with readings on every shown frame (ball extents `diam_px` wide,
    motion points shifted by `motion_shift`)."""
    out = _keep_all(meta)
    frames = meta["frames_shown"]
    out["tracks"][0]["obs"] = [{"frame": f, "point": [ball_x(f) + motion_shift, 120.0], "extent": None, "box": None}
                               for f in frames]
    out["tracks"][1]["obs"] = [{"frame": f, "point": None, "box": None,
                                "extent": [[ball_x(f) - diam_px / 2, 120.0], [ball_x(f) + diam_px / 2, 120.0]]}
                               for f in frames]
    return out


def test_remeasure_rule_uses_readings_of_size_tracks_only(ws):
    ctx = _ctx_ws(ws)
    _, meta = cvf.build_request(ctx)
    resp = _remeasured(meta, motion_shift=3.0)
    for q in resp["questions"]:
        q["final_answer"] = 66.0 if q["qid"] == 101 else 2.0
    ver = {r["id"]: r for r in cvf.recompute(meta, resp, rule="verify")}
    assert ver[101]["verify_how"] == "pass1" and ver[101]["delta_px"] == pytest.approx(3.0)   # readings: 2 px wider each side, motion 3 px
    rem = {r["id"]: r for r in cvf.recompute(meta, resp, rule="remeasure")}
    assert rem[101]["verify_how"] == "recomputed" and rem[101]["parsed_value"] == pytest.approx(200 / 3, rel=1e-3)
    assert rem[102]["verify_how"] == "pass1"      # the motion track keeps its pass-1 points
    tracks, info = cvf.apply_track_fixes(cvf.context_from_meta(meta), resp, set(meta["frames_shown"]), remeasure=True)
    assert info["A"]["applied"] is False and info["B"]["applied"] is True
    assert info["A"]["delta_px"] == pytest.approx(3.0) and info["B"]["delta_px"] == pytest.approx(2.0)


def test_reading_delta_matches_extent_ends_in_either_order():
    t = cvf.Track("A", "x", [Obs(t=0.0, extent=[[0, 0], [10, 0]]), Obs(t=0.1, point=[5, 5])])
    got = [Obs(t=0.0, extent=[[10, 1], [0, 0]]), Obs(t=0.1, point=[8, 9]), Obs(t=0.2, point=[0, 0])]
    assert cvf.reading_delta(t, got, FPS) == pytest.approx(5.0)
    assert cvf.reading_delta(t, [Obs(t=0.5, point=[0, 0])], FPS) is None


def test_request_versions(ws):
    ctx = _ctx_ws(ws)
    p2, m2 = cvf.build_request(ctx)
    p1, m1 = cvf.build_request(ctx, version="vf1")
    assert p2["system"][0]["text"] == cvf.SYSTEM and "ALWAYS your own reading" in cvf.SYSTEM
    assert p1["system"][0]["text"] == cvf.SYSTEM_VF1 and m1["verify_version"] == "vf1" and m2["verify_version"] == "vf2"
    assert p1["messages"] == p2["messages"]
    with pytest.raises(ValueError):
        cvf.build_request(ctx, version="vf9")


def test_schema_accepts_a_response():
    jsonschema = pytest.importorskip("jsonschema")
    meta = {"tracks": {"A": {}, "B": {}}, "questions": [{"qid": 101}], "frames_shown": [4, 10]}
    jsonschema.validate(_fixed(meta), cvf.SCHEMA)
    jsonschema.validate(_keep_all(meta), cvf.SCHEMA)
    jsonschema.validate(_remeasured(meta), cvf.SCHEMA)


def test_recompute_keep_correct_inconsistent_direct(ws):
    ctx = _ctx_ws(ws)
    _, meta = cvf.build_request(ctx)
    keep = cvf.recompute(meta, _keep_all(meta))
    assert [r["verify_how"] for r in keep] == ["pass1", "pass1"]
    assert keep[0]["parsed_value"] == pytest.approx(16 / 30 * 100, rel=1e-3) and keep[0]["method"] == "geometry:2d_scale"
    fixed = {r["id"]: r for r in cvf.recompute(meta, _fixed(meta))}
    assert fixed[101]["verify_how"] == "recomputed" and fixed[101]["parsed_value"] == pytest.approx(200 / 3, rel=1e-3)
    assert fixed[101]["geo2_value"] == pytest.approx(200 / 3, rel=1e-3) and "verify_touched" in fixed[101]["flags"]
    assert fixed[102]["verify_how"] == "pass1"            # track B is not one of q102's tracks
    # the model's own number disagrees with its coordinates (e.g. it gave crop pixels): pass-1 answer kept
    bad = {r["id"]: r for r in cvf.recompute(meta, _fixed(meta, final=20.0))}
    assert bad[101]["verify_how"] == "pass1" and "verify_inconsistent" in bad[101]["flags"]
    # accept_direct -> the pass-1 direct answer; geo_value blank so combine_runs re-selects the same
    d = _keep_all(meta)
    d["questions"][0]["verdict"] = "accept_direct"
    r = cvf.recompute(meta, d)[0]
    assert r["parsed_value"] == 60.0 and r["method"] == "direct" and math.isnan(r["geo_value"])
    # other rules
    assert cvf.recompute(meta, _fixed(meta), rule="verify_final")[0]["parsed_value"] == 66.0
    assert cvf.recompute(meta, _fixed(meta), rule="pass1")[0]["parsed_value"] == pytest.approx(16 / 30 * 100, rel=1e-3)
    vd = _fixed(meta, final=66.0)
    vd["questions"][0]["verdict"] = "accept_direct"
    assert cvf.recompute(meta, vd, rule="verify_vdirect")[0]["parsed_value"] == 66.0
    # nothing parsed: every question keeps its pass-1 answer, flagged
    miss = cvf.recompute(meta, None)
    assert all(r["verify_how"] == "pass1" and "verify_missing" in r["flags"] for r in miss)


def test_track_fix_validation(ws):
    ctx = _ctx_ws(ws)
    _, meta = cvf.build_request(ctx)
    shown = set(meta["frames_shown"])
    hidden = next(f for f in range(30) if f not in shown)
    fixes = {"tracks": [
        {"track": "A", "action": "replace", "problem": "", "depth_name": None,     # motion: one usable point only
         "obs": [{"frame": min(shown), "point": [10, 10], "extent": None, "box": None},
                 {"frame": hidden, "point": [20, 20], "extent": None, "box": None}]},
        {"track": "B", "action": "replace", "problem": "", "depth_name": "ball",   # 2D: depth_name ignored
         "obs": [{"frame": min(shown), "point": None, "extent": [[0, 0], [5000, 0]], "box": None}]},
        {"track": "Z", "action": "replace", "problem": "", "depth_name": None, "obs": []}]}
    tracks, info = cvf.apply_track_fixes(cvf.context_from_meta(meta), fixes, shown)
    assert not info["A"]["applied"] and {"verify_unknown_frame", "verify_replace_unusable"} <= set(info["A"]["flags"])
    assert not info["B"]["applied"] and "verify_outside_frame" in info["B"]["flags"]
    assert "Z" not in info and tracks["A"].obs == ctx.tracks["A"].obs


def test_spec_fix_fields_and_dimension_guard():
    spec = QuestionSpec(qid=1, target=Quantity("speed", ["ball"], time=1.0, unit="m/s"),
                        prior=Quantity("size", ["ball"], "diameter", value_si=0.2))
    flags = []
    fix = {"target": {"change": ["window", "time", "kind"], "kind": "displacement", "time": None, "window": [2.0, 1.0],
                      "objects": None, "dimension": None, "axis": None},
           "prior": {"change": ["dimension", "axis"], "dimension": "height", "axis": "vertical", "kind": "speed",
                     "time": 5.0, "window": None, "objects": None}}
    out = cvf.apply_spec_fix(spec, fix, "m/s", flags)
    assert out.target.window == [1.0, 2.0] and out.target.time is None and out.target.kind == "speed"
    assert "verify_target_kind_rejected" in flags                       # m/s asked: not a displacement
    assert out.prior.dimension == "height" and out.prior.axis == "vertical" and out.prior.kind == "size"
    assert out.prior.time is None                                       # not listed in "change"
    assert spec.target.window is None                                   # the input is not modified


# --------------------------------------------------------------------------- CLI with a fake client

def _fake_message(params, n=1, mode="fix"):
    text = params["messages"][0]["content"][-1]["text"]
    meta = {"tracks": {t: {} for t in re.search(r"Answer every track \(([^)]*)\)", text).group(1).split(", ")},
            "questions": [{"qid": int(q)} for q in re.search(r"every question \(([^)]*)\)", text).group(1).split(", ")],
            "frames_shown": json.loads(re.search(r"replaced tracks: (\[[^\]]*\])", text).group(1))}
    resp = _fixed(meta) if mode == "fix" else _keep_all(meta)
    return SimpleNamespace(
        id=f"msg_{n}", stop_reason="end_turn", stop_details=None,
        content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=json.dumps(resp))],
        usage=SimpleNamespace(input_tokens=5000, output_tokens=3000, cache_creation_input_tokens=0,
                              cache_read_input_tokens=0, cache_creation=None))


class FakeStream:
    def __init__(self, msg):
        self.msg, self.request_id = msg, "req_fake"

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get_final_message(self):
        return self.msg


class FakeBatches:
    def __init__(self):
        self.created, self.status = [], {}

    def create(self, requests):
        bid = f"msgbatch_{len(self.created) + 1}"
        self.created.append((bid, list(requests)))
        self.status[bid] = "ended"
        return SimpleNamespace(id=bid, processing_status="in_progress")

    def retrieve(self, bid):
        counts = SimpleNamespace(processing=0, succeeded=1, errored=0, expired=0, canceled=0)
        return SimpleNamespace(id=bid, processing_status=self.status[bid], request_counts=counts)

    def results(self, bid):
        for r in dict(self.created)[bid]:
            yield SimpleNamespace(custom_id=r["custom_id"],
                                  result=SimpleNamespace(type="succeeded", message=_fake_message(r["params"])))


class FakeClient:
    def __init__(self, mode="fix"):
        self.mode, self.counted, self.streamed = mode, 0, []
        self.batches = FakeBatches()
        self.messages = SimpleNamespace(batches=self.batches, count_tokens=self._count, stream=self._stream)

    def _count(self, **params):
        assert "max_tokens" not in params
        self.counted += 1
        return SimpleNamespace(input_tokens=4000)

    def _stream(self, **params):
        self.streamed.append(params)
        return FakeStream(_fake_message(params, len(self.streamed), self.mode))


def _argv(ws, *extra):
    return ["--csv", str(ws.csv), "--video-dir", str(ws.videos), "--name", "ver", "--from", "p1",
            "--out-root", str(ws.runs), "--no-refine", "--poll-interval", "0", *extra]


def test_sync_run_records_ledger_csv_and_resume(ws):
    client = FakeClient()
    res = rcv.main(_argv(ws, "--save-evidence"), client=client)
    assert client.counted == 1 and len(client.streamed) == 1
    rec = rcv.rc.load_records(ws.runs / "ver" / "qs" / "records")["vid_a"]
    assert rec["status"] == "ok" and rec["config"]["from_run"] == "p1" and rec["meta"]["tracks"]
    led = budget.entries()
    assert len(led) == 1 and led[0]["mode"] == "sync" and led[0]["run"] == "ver" and led[0]["video_id"] == "vid_a"
    assert led[0]["usd"] == pytest.approx(5000 * 4e-6 + 3000 * 20e-6)
    assert list(res.columns) == cvf.COLUMNS
    r = res.set_index("id")
    assert r.parsed_value[101] == pytest.approx(200 / 3, rel=1e-3) and r.pass1_value[101] == pytest.approx(160 / 3, rel=1e-3)
    assert r.verify_how[101] == "recomputed" and r.verdict[102] == "accept_geometry"
    assert (ws.runs / "ver" / "qs.csv").exists() and list((ws.runs / "ver" / "qs" / "evidence" / "vid_a").glob("*.jpg"))
    # the CSV re-selects to the same answers with qp.combine (scripts/combine_runs.py)
    meta = _rows(ws)
    sel = rcv.combine.select_table(pd.read_csv(ws.runs / "ver" / "qs.csv"), meta).set_index("id")
    assert sel.parsed_value.to_dict() == pytest.approx(r.parsed_value.to_dict())
    # rerun: cached, nothing sent; another rule re-scores without the API
    client2 = FakeClient()
    res2 = rcv.main(_argv(ws, "--rule", "pass1"), client=client2)
    assert not client2.streamed and client2.counted == 0 and len(budget.entries()) == 1
    assert res2.set_index("id").parsed_value[101] == pytest.approx(160 / 3, rel=1e-3)
    # other settings on the cached records: refused
    with pytest.raises(SystemExit, match="other settings"):
        rcv.main(_argv(ws, "--effort", "medium"), client=FakeClient())


def test_dry_run_and_budget_refusal(ws, monkeypatch):
    client = FakeClient()
    assert rcv.main(_argv(ws, "--dry-run"), client=client) is None
    assert client.counted == 1 and not client.streamed and not budget.entries()
    monkeypatch.setenv("QP_BUDGET_USD", "0.01")
    res = rcv.main(_argv(ws), client=client)
    assert not client.streamed and not budget.entries()
    assert res.set_index("id").verify_how[101] == "pass1_unverified"


def test_batch_run_holds_collects_and_releases(ws):
    client = FakeClient()
    res = rcv.main(_argv(ws, "--mode", "batch"), client=client)
    assert len(client.batches.created) == 1
    kinds = [e.get("type") for e in budget.entries()]
    assert kinds.count("hold") == 1 and kinds.count("usage") == 1 and kinds.count("release") == 1
    usage = next(e for e in budget.entries() if e.get("type") == "usage")
    assert usage["mode"] == "batch" and usage["usd"] == pytest.approx(0.5 * (5000 * 4e-6 + 3000 * 20e-6))
    assert res.set_index("id").parsed_value[101] == pytest.approx(200 / 3, rel=1e-3)
    state = json.loads((ws.runs / "ver" / "qs" / "batch.json").read_text())
    assert state["batches"][0]["collected"]
    # batch.json lost after collection: nothing re-sent
    (ws.runs / "ver" / "qs" / "batch.json").unlink()
    client2 = FakeClient()
    rcv.main(_argv(ws, "--mode", "batch"), client=client2)
    assert not client2.batches.created


def test_batch_recovered_from_ledger_rebuilds_meta(ws):
    client = FakeClient()
    rcv.main(_argv(ws, "--mode", "batch", "--no-wait"), client=client)  # submitted, then "ended" at the next look
    rec_dir = ws.runs / "ver" / "qs" / "records"
    for p in rec_dir.glob("*.json"):
        p.unlink()
    # lose the state before collection: the ledger hold names the batch; the meta is rebuilt
    (ws.runs / "ver" / "qs" / "batch.json").unlink()
    holds = budget.open_holds()
    if not holds:   # the first run already collected (the fake batch ends at once): re-open its hold
        bid = client.batches.created[0][0]
        e = next(e for e in budget.entries() if e.get("type") == "hold")
        budget.hold(e["run"], bid, e["usd"], split=e["split"], custom_ids=e["custom_ids"], config=e["config"])
    res = rcv.main(_argv(ws, "--mode", "batch"), client=client)
    assert len(client.batches.created) == 1                               # not bought again
    assert rcv.rc.load_records(rec_dir)["vid_a"]["status"] == "ok"
    assert res.set_index("id").parsed_value[101] == pytest.approx(200 / 3, rel=1e-3)
    assert sum(e.get("type", "usage") == "usage" for e in budget.entries()) == 1


def test_dense_tracks_replace_pass1_roles(ws, tmp_path):
    dense = tmp_path / "dense.json"
    ext = [{"t": f / FPS, "point": None, "extent": [[ball_x(f) - R, 120.0], [ball_x(f) + R, 120.0]], "box": None,
            "score": None} for f in (6, 12)]
    dense.write_text(json.dumps({"101": [{"role": "target", "object": "ball", "obs": ext, "source": "dense"}]}))
    df = _rows(ws)
    p1 = rcv.rc.load_records(ws.runs / "p1" / "qs" / "records")
    ctx = cvf.build_contexts(df, p1, refine_priors=False, dense=cvf.load_dense(str(dense)))["vid_a"]
    q = ctx.questions[0]
    tgt = ctx.tracks[dict(q.roles)["target"]]
    assert "dense_tracks" in q.ann_flags and tgt.source == "dense" and len(tgt.obs) == 2
    assert cvf.pass1_answers(ctx)[101]["chosen"][0] == pytest.approx(200 / 3, rel=1e-3)
    csv = tmp_path / "dense.csv"
    pd.DataFrame({"id": [101, 102], "parsed_value": [66.0, 2.0]}).to_csv(csv, index=False)
    ctx2 = cvf.build_contexts(df, p1, refine_priors=False, dense=cvf.load_dense(str(csv)))["vid_a"]
    assert ctx2.questions[0].dense_value == 66.0
    params, _ = cvf.build_request(ctx2)
    assert "Dense-tracking answer: 66" in params["messages"][0]["content"][-1]["text"]


@pytest.mark.skipif(not (ROOT / "runs" / "val_opus_high" / "val.csv").exists()
                    or not (ROOT / "data" / "QuantiPhy-validation").exists(), reason="cached val run not present")
def test_pass1_reproduced_on_cached_val_run():
    from qp.data import load_split
    df = load_split("val")
    vids = ["internet_0005", "simulation_0196"]
    recs = rcv.rc.load_records(ROOT / "runs" / "val_opus_high" / "val" / "records")
    ctxs = cvf.build_contexts(df[df.video_id.isin(vids)], {v: recs[v] for v in vids})
    ref = pd.read_csv(ROOT / "runs" / "val_opus_high" / "val.csv").set_index("id")
    # the run CSV includes run_claude's dense-motion post-step, which build_contexts does not apply
    # (dense tracks come in through `dense=`): compare the rows that step left unchanged
    dense_rows = ref["flags"].fillna("").str.contains("dense_motion")
    checked = 0
    for ctx in ctxs.values():
        for qid, a in cvf.pass1_answers(ctx).items():
            if not dense_rows[qid]:
                assert a["chosen"][0] == pytest.approx(ref.parsed_value[qid], rel=1e-9)
                checked += 1
    assert checked >= 4


# --------------------------------------------------------------------------- review fixes (regressions)

def _size_dist_ctx():
    """A 2D video with a motion prior (A), a size target whose extents vary in length over 5 frames (B,
    median 21 px; the evidence shows 2 of them) and a distance between two point tracks at t=1.0 (C, D)."""
    pts = [Obs(t=i / FPS, point=[ball_x(i), 120.0]) for i in range(30)]
    lens = {2: 18.0, 6: 20.0, 10: 21.0, 14: 25.0, 18: 30.0}
    ext = [Obs(t=f / FPS, extent=[[100.0, 60.0], [100.0 + L, 60.0]]) for f, L in lens.items()]
    c = [Obs(t=f / FPS, point=[50.0 + f, 200.0], box=[44.0 + f, 194.0, 56.0 + f, 206.0]) for f in range(4, 16, 2)]
    d = [Obs(t=f / FPS, point=[150.0 + 2 * f, 190.0]) for f in range(4, 16, 2)]
    prior = Quantity("speed", ["ball"], value_si=2.0)
    q1 = cvf.QCtx(qid=1, question="size?", prior_text="2 m/s", depth_info="", category="S2",
                  spec=QuestionSpec(qid=1, target=Quantity("size", ["bar"], "length", unit="cm"), prior=prior),
                  roles=[["prior", "A"], ["target", "B"]], direct=70.0, confidence=0.5, ann_flags=[])
    q2 = cvf.QCtx(qid=2, question="distance?", prior_text="2 m/s", depth_info="", category="S2",
                  spec=QuestionSpec(qid=2, target=Quantity("distance", ["c", "d"], time=1.0, unit="m"), prior=prior),
                  roles=[["prior", "A"], ["target", "C"], ["target2", "D"]], direct=4.0, confidence=0.5, ann_flags=[])
    tracks = {"A": cvf.Track("A", "ball", pts, uses=[{"qid": 1, "role": "prior", "use": "motion"},
                                                     {"qid": 2, "role": "prior", "use": "motion"}]),
              "B": cvf.Track("B", "bar", ext, uses=[{"qid": 1, "role": "target", "use": "size"}]),
              "C": cvf.Track("C", "c", c, uses=[{"qid": 2, "role": "target", "use": "distance"}]),
              "D": cvf.Track("D", "d", d, uses=[{"qid": 2, "role": "target2", "use": "distance"}])}
    return cvf.VideoContext("v", "", FPS, (W, H), 30, "V2SC", "simulation", tracks, [q1, q2])


def _meta_for(ctx):
    plan = cvf.plan_evidence(ctx)
    blank = np.zeros((H, W, 3), np.uint8)
    _, meta = cvf.build_request(ctx, frames={f: blank for f in plan["frames"]})
    return plan, meta


def _readings(ctx, plan, action, fn=lambda tid, o: o):
    """A response whose readings are fn(pass-1 obs) on every evidence frame of every track."""
    tracks = []
    for tid, t in ctx.tracks.items():
        fr, obs, seen = set(plan["per_track"].get(tid, [])), [], set()
        for o in t.obs:
            f = cvf.frame_of(o.t, ctx.fps)
            if f in fr and f not in seen:
                seen.add(f)
                n = fn(tid, o)
                obs.append({"frame": f, "point": n.point, "extent": n.extent, "box": n.box})
        tracks.append({"track": tid, "action": action, "problem": "", "depth_name": None, "obs": obs})
    return tracks


def test_identical_readings_leave_every_answer_unchanged_under_every_rule():
    ctx = _size_dist_ctx()
    plan, meta = _meta_for(ctx)
    assert len(plan["per_track"]["B"]) == 2 and len(ctx.tracks["B"].obs) == 5    # evidence is a subset
    p1 = cvf.pass1_answers(ctx)
    nofix = {"change": []}
    for action, verdict in (("keep", "accept_geometry"), ("replace", "corrected")):
        tr = _readings(ctx, plan, action)
        resp = {"tracks": tr, "questions": [{"qid": q.qid, "verdict": verdict, "problem": "",
                                             "spec_fix": {"target": nofix, "prior": nofix},
                                             "final_answer": p1[q.qid]["chosen"][0], "confidence": 0.5}
                                            for q in ctx.questions]}
        for rule in cvf.RULES:
            for r in cvf.recompute(meta, resp, rule=rule):
                assert r["parsed_value"] == pytest.approx(r["pass1_value"], rel=1e-12), (action, rule, r["id"])
                assert rule == "verify_final" or r["verify_how"] == "pass1", (action, rule, r)
        tracks, info = cvf.apply_track_fixes(cvf.context_from_meta(meta), resp, set(meta["frames_shown"]),
                                             remeasure=True, evidence=meta["evidence"])
        assert not any(i["applied"] for i in info.values()) and all(i["delta_px"] in (0.0, None) for i in info.values())
        assert ("verify_replace_noop" in info["A"]["flags"]) == (action == "replace")   # dense motion track kept
    # a motion track replaced by readings that do move is replaced by them (wrong object / drift)
    tr = _readings(ctx, plan, "replace", lambda tid, o: Obs(t=o.t, point=[o.point[0], o.point[1] + 5]) if tid == "A" else o)
    tracks, info = cvf.apply_track_fixes(cvf.context_from_meta(meta), {"tracks": tr[:1]}, set(meta["frames_shown"]))
    assert info["A"]["applied"] and len(tracks["A"].obs) == len(plan["per_track"]["A"]) < len(ctx.tracks["A"].obs)


def test_readings_carry_their_systematic_change_to_every_frame():
    ctx = _size_dist_ctx()
    plan, meta = _meta_for(ctx)
    p1 = {q: a["geo"].value for q, a in cvf.pass1_answers(ctx).items()}

    def change(tid, o):
        n = Obs(**{**o.__dict__})
        if tid == "B":                    # every extent 10% longer, about its midpoint
            (x1, y1), (x2, y2) = o.extent
            n.extent = [[x1 - 0.05 * (x2 - x1), y1], [x2 + 0.05 * (x2 - x1), y2]]
        if tid == "C":                    # the point 6 px further left (box with it)
            n.point = [o.point[0] - 6, o.point[1]]
            n.box = [o.box[0] - 6, o.box[1], o.box[2] - 6, o.box[3]]
        return n

    resp = {"tracks": _readings(ctx, plan, "keep", change), "questions": []}
    rows = {r["id"]: r for r in cvf.recompute(meta, resp, rule="remeasure")}
    assert rows[1]["geo2_value"] == pytest.approx(1.1 * p1[1], rel=1e-9)          # all 5 frames, not 2
    assert rows[2]["geo2_value"] == pytest.approx(p1[2] * math.hypot(116, 10) / math.hypot(110, 10), rel=1e-6)
    tracks, info = cvf.apply_track_fixes(cvf.context_from_meta(meta), resp, set(meta["frames_shown"]), remeasure=True)
    assert len(tracks["B"].obs) == 5 and len(tracks["C"].obs) == 6 and not info["A"]["applied"]
    assert [round(cvf._len(o), 6) for o in tracks["B"].obs] == [round(1.1 * L, 6) for L in (18, 20, 21, 25, 30)]
    assert [o.point[0] for o in tracks["C"].obs] == pytest.approx([50.0 + f - 6 for f in range(4, 16, 2)])
    assert [o.box[0] for o in tracks["C"].obs] == pytest.approx([44.0 + f - 6 for f in range(4, 16, 2)])


def test_merge_readings_keeps_pass1_times_and_adds_unknown_frames():
    p1 = [Obs(t=0.101, extent=[[0, 0], [10, 0]], box=[0, -2, 10, 2]), Obs(t=0.5, extent=[[0, 0], [20, 0]])]
    got = cvf.merge_readings(p1, [Obs(t=0.1, extent=[[0, 0], [12, 0]]), Obs(t=0.9, extent=[[1, 1], [2, 1]])], FPS)
    assert [o.t for o in got] == [0.101, 0.5, 0.9]                                  # frame 1 keeps t=0.101
    assert got[0].extent == [[0, 0], [12, 0]] and got[0].box == [0, -2, 10, 2]    # no box reading: box as is
    assert cvf._len(got[1]) == pytest.approx(24.0)                                  # 1.2 x the unread frame
    assert cvf.merge_readings(p1, [Obs(t=2.0, extent=[[0, 0], [5, 0]])], FPS) is None  # no shared frame


def test_reading_delta_prefers_the_obs_carrying_the_field_on_repeated_frames():
    # a flow-refined track: one point obs per frame, then box-only obs appended at the annotated frames
    t = cvf.Track("A", "x", [Obs(t=0.0, point=[10, 10]), Obs(t=0.1, point=[12, 10]),
                             Obs(t=0.0, box=[0, 0, 40, 40]), Obs(t=0.1, box=[2, 0, 42, 40])])
    assert cvf.reading_delta(t, [Obs(t=0.0, point=[11, 10]), Obs(t=0.1, point=[12, 10])], FPS) == pytest.approx(1.0)
    assert cvf.reading_delta(t, [Obs(t=0.1, box=[2, 0, 45, 40])], FPS) == pytest.approx(3.0)


def test_crop_label_formula_maps_drawn_markers_to_the_listed_coordinates(ws):
    ctx = _ctx_ws(ws)
    params, meta = cvf.build_request(ctx)
    content = params["messages"][0]["content"]
    assert f"x = x0 + (u - {cvf.MARGIN_L}) / zoom, y = y0 + (v - {cvf.MARGIN_T}) / zoom" in params["system"][0]["text"]
    assert f"(u - {cvf.MARGIN_L})" in cvf.SYSTEM_VF1 and "crop_x / zoom" not in cvf.SYSTEM + cvf.SYSTEM_VF1
    magenta = cvf.PALETTE[1][1]
    checked = 0
    for k, b in enumerate(content):
        if b["type"] != "text" or not b["text"].startswith("[Image"):
            continue
        img = cv2.imdecode(np.frombuffer(__import__("base64").b64decode(content[k + 1]["source"]["data"]), np.uint8), 1)
        m = re.search(r"original x = (?:([\d.]+) \+ )?\(u - (\d+)\) / ([\d.]+), y = (?:([\d.]+) \+ )?\(v - (\d+)\) / "
                      r"([\d.]+)", b["text"])
        assert m, b["text"]
        x0, ml, zx, y0, mt, zy = (float(g or 0) for g in m.groups())
        if " crop " not in b["text"]:
            assert (x0, y0, ml, mt) == (0, 0, cvf.MARGIN_L, cvf.MARGIN_T)
            continue
        for x, y in [tuple(map(float, p)) for w in b["text"].split("Shows: ")[1].split("; ") if w.startswith("B end")
                     for p in re.findall(r"\(([-\d.]+), ([-\d.]+)\)", w)]:
            u0, v0 = ml + (x - x0) * zx - 0.5, mt + (y - y0) * zy - 0.5            # expected ring centre (index)
            u, v = _centroid(img, magenta, near=(u0, v0), radius=6.5)
            assert (x0 + (u + 0.5 - ml) / zx, y0 + (v + 0.5 - mt) / zy) == pytest.approx((x, y), abs=0.25)
            checked += 1
    assert checked >= 2


def test_readings_in_evidence_image_pixels_are_not_applied():
    ctx = _size_dist_ctx()
    ctx.image_size = (1920, 1080)          # overview scale 2/3: 1080p
    plan = cvf.plan_evidence(ctx)
    meta = cvf.context_meta(ctx)
    meta["frames_shown"] = sorted(plan["frames"])
    s = 1280 / 1920
    meta["evidence"] = [{"frame": f, "region": [0, 0, 1920, 1080], "zoom": s, "kind": "frame"} for f in plan["frames"]] \
        + [{"frame": c.frame, "region": [c.x0, c.y0, c.x1, c.y1], "zoom": c.zoom, "kind": "crop"} for c in plan["crops"]]
    crop_c = next(c for c in plan["crops"] if any(w.startswith("C ") for w in c.what))

    def to_img(margins, x0, y0, z):
        ml, mt = (cvf.MARGIN_L, cvf.MARGIN_T) if margins else (0, 0)
        f = lambda p: [ml + (p[0] - x0) * z, mt + (p[1] - y0) * z]   # noqa: E731
        return lambda tid, o: Obs(t=o.t, point=f(o.point) if o.point else None,
                                  extent=[f(p) for p in o.extent] if o.extent else None)

    for fn in (to_img(False, 0, 0, s), to_img(True, 0, 0, s), to_img(True, crop_c.x0, crop_c.y0, crop_c.zoom)):
        tr = [t for t in _readings(ctx, plan, "replace", fn) if t["track"] in ("B", "C")]
        _, info = cvf.apply_track_fixes(cvf.context_from_meta(meta), {"tracks": tr}, set(meta["frames_shown"]),
                                        evidence=meta["evidence"])
        assert "verify_pixel_space" in info["C"]["flags"] and not info["C"]["applied"]
    # a real correction of the same size is applied
    real = lambda tid, o: Obs(t=o.t, point=[o.point[0] + 25, o.point[1] + 3] if o.point else None)  # noqa: E731
    tr = [t for t in _readings(ctx, plan, "replace", real) if t["track"] == "C"]
    _, info = cvf.apply_track_fixes(cvf.context_from_meta(meta), {"tracks": tr}, set(meta["frames_shown"]),
                                    evidence=meta["evidence"])
    assert info["C"]["applied"] and not info["C"]["flags"].count("verify_pixel_space")


def test_agreement_gate_catches_a_1080p_overview_factor(ws):
    ctx = _ctx_ws(ws)
    _, meta = cvf.build_request(ctx)
    bad = {r["id"]: r for r in cvf.recompute(meta, _fixed(meta, final=200 / 3 / 1.5))}
    assert bad[101]["verify_how"] == "pass1" and "verify_inconsistent" in bad[101]["flags"]
    ok = {r["id"]: r for r in cvf.recompute(meta, _fixed(meta, final=200 / 3 * 1.2))}
    assert ok[101]["verify_how"] == "recomputed"


def test_crop_draws_only_boxes_the_geometry_reads():
    # track A: motion points with boxes (box not read); its box's left side runs through B's extent end
    a = [Obs(t=0.6, point=[160.0, 120.0], box=[100.0, 90.0, 220.0, 150.0])]
    b = [Obs(t=0.6, extent=[[100.0, 120.0], [60.0, 120.0]])]
    ctx = _ctx(a, b)
    crop = cvf.CropSpec(6, 70, 90, 130, 150, 4, ["B end 1"])
    items = [("A", a[0], "motion"), ("B", b[0], "size")]
    img = cvf.render_crop(np.zeros((H, W, 3), np.uint8), crop, items, ctx)
    cyan = lambda p: (p[..., 0] > 50) & (p[..., 1] > 50) & (p[..., 2] < 30)      # noqa: E731 (BGR, anti-aliased)
    near = lambda u0, v0, r=3: cyan(img[v0 - r:v0 + r + 1, u0 - r:u0 + r + 1].astype(int)).any()  # noqa: E731
    side_u = cvf.MARGIN_L + (100 - 70) * 4
    assert not near(side_u, cvf.MARGIN_T + (140 - 90) * 4)        # no box side through B's endpoint
    assert not near(side_u, cvf.MARGIN_T + (120 - 90) * 4 + 30)
    # a size read from a box (no extent): corner brackets only
    a2 = [Obs(t=0.6, box=[100.0, 100.0, 120.0, 140.0])]
    ctx2 = _ctx(a2, b, use_b="size")
    img = cvf.render_crop(np.zeros((H, W, 3), np.uint8), crop, [("B", a2[0], "size")], ctx2)
    magenta = lambda p: (p[..., 0] > 50) & (p[..., 2] > 50) & (p[..., 1] < 30)   # noqa: E731
    hit = lambda x, y: magenta(img[int(cvf.MARGIN_T + (y - 90) * 4) - 2:int(cvf.MARGIN_T + (y - 90) * 4) + 3,  # noqa: E731
                                   int(cvf.MARGIN_L + (x - 70) * 4) - 2:int(cvf.MARGIN_L + (x - 70) * 4) + 3]
                           .astype(int)).any()
    assert hit(100, 101) and hit(101, 100) and not hit(100, 120)   # bracket at the corner, side open


def test_size_evidence_shows_every_asked_time():
    ext = [Obs(t=f / FPS, extent=[[100.0, 60.0], [120.0, 60.0]]) for f in range(0, 30, 2)]
    tr = cvf.Track("B", "bar", ext, uses=[{"qid": 1, "role": "target", "use": "size"},
                                          {"qid": 2, "role": "target", "use": "size"}])
    qs = {q: cvf.QCtx(qid=q, question="", prior_text="", depth_info="", category="S2",
                      spec=QuestionSpec(qid=q, target=Quantity("size", ["bar"], time=t), prior=Quantity("size", ["x"])),
                      roles=[["target", "B"]], direct=None, confidence=None, ann_flags=[])
          for q, t in ((1, 0.4), (2, 2.4))}
    frames = [round(o.t * FPS) for o, _ in cvf.evidence_obs(tr, qs)]
    assert frames[:2] == [4, 24] and len(frames) == 3


def _argv_as(ws, name, frm):
    a = _argv(ws)
    a[a.index("--name") + 1], a[a.index("--from") + 1] = name, frm
    return a


def _ledger_entry(**e):
    budget._append({"ts": "2026-01-01T00:00:00+00:00", **e})


def test_run_name_guards(ws):
    with pytest.raises(SystemExit, match="pass-1 run"):
        rcv.main(_argv_as(ws, "p1", "p1"), client=FakeClient())
    assert not (ws.runs / "p1" / "qs.csv").exists()
    # a folder holding pass-1 records
    rcv.rc.save_record(ws.runs / "ver" / "qs" / "records",
                       rcv.rc.load_records(ws.runs / "p1" / "qs" / "records")["vid_a"])
    with pytest.raises(SystemExit, match="not verify records"):
        rcv.main(_argv(ws), client=FakeClient())
    for p in (ws.runs / "ver" / "qs" / "records").glob("*.json"):
        p.unlink()
    # a pass-1 run of the same name in the ledger (hold with a pass-1 config, untagged usage)
    _ledger_entry(type="hold", run="ver", id="msgbatch_x", usd=1.0, split="qs", custom_ids={"vid_a": "vid_a"},
                  config={"prompt_version": "v1"})
    with pytest.raises(SystemExit, match="did not write"):
        rcv.main(_argv(ws), client=FakeClient())


def test_run_name_guard_accepts_own_entries(ws):
    client = FakeClient()
    rcv.main(_argv(ws), client=client)
    led = budget.entries()
    assert led[-1]["kind"] == "verify"
    # an untagged sync usage entry from before the tag, for a video with a verify record, is ours
    _ledger_entry(type="usage", run="ver", id="req_old", usd=0.1, split="qs", video_id="vid_a", mode="sync")
    rcv.main(_argv(ws), client=FakeClient())
    # --from a verify run
    with pytest.raises(SystemExit, match="holds verify records"):
        rcv.main(_argv_as(ws, "ver2", "ver"), client=FakeClient())
