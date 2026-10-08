"""Cross-module end-to-end checks on synthetic scenes (CPU only: no network, no paid API, no GPU).

Track A: scripts/run_claude.py with a fake Anthropic client whose "model" reads the request it is
sent (frame labels, image size, qids) and annotates the scenes' true geometry -> claude_annotate
-> qp.geometry.solve -> the run CSV -> scripts/score.py and scripts/make_submission.py.
Track B: the Colab notebook's own stage commands (specs -> CV tracks -> Qwen grounding -> direct
answers -> geometry for both track sources), run with fake Qwen3-VL / detector / SAM 2 models that
find the rendered discs by colour, then the notebook's METHODS files -> score -> submission.
"""

import ast
import importlib.util
import json
import math
import re
import shlex
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from qp import claude_annotate as ca
from qp.geometry import solve
from qp.open import cv_track as cv
from qp.open import qwen_vl as Q
from qp.spec import Answer
from synth import Body, Camera, ballistic, render_video, static, track

ROOT = Path(__file__).resolve().parents[1]
CAM = Camera()          # 854 x 480, 60 deg horizontal FOV


def _script(name: str):
    spec = importlib.util.spec_from_file_location(f"_it_{name}", ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_questions(path: Path, rows: list[dict]) -> Path:
    """Validation-format CSV: first unnamed column = qid."""
    df = pd.DataFrame(rows)
    df.insert(0, "", df.pop("qid"))
    df.to_csv(path, index=False)
    return path


def _render(path: Path, bodies: list[Body], fps: float, duration: float) -> None:
    """Video whose frame i shows time i / fps (the dataset fps) while its container claims fps + 6, so a
    stage that timed frames by the container fps would get every speed and time wrong."""
    k = (fps + 6) / fps
    shown = [Body(b.name, (lambda t, b=b: b.pos(t * k)), b.size, b.angle, b.color) for b in bodies]
    render_video(str(path), shown, CAM, duration / k, fps + 6)


def _score_table(score_mod, gt: pd.DataFrame, paths: list[str], monkeypatch, capsys) -> pd.DataFrame:
    """scripts/score.py on `paths` against `gt` (qp.data columns incl. answer) -> its printed table."""
    monkeypatch.setattr(score_mod, "load_validation", lambda: gt)
    capsys.readouterr()
    score_mod.main(paths)
    lines = capsys.readouterr().out.strip().splitlines()
    head = lines[0].split()
    return pd.DataFrame([dict(zip(head, ln.split())) for ln in lines[1:]]).set_index("file")


def _submit(sub_mod, pred_csv: Path, ids: list[int], out: Path, monkeypatch) -> pd.DataFrame:
    """scripts/make_submission.py with a stand-in template (the real one is downloaded on Colab)."""
    tmpl = pd.DataFrame({"id": ids, "video_id": "v", "question": "q", "parsed_value": np.nan})
    monkeypatch.setattr(sub_mod, "load_template", lambda: tmpl)
    monkeypatch.setattr(sys, "argv", ["make_submission.py", str(pred_csv), str(out)])
    sub_mod.main()
    return pd.read_csv(out)


# =========================================================================== Track A (Claude)

def _q(kind, objects, dimension="", time=None, window=None, axis="any", value_si=None, unit=""):
    return {"kind": kind, "objects": objects, "dimension": dimension, "time": time, "window": window,
            "axis": axis, "value_si": value_si, "unit": unit}


BIRD = Body("bird", ballistic([-3.0, -1.0, 20.0], [6.0, 0.0, 0.0]), size=1.2)
HOUSE = Body("house", static([-2.0, 2.5, 20.0]), size=8.0)
WHITE = Body("white ball", ballistic([0.3, -0.2, 1.0], [-0.1, 0.05, 0.0]), size=0.0572)
PURPLE = Body("purple ball", static([0.1, 0.05, 1.0]), size=0.0572)
BLACK = Body("black ball", ballistic([-0.4, 0.0, 1.0], [0.15, 0.0, 0.0]), size=0.0572)
BALL = Body("ball", ballistic([-4.0, -2.0, 8.0], [4.0, -3.0, 0.0], [0.0, 9.8, 0.0]), size=0.24)
PERSON = Body("person", ballistic([-1.0, 0.4, 12.0], [0.3, 0.0, -1.3]), size=1.87, angle=math.pi / 2)
PEDESTAL = Body("pedestal", static([1.5, 1.2, 9.4]), size=0.6, angle=math.pi / 2)
CAR = Body("car", ballistic([-3.0, 1.0, 30.0], [3.0, 0.0, 0.0]), size=4.2)
BILLIARD_END = (round(2.4 * 30) - 1) / 30    # time of the last frame of synth_billiards

# Each question: (qid, inference_type, question, answer, target spec, prior spec, tracks); a track is
# (role, body, how): "motion" = point + box on every sent frame, "extent" = extent + box on 5 frames,
# "reuse" = empty obs (claude_annotate reuses an earlier track of that object). time "last" = last frame.
SCENES = {
    "synth_bird": dict(type="V2MC", fps=24.0, duration=2.0, bodies=[BIRD, HOUSE], depth=[],
                       prior="speed of the bird =6m/s", questions=[
        (0, "DS", "What is the width between the two widest eaves of the house in meters?", 8.0,
         _q("size", ["house"], "width", unit="m"), _q("speed", ["bird"], value_si=6.0),
         [("prior", BIRD, "motion"), ("target", HOUSE, "extent")]),
        (1, "DS", "What is the length of the bird in cm?", 120.0,
         _q("size", ["bird"], "length", unit="cm"), _q("speed", ["bird"], value_si=6.0),
         [("prior", BIRD, "reuse"), ("target", BIRD, "extent")]),
        (2, "DD", "What is the bird's average velocity in 0.50s to 1.50s in cm/s?", 600.0,
         _q("speed", ["bird"], window=[0.5, 1.5], unit="cm/s"), _q("speed", ["bird"], value_si=6.0),
         [("prior", BIRD, "reuse"), ("target", BIRD, "reuse")]),
    ]),
    "synth_billiards": dict(type="S2MC", fps=30.0, duration=2.4, bodies=[WHITE, PURPLE, BLACK], depth=[],
                            prior="billiard ball diameter = 57.2mm", questions=[
        (40, "SS", "What is the final distance between the purple ball and the black ball in cm?",
         100 * float(np.linalg.norm(PURPLE.pos(0)[:2] - BLACK.pos(BILLIARD_END)[:2])),
         _q("distance", ["purple ball", "black ball"], time="last", unit="cm"),
         _q("size", ["billiard ball"], "diameter", value_si=0.0572),
         [("prior", WHITE, "extent"), ("target", PURPLE, "motion"), ("target2", BLACK, "motion")]),
        (41, "SD", "What is the white ball's average velocity in 1.00s to 2.00s in cm/s?",
         100 * math.hypot(0.1, 0.05),
         _q("speed", ["white ball"], window=[1.0, 2.0], unit="cm/s"),
         _q("size", ["billiard ball"], "diameter", value_si=0.0572),
         [("prior", WHITE, "reuse"), ("target", WHITE, "motion")]),
    ]),
    "synth_drop": dict(type="A2SC", fps=30.0, duration=1.2, bodies=[BALL], depth=[],
                       prior="gravity acc = 9.8m/s^2", questions=[
        (20, "DD", "What is the (average) horizontal velocity of the ball in m/s?", 4.0,
         _q("speed", ["ball"], axis="horizontal", unit="m/s"),
         _q("acceleration", ["ball"], axis="vertical", value_si=9.8),
         [("prior", BALL, "motion"), ("target", BALL, "reuse")]),
        (21, "DS", "What is the diameter of the ball in cm?", 24.0,
         _q("size", ["ball"], "diameter", unit="cm"),
         _q("acceleration", ["ball"], value_si=9.8),          # model forgot axis "vertical"
         [("prior", BALL, "reuse"), ("target", BALL, "extent")]),
    ]),
    "synth_plaza": dict(type="S3MC", fps=30.0, duration=2.0, bodies=[PERSON, PEDESTAL],
                        depth=[("human", PERSON, 0.0), ("human", PERSON, 1.0), ("human", PERSON, 2.0),
                               ("the pedestal of the central _sculpture", PEDESTAL, None)],
                        prior="height of the person = 1.87m", questions=[
        (10, "SS", "What is the height of the pedestal (square base) of the central sculpture in meters?", 0.6,
         _q("size", ["pedestal of the central sculpture"], "height", unit="m"),
         _q("size", ["person"], "height", value_si=1.87),
         [("prior", PERSON, "extent"), ("target", PEDESTAL, "extent")]),
        (11, "SD", "What is the speed of the person at time 1s in m/s?", math.hypot(0.3, 1.3),
         _q("speed", ["person"], time=1.0, unit="m/s"), _q("size", ["person"], "height", value_si=1.87),
         [("prior", PERSON, "reuse"), ("target", PERSON, "motion")]),
    ]),
    "synth_road": dict(type="V3SC", fps=25.0, duration=2.0, bodies=[CAR],
                       depth=[("car", CAR, 0.0), ("car", CAR, 1.0), ("car", CAR, 2.0)],
                       prior="t=1s, speed of the car = 3.0m/s", questions=[
        (30, "DS", "What is the length of the car in meters?", 4.2,
         _q("size", ["car"], "length", unit="m"), _q("speed", ["car"], time=1.0, value_si=3.0),
         [("prior", CAR, "motion"), ("target", CAR, "extent")]),
        (31, "DD", "What is the displacement of the car from 0.5s to 1.5s in meters?", 3.0,
         _q("displacement", ["car"], window=[0.5, 1.5], unit="m"), _q("speed", ["car"], time=1.0, value_si=3.0),
         [("prior", CAR, "reuse"), ("target", CAR, "reuse")]),
    ]),
}


def _depth_text(sc: dict) -> str:
    return "\n".join((f"t={t:g}s, " if t is not None else "") + f"distance_{label.replace(' ', '_')}_camera = "
                     f"{body.range(t or 0.0):.3f}m" for label, body, t in sc["depth"])


def _claude_obs(body: Body, frames: list[int], fps: float, scale: float, how: str, seed: int) -> list[dict]:
    """What a careful annotator gives: coordinates of the SENT image (original x scale), 0.25 px noise."""
    if how == "reuse":
        return []
    if how == "extent":
        frames = [frames[i] for i in np.linspace(0, len(frames) - 1, 5).round().astype(int)]
    tr = track(body, "x", [f / fps for f in frames], CAM, noise_px=0.25, seed=seed,
               point=how == "motion", extent=how == "extent", box=True)
    s = lambda v: None if v is None else np.round(np.asarray(v) * scale, 2).tolist()  # noqa: E731
    return [{"frame": f, "point": s(o.point), "extent": s(o.extent), "box": s(o.box)} for f, o in zip(frames, tr.obs)]


def _claude_reply(params: dict) -> dict:
    """The fake model's structured output for one request, from what the request shows it."""
    content = params["messages"][0]["content"]
    head = content[0]["text"]
    vid = re.match(r"Video (\S+?):", head).group(1)
    scale = int(re.search(r"(\d+)x\d+ px", head).group(1)) / CAM.width
    frames = [int(m.group(1)) for b in content if b["type"] == "text"
              for m in [re.match(r"Frame (\d+) \(t=", b["text"])] if m]
    asked = {int(q) for q in re.findall(r"qid=(\d+)", content[-1]["text"])}
    sc = SCENES[vid]
    depth = [{"object": " ".join(label.replace("_", " ").split()), "distance_m": round(body.range(t or 0.0), 3),
              "time": t} for label, body, t in sc["depth"]]
    out = []
    for qid, _, _, answer, target, prior, tracks in sc["questions"]:
        if qid not in asked:
            continue
        target = dict(target, time=frames[-1] / sc["fps"] if target["time"] == "last" else target["time"])
        out.append({"qid": qid, "spec": {"target": target, "prior": prior, "depth": depth, "notes": ""},
                    "tracks": [{"role": role, "object": body.name,
                                "obs": _claude_obs(body, frames, sc["fps"], scale, how, seed=qid * 10 + k)}
                               for k, (role, body, how) in enumerate(tracks)],
                    "direct_answer": round(answer * 1.1, 4), "confidence": 0.6})
    return {"questions": out}


class _Stream:
    def __init__(self, msg):
        self.msg, self.request_id = msg, "req_fake"

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get_final_message(self):
        return self.msg


class FakeAnthropic:
    """messages.stream(**params) -> a Message carrying _claude_reply(params) as its text."""

    def __init__(self):
        self.requests = []
        self.messages = SimpleNamespace(stream=self._stream, count_tokens=None, batches=None)

    def _stream(self, **params):
        self.requests.append(params)
        return _Stream(SimpleNamespace(
            id=f"msg_{len(self.requests)}", stop_reason="end_turn", stop_details=None,
            content=[SimpleNamespace(type="text", text=json.dumps(_claude_reply(params)))],
            usage=SimpleNamespace(input_tokens=20000, output_tokens=6000, cache_creation_input_tokens=0,
                                  cache_read_input_tokens=0, cache_creation=None)))


@pytest.fixture
def claude_ws(tmp_path, monkeypatch):
    videos = tmp_path / "videos"
    videos.mkdir()
    rows = []
    for vid, sc in SCENES.items():
        _render(videos / f"{vid}.mp4", sc["bodies"], sc["fps"], sc["duration"])
        for qid, inf, question, answer, *_ in sc["questions"]:
            rows.append({"qid": qid, "video_id": vid, "video_source": "simulation", "video_type": sc["type"],
                         "fps": sc["fps"], "inference_type": inf, "question": question,
                         "ground_truth_prior": sc["prior"], "depth_info": _depth_text(sc) or np.nan,
                         "ground_truth_posterior": answer})
    csv = _write_questions(tmp_path / "questions.csv", rows)
    monkeypatch.setenv("QP_LEDGER", str(tmp_path / "ledger.jsonl"))
    monkeypatch.setenv("QP_BUDGET_USD", "50")
    # frames reach the model downscaled (as videos over 2576 px do), so coordinates must be mapped back
    read = ca.read_frames
    monkeypatch.setattr(ca, "read_frames", lambda path, idx, fps, quality=90, max_side=0: read(
        path, idx, fps, quality, max_side=640))
    return SimpleNamespace(root=tmp_path, videos=videos, csv=csv)


def test_track_a_end_to_end(claude_ws, monkeypatch, capsys):
    rc = _script("run_claude")
    monkeypatch.setattr(rc, "ROOT", claude_ws.root)             # no .env from the repo
    client = FakeAnthropic()
    runs = claude_ws.root / "runs"
    argv = ["--csv", str(claude_ws.csv), "--video-dir", str(claude_ws.videos), "--name", "e2e",
            "--out-root", str(runs), "--local-estimate", "--workers", "1"]
    res = rc.main(argv, client=client)
    assert len(client.requests) == len(SCENES)
    sent = client.requests[0]["messages"][0]["content"]
    assert re.search(r"640x360 px", sent[0]["text"])            # downscaled frames really were sent

    res = res.set_index("id")
    want = {qid: (ans, sc["type"][1]) for sc in SCENES.values() for qid, _, _, ans, *_ in sc["questions"]}
    for qid, (ans, dim) in want.items():
        r = res.loc[qid]
        assert r.geo_value == pytest.approx(ans, rel=0.03), (qid, r.to_dict())
        assert r.direct_value == pytest.approx(ans * 1.1, rel=1e-3)
        if dim == "2":
            assert r.parsed_value == r.geo_value and r.method == "geometry:2d_scale", (qid, r["flags"])
        else:  # default rule: 3D of a video without a known camera (simulation) -> Claude's direct answer
            assert r.parsed_value == r.direct_value and "geo_3d_no_camera" in r["flags"], (qid, r["flags"])
            assert r.geo_method == "3d_focal_from_prior"
    # the geometry-first rule answers everything from the tracks (same records: nothing is sent)
    n_req = len(client.requests)
    geo_res = rc.main([*argv, "--rule", "geo"], client=client).set_index("id")
    assert len(client.requests) == n_req
    for qid, (ans, dim) in want.items():
        r = geo_res.loc[qid]
        assert r.parsed_value == pytest.approx(ans, rel=0.03), (qid, r.to_dict())
        assert r.method == ("geometry:2d_scale" if dim == "2" else "geometry:3d_focal_from_prior"), (qid, r["flags"])
    res = rc.main(argv, client=client).set_index("id")  # back to the default rule's CSV
    assert all("reused_track" in res["flags"][q] for q in (1, 2, 31))
    assert "prior_axis_gravity" in res["flags"][21]               # gravity prior made vertical for the solver

    out_csv = runs / "e2e" / "questions.csv"
    assert out_csv.exists() and list(pd.read_csv(out_csv).columns[:2]) == ["id", "parsed_value"]

    # the run's records give the same specs to Track B tools (cv_track.load_specs) as to Track A
    rec_dir = runs / "e2e" / "questions" / "records"
    specs = cv.load_specs(rec_dir)
    assert set(specs) == set(want)
    assert specs[21].prior.axis == "vertical" and specs[10].is_3d and specs[30].prior.value_si == 3.0
    anns = ca.load_annotations(rc.load_records(rec_dir))
    assert all(specs[q] == anns[q].spec for q in want)

    # CSV contract: scripts/score.py and scripts/make_submission.py accept the run CSV
    gt, _ = rc.load_questions(rc.parse_args(argv))
    table = _score_table(_script("score"), gt, [str(out_csv)], monkeypatch, capsys)
    row = table.loc[str(out_csv)]
    assert int(row.missing) == 0  # 3D answers are the (10% off) direct ones: 0.8 each, 2D exact
    assert float(row.S2) == pytest.approx(1.0) and float(row.D2) == pytest.approx(1.0)
    assert all(0.8 - 1e-9 <= float(row[c]) < 1.0 for c in ("S3", "D3"))
    sub = _submit(_script("make_submission"), out_csv, [*sorted(want), 999], claude_ws.root / "sub.csv", monkeypatch)
    vals = sub.set_index("id").parsed_value
    assert vals[999] == 1.0 and all(vals[q] == pytest.approx(res.parsed_value[q]) for q in want)


def test_track_a_replaces_geometry_blowups_by_direct(monkeypatch):
    """run_claude keeps the same guard as run_open_vlm: implausible or >10x-off geometry -> direct."""
    rc = _script("run_claude")
    values = {1: 5e4, 2: 30.0, 3: 2.2}        # metres: beyond 10 km, 15x the direct 2.0, fine
    geo = types.ModuleType("qp.geometry")
    geo.solve = lambda spec, tracks, size, fps: Answer(spec.qid, values[spec.qid], "geometry", "2d_scale",
                                                       debug={"value_si": values[spec.qid]})
    monkeypatch.setitem(sys.modules, "qp.geometry", geo)
    meta = {"video_id": "v", "fps": 24.0, "video_type": "V2SC", "scale": 1.0, "image_size": [854, 480], "frames": [0],
            "questions": [{"qid": q, "target_unit": "m", "prior": "speed of the car = 3m/s"} for q in values]}
    parsed = {"questions": [{"qid": q, "spec": {"target": _q("size", ["car"], "length", unit="m"),
                                                "prior": _q("speed", ["car"], value_si=3.0), "depth": [], "notes": ""},
                             "tracks": [], "direct_answer": 2.0, "confidence": 0.5} for q in values]}
    df = pd.DataFrame({"qid": list(values), "video_id": "v"})
    res = rc.build_results(df, {"v": {"status": "ok", "parsed": parsed, "meta": meta}}).set_index("id")
    assert res.parsed_value.tolist() == [2.0, 2.0, 2.2] and res.geo_value.tolist() == [5e4, 30.0, 2.2]
    assert "geo_rejected_implausible" in res["flags"][1] and "geo_rejected_disagree" in res["flags"][2]
    assert res.method[3] == "geometry:2d_scale"


def test_claude_response_to_geometry_with_scaled_frames():
    """to_annotations on its own: sent-image pixels (scale 0.5) -> original pixels, t = idx / dataset fps."""
    sc, fps, frames = SCENES["synth_plaza"], 30.0, list(range(0, 60, 3))
    meta = {"video_id": "synth_plaza", "fps": fps, "video_type": sc["type"], "n_frames_total": 60, "scale": 0.5,
            "image_size": list(CAM.size), "frames": frames,
            "questions": [{"qid": q[0], "target_unit": "m" if q[0] == 10 else "m/s", "prior": sc["prior"]}
                          for q in sc["questions"]]}
    params = {"messages": [{"content": [
        {"type": "text", "text": "Video synth_plaza: 3D video; 427x240 px; 30 fps; 60 frames"},
        *[{"type": "text", "text": f"Frame {f} (t={f / fps:.3f}s)"} for f in frames],
        {"type": "text", "text": "qid=10 qid=11"}]}]}
    anns = ca.to_annotations(_claude_reply(params), meta)
    prior = next(t for t in anns[10].tracks if t.role == "prior")
    assert [o.t for o in prior.obs] == pytest.approx([f / fps for f in np.array(frames)[[0, 5, 10, 14, 19]]])
    truth = track(PERSON, "prior", [o.t for o in prior.obs], CAM).obs
    assert np.allclose([o.extent for o in prior.obs], [o.extent for o in truth], atol=1.5)
    for qid, ans in ((10, 0.6), (11, math.hypot(0.3, 1.3))):
        a = solve(anns[qid].spec, anns[qid].tracks, tuple(meta["image_size"]), meta["fps"])
        assert a.value == pytest.approx(ans, rel=0.03) and a.method == "3d_focal_from_prior", a.flags
        assert a.debug["fov_deg"] == pytest.approx(CAM.fov_deg, rel=0.03)


# =========================================================================== Track B (notebook)

Z, R_PX, NB_FPS = 10.0, 20, 24.0
SIZE = (2 * R_PX + 2) * Z / CAM.f          # cv2.circle(LINE_AA) of radius R covers ~2R + 2 px (see test_cv_track)
RED = Body("red ball", ballistic([-3.0, 0.5, Z], [1.2, 0.0, 0.0]), size=2 * R_PX * Z / CAM.f, color=(0, 0, 255))
BLUE = Body("blue ball", static([2.0, -1.0, Z]), size=2 * R_PX * Z / CAM.f, color=(255, 0, 0))
RGB = {"red": (255, 0, 0), "blue": (0, 0, 255)}
NB_QUESTIONS = [  # qid, inference type, question, answer, model spec (target, prior)
    (1, "SD", "What is the speed of the red ball at 1s in m/s?", 1.2,
     _q("speed", ["red ball"], time=1.0, unit="m/s")),
    (2, "SS", "What is the distance between the red ball and the blue ball at 0.5s in meters?",
     float(np.linalg.norm(RED.pos(0.5)[:2] - BLUE.pos(0)[:2])),
     _q("distance", ["red ball", "blue ball"], time=0.5, unit="m")),
    (3, "SS", "What is the diameter of the red ball in cm?", SIZE * 100,
     _q("size", ["red ball"], "diameter", unit="cm")),
]
NB_PRIOR = f"diameter of the blue ball = {SIZE:.4f}m"


def _mask(img: np.ndarray, colour: str) -> np.ndarray:
    return np.abs(img.astype(int) - np.array(RGB[colour])).sum(axis=2) < 200


def _colour(name: str) -> str:
    return next(c for c in RGB if c in name)


def _rel(v: float, n: int) -> int:
    return int(round(v / n * 1000))


def _qwen_reply(req) -> str:
    """Fake Qwen3-VL: specs from the question, boxes / end points of the coloured disc (0-1000 grid)."""
    text = req.messages[-1]["content"]
    text = (text if isinstance(text, str) else " ".join(c.get("text", "") for c in text)).strip()
    if req.json_schema is not None or req.messages[0]["content"] == Q.SPEC_SYSTEM:
        question = re.search(r"Question: (.*)", text).group(1).strip()
        target = next(q[4] for q in NB_QUESTIONS if q[2] == question)
        return json.dumps({"target": target, "notes": "",
                           "prior": _q("size", ["blue ball"], "diameter", value_si=round(SIZE, 4))})
    if req.video is not None:                                         # direct answers: 20% high, no unit
        return f"{next(q[3] for q in NB_QUESTIONS if q[2] in text) * 1.2:.4g}"
    img = np.asarray(req.images[0])
    H, W = img.shape[:2]
    f = cv.mask_features(_mask(img, _colour(text)))
    if f is None:
        return "[]"
    x1, y1, x2, y2 = f["box"]
    if text.startswith("Point to the two ends"):
        y = (y1 + y2) / 2
        return json.dumps([{"point_2d": [_rel(x1, W), _rel(y, H)], "label": "end 1"},
                           {"point_2d": [_rel(x2, W), _rel(y, H)], "label": "end 2"}])
    return "```json\n" + json.dumps([{"bbox_2d": [_rel(x1, W), _rel(y1, H), _rel(x2, W), _rel(y2, H)],
                                       "label": "ball"}]) + "\n```"


class _Backend:
    def generate(self, reqs):
        return [_qwen_reply(r) for r in reqs]


class _Detector:
    name = "fake"

    def detect(self, images, query):
        out = []
        for img in images:
            cands = [{"box": [float(v) for v in f["box"]], "score": 0.8, "label": "ball"}
                     for c in RGB if (f := cv.mask_features(_mask(img, c)))]
            out.append(cands)
        return out


class _Segmenter:
    name = "fake-sam"

    def propagate(self, frames, prompts):
        for oid, (k, box) in prompts.items():
            cx, cy = int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2)
            colour = min(RGB, key=lambda c: np.abs(frames[k][cy, cx].astype(int) - RGB[c]).sum())
            for p, img in enumerate(frames):
                yield p, oid, _mask(img, colour), 0.95


def _notebook():
    spec = importlib.util.spec_from_file_location("_it_build_nb", ROOT / "notebooks" / "_build_notebook.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return "\n".join(src for kind, src in mod.CELLS if kind == "code")


def test_track_b_notebook_stages_end_to_end(tmp_path, monkeypatch, capsys):
    videos = tmp_path / "videos"
    videos.mkdir()
    _render(videos / "synth_nb.mp4", [RED, BLUE], NB_FPS, 2.0)
    csv = _write_questions(tmp_path / "nb.csv", [
        {"qid": qid, "video_id": "synth_nb", "video_source": "simulation", "video_type": "S2MC", "fps": NB_FPS,
         "inference_type": inf, "question": question, "ground_truth_prior": NB_PRIOR, "depth_info": np.nan,
         "ground_truth_posterior": ans} for qid, inf, question, ans, _ in NB_QUESTIONS])

    src = _notebook()
    commands = re.findall(r'stage\("(\w+)", (?:split|"test"), (f"python scripts/[^"\n]+")\)', src)
    assert [c[0] for c in commands] == ["specs", "cv", "annotate", "direct", "caw", "geometry", "geometry",
                                        "submission"]
    methods = ast.literal_eval(re.search(r"^METHODS = (\{.*?\})$", src, re.M | re.S).group(1))

    split, run = "val", "nb"
    base = tmp_path / "outputs" / run / split
    q, a, c = (str(base / n) for n in ("qwen", "caw", "cv"))
    ns = dict(split=split, RUN_NAME=run, q=q, a=a, c=c, MODEL="fake-qwen", BACKEND="hf", CAW_BACKEND="hf",
              DETECTOR="gdino", SAM_MODEL="fake-sam", LIM="", EXT=" --extents", CAWM="")
    qwen = Q.QwenVL(backend=_Backend())
    mods = {"run_open_vlm": _script("run_open_vlm"), "run_cv": _script("run_cv")}
    for name, fstring in commands:
        if name == "submission":
            continue
        fb = next((f for f in (f"{a}/caw.csv", f"{q}/direct.csv") if Path(f).exists()), None)  # stage 13 rule
        ns["fb"], ns["DF"] = fb, (f" --direct-from {fb}" if fb else "")
        argv = shlex.split(eval(fstring, {}, ns))                                              # noqa: S307
        script = Path(argv[1]).stem
        i = argv.index("--split")
        argv = argv[2:i] + ["--csv", str(csv), "--video-dir", str(videos)] + argv[i + 2:]
        if script == "run_cv":
            mods[script].main(argv, tracker=cv.CVTracker(_Detector(), _Segmenter(), max_frames=360))
        else:
            mods[script].main(argv, runner=qwen)                     # caw stage: same fake answers

    files = {m: base / p for m, p in methods.items()}
    assert all(p.exists() for p in files.values()), {m: str(p) for m, p in files.items() if not p.exists()}
    truth = {qid: ans for qid, _, _, ans, _ in NB_QUESTIONS}
    for m in ("qwen_geometry", "cv_geometry", "cv_geometry_only"):
        got = pd.read_csv(files[m]).set_index("id").parsed_value
        for qid, ans in truth.items():
            assert got[qid] == pytest.approx(ans, rel=0.03), (m, qid)
    for m in ("qwen_direct", "caw_direct"):
        got = pd.read_csv(files[m]).set_index("id").parsed_value
        assert all(got[qid] == pytest.approx(ans * 1.2, rel=1e-3) for qid, ans in truth.items())
    geo = pd.read_csv(files["qwen_geometry"])
    assert list(geo.columns) == ["id", "parsed_value", "geo_value", "direct_value", "method", "flags"]
    assert geo.method.str.startswith("geometry:2d_scale").all(), geo["flags"].tolist()

    # stage 14 (scores) and 15 (submission) on these files
    rc = _script("run_claude")
    gt, _ = rc.load_questions(rc.parse_args(["--csv", str(csv), "--video-dir", str(videos), "--name", "x"]))
    table = _score_table(_script("score"), gt, [str(p) for p in files.values()], monkeypatch, capsys)
    assert float(table.loc[str(files["qwen_geometry"]), "S2"]) == pytest.approx(1.0)
    assert float(table.loc[str(files["cv_geometry"]), "S2"]) == pytest.approx(1.0)
    sub = _submit(_script("make_submission"), files["cv_geometry"], sorted(truth), tmp_path / "sub.csv", monkeypatch)
    assert sub.parsed_value.tolist() == pytest.approx([truth[k] for k in sorted(truth)], rel=0.03)


def test_track_b_missing_dataset_fps_falls_back_to_container(tmp_path):
    """Qwen grounding and CV tracks time frames like Track A: dataset fps, else the container's."""
    path = tmp_path / "synth_nb.mp4"
    _render(path, [RED, BLUE], NB_FPS, 2.0)                    # container claims NB_FPS + 6
    rows = pd.DataFrame({"qid": [3], "video_id": "synth_nb", "video_path": str(path), "fps": math.nan,
                         "video_type": "S2MC", "question": NB_QUESTIONS[2][2], "prior": NB_PRIOR, "depth_info": "",
                         "target_unit": "cm"})
    spec = Q.rule_spec(next(rows.itertuples()))
    rec = Q.QwenVL(backend=_Backend()).annotate_videos([rows], {3: spec}, n_uniform=6)["synth_nb"]
    assert rec["meta"]["fps"] == pytest.approx(NB_FPS + 6)
    assert rec["tracks"]["3"][0]["obs"][1]["t"] == pytest.approx(rec["meta"]["frames"][1] / (NB_FPS + 6))
    rec, _ = cv.CVTracker(_Detector(), _Segmenter(), max_frames=360).track_video(rows, {3: spec})
    assert rec["meta"]["fps"] == pytest.approx(NB_FPS + 6) and rec["tracks"]["3"]
