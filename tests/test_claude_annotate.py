import base64
import importlib.util
import json
import re
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import cv2
import numpy as np
import pandas as pd
import pytest

from qp import budget
from qp import claude_annotate as ca
from qp.spec import Answer

ROOT = Path(__file__).resolve().parents[1]
FPS = 10


def _load_runner():
    spec = importlib.util.spec_from_file_location("run_claude", ROOT / "scripts" / "run_claude.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rc = _load_runner()


def make_video(path: Path, n: int = 30, w: int = 64, h: int = 48) -> Path:
    vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (w, h))
    for i in range(n):
        img = np.full((h, w, 3), 40, np.uint8)
        cv2.circle(img, (5 + 2 * i % (w - 10), h // 2), 4, (255, 255, 255), -1)
        vw.write(img)
    vw.release()
    return path


QUESTIONS = [
    # video_id, video_type, inference_type, question, prior, depth_info, answer
    ("vid_a", "V2SC", "DS", "What is the diameter of the ball in cm?", "speed of the ball = 2m/s", "", 8.0),
    ("vid_a", "V2SC", "DD", "What is the speed of the ball at 1.2s in m/s?", "speed of the ball = 2m/s", "", 2.0),
    ("vid_b", "S3SC", "SS", "What is the height of the box in meters?", "diameter of the ball = 0.21m",
     "t=0.5s, distance_ball_camera = 2.0m\ndistance_box_camera = 3.0m", 0.5),
]


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    videos = tmp_path / "videos"
    videos.mkdir()
    make_video(videos / "vid_a.mp4")
    make_video(videos / "vid_b.mp4")
    df = pd.DataFrame(QUESTIONS, columns=["video_id", "video_type", "inference_type", "question",
                                          "ground_truth_prior", "depth_info", "ground_truth_posterior"])
    df.insert(0, "", [101, 102, 103])
    df.insert(3, "fps", FPS)
    csv = tmp_path / "qs.csv"
    df.to_csv(csv, index=False)
    monkeypatch.setattr(rc, "ROOT", tmp_path)
    monkeypatch.setenv("QP_LEDGER", str(tmp_path / "ledger.jsonl"))
    monkeypatch.setenv("QP_BUDGET_USD", "50")
    monkeypatch.setitem(sys.modules, "qp.geometry", None)  # solver absent unless a test installs one
    return SimpleNamespace(root=tmp_path, videos=videos, csv=csv)


def _rows(ws, video_id):
    args = rc.parse_args(["--csv", str(ws.csv), "--video-dir", str(ws.videos), "--name", "t"])
    df, _ = rc.load_questions(args)
    return df[df.video_id == video_id].reset_index(drop=True)


# --------------------------------------------------------------------------- frames

def test_mentioned_times():
    texts = ["What is the white ball's average velocity in 1.00s to 2.00s in cm/s?",
             "t=1.5, ball acceleration = 3.0m/s^2", "t = 0.58s, distance_car_camera = 17.8 m",
             "speed of the bird =6m/s", "gravity acc = 9.8m/s^2", "What is the speed at time 1s in m/s?",
             "billiard ball diameter = 57.2mm", None]
    assert ca.mentioned_times(texts) == [0.58, 1.0, 1.5, 2.0]


def test_select_frames_includes_times_and_caps():
    idx = ca.select_frames(61, 24, [1.0, 1.5], n_uniform=16, max_frames=32)
    assert {24, 36, 22, 26, 34, 38} <= set(idx) and {0, 60} <= set(idx)
    assert idx == sorted(set(idx)) and len(idx) <= 32
    capped = ca.select_frames(61, 24, [1.0, 1.5], n_uniform=16, max_frames=8)
    assert len(capped) == 8 and {24, 36, 22, 26, 34, 38} <= set(capped)
    assert ca.select_frames(10, 24, [5.0], 16, 32) == list(range(10))  # short clip, time beyond end clipped
    assert len(ca.select_frames(61, 24, [], 16, 32)) == 16


# --------------------------------------------------------------------------- request

def test_build_request_labels_frames_and_images(workspace):
    rows = _rows(workspace, "vid_a")
    params, meta = ca.build_request(rows, n_uniform=4, max_frames=32, effort="low")
    assert params["model"] == "claude-opus-5-5" and params["max_tokens"] == ca.default_max_tokens(2)
    assert params["output_config"]["effort"] == "low"
    assert params["output_config"]["format"] == {"type": "json_schema", "schema": ca.SCHEMA}
    assert params["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert "thinking" not in params and "temperature" not in params
    content = params["messages"][0]["content"]
    images = [i for i, b in enumerate(content) if b["type"] == "image"]
    assert len(images) == len(meta["frames"])
    for i, idx in zip(images, meta["frames"]):
        assert content[i - 1] == {"type": "text", "text": f"Frame {idx} (t={idx / FPS:.3f}s)"}
        src = content[i]["source"]
        assert src["type"] == "base64" and src["media_type"] == "image/jpeg"
        raw = base64.b64decode(src["data"])
        assert raw[:2] == b"\xff\xd8"
        img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        assert img.shape[:2] == (48, 64)  # native resolution, no resize
    assert {11, 12, 13} <= set(meta["frames"])  # "at 1.2s" and +/- 0.1 s
    assert meta["image_size"] == [64, 48] and meta["scale"] == 1.0 and meta["fps"] == FPS
    last = content[-1]["text"]
    assert "qid=101" in last and "qid=102" in last and "speed of the ball = 2m/s" in last
    assert "Asked unit: cm" in last and "Asked unit: m/s" in last
    assert ca.estimate_input_tokens(params) > len(images) * 4


def test_build_request_3d_depth_times(workspace):
    params, meta = ca.build_request(_rows(workspace, "vid_b"), n_uniform=2, max_frames=32)
    assert {4, 5, 6} <= set(meta["frames"])  # depth line "t=0.5s"
    assert "3D video" in params["messages"][0]["content"][0]["text"]
    assert "distance_box_camera = 3.0m" in params["messages"][0]["content"][-1]["text"]


# --------------------------------------------------------------------------- schema

def _walk(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk(v)


def test_schema_valid_and_strict():
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.Draft202012Validator.check_schema(ca.SCHEMA)
    unsupported = {"minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
                   "minLength", "maxLength", "minItems", "maxItems", "uniqueItems", "pattern"}
    for node in _walk(ca.SCHEMA):
        assert not unsupported & set(node), node
        if node.get("type") == "object":
            assert node["additionalProperties"] is False
            assert set(node["required"]) == set(node["properties"])
    question = ca.SCHEMA["properties"]["questions"]["items"]
    assert set(question["required"]) == {"qid", "spec", "tracks", "direct_answer", "confidence"}
    spec = question["properties"]["spec"]
    assert set(spec["required"]) == {"target", "prior", "depth", "notes"}
    assert set(spec["properties"]["target"]["required"]) == {
        "kind", "objects", "dimension", "time", "window", "axis", "value_si", "unit"}
    track = question["properties"]["tracks"]["items"]
    assert track["properties"]["role"]["enum"] == ["prior", "prior2", "target", "target2"]
    assert set(track["properties"]["obs"]["items"]["required"]) == {"frame", "point", "extent", "box"}
    jsonschema.validate(SAMPLE, ca.SCHEMA)


def _q(kind, objects, dimension="", time=None, window=None, axis="any", value_si=None, unit=""):
    return {"kind": kind, "objects": objects, "dimension": dimension, "time": time, "window": window,
            "axis": axis, "value_si": value_si, "unit": unit}


def _obs(frame, point=None, extent=None, box=None):
    return {"frame": frame, "point": point, "extent": extent, "box": box}


SAMPLE = {"questions": [
    {"qid": 101,
     "spec": {"target": _q("size", ["ball"], "diameter", unit="cm"),
              "prior": _q("speed", ["ball"], value_si=2.0), "depth": [], "notes": ""},
     "tracks": [
         {"role": "prior", "object": "ball", "obs": [_obs(0, [5, 24], box=[1, 20, 9, 28]), _obs(12, [29, 24]),
                                                     _obs(99, [1, 1])]},
         {"role": "target", "object": "white ball",
          "obs": [_obs(12, extent=[[25, 24], [33, 24]], box=[33, 28, 25, 20])]}],
     "direct_answer": 8.5, "confidence": 0.7},
    {"qid": 102,
     "spec": {"target": _q("speed", ["ball"], time=1.2, unit="m/s"), "prior": _q("speed", ["ball"], value_si=2.0),
              "depth": [], "notes": ""},
     "tracks": [{"role": "prior", "object": "Ball", "obs": []},
                {"role": "target", "object": "ball", "obs": [_obs(11, [27, 24]), _obs(13, [31, 24])]}],
     "direct_answer": 2.1, "confidence": 0.8},
    {"qid": 999, "spec": {"target": _q("size", ["x"]), "prior": _q("size", ["y"]), "depth": [], "notes": ""},
     "tracks": [], "direct_answer": 1.0, "confidence": 0.1},
]}
META = {"video_id": "vid_a", "fps": 10.0, "video_type": "V2SC", "n_frames_total": 30, "scale": 0.5,
        "image_size": [128, 96], "frames": [0, 11, 12, 13, 29],
        "questions": [{"qid": 101, "target_unit": "cm", "prior": "speed of the ball = 2m/s"},
                      {"qid": 102, "target_unit": "m/s", "prior": "speed of the ball = 2m/s"}]}


def test_to_annotations_sample_response():
    anns = ca.to_annotations(SAMPLE, META)
    assert set(anns) == {101, 102}  # unknown qid dropped
    a = anns[101]
    assert a.spec.qid == 101 and not a.spec.is_3d
    assert a.spec.target.kind == "size" and a.spec.target.dimension == "diameter" and a.spec.target.unit == "cm"
    assert a.spec.target.value_si is None and a.spec.prior.value_si == 2.0 and a.spec.prior.unit == ""
    assert a.direct_answer == 8.5 and a.confidence == 0.7
    prior, target = a.tracks
    assert prior.role == "prior" and prior.source == "claude"
    assert [o.t for o in prior.obs] == [0.0, 1.2]  # frame 99 was not sent -> dropped
    assert prior.obs[0].point == [10.0, 48.0] and prior.obs[0].box == [2.0, 40.0, 18.0, 56.0]  # scale 0.5 -> x2
    assert target.obs[0].extent == [[50.0, 48.0], [66.0, 48.0]]
    assert target.obs[0].box == [50.0, 40.0, 66.0, 56.0]  # corners normalised
    assert "unknown_frame" in a.flags and "prior_value_unverified" not in a.flags
    b = anns[102]
    assert b.spec.target.time == 1.2 and b.spec.target.kind == "speed"
    assert "reused_track" in b.flags and [o.t for o in b.tracks[0].obs] == [0.0, 1.2]
    assert [o.t for o in b.tracks[1].obs] == [1.1, 1.3]


def test_to_annotations_3d_and_bad_values():
    meta = dict(META, video_type="S3SC", scale=1.0, questions=[{"qid": 5, "target_unit": "", "prior": "h = 1.8m"}])
    parsed = {"questions": [{"qid": 5, "spec": {
        "target": _q("teleport", ["box"], unit="centimeters"), "prior": _q("size", ["man"], value_si=18.0),
        "depth": [{"object": "man", "distance_m": 4.2, "time": 0.5}, {"object": "box", "distance_m": -1, "time": None}],
        "notes": "typo"}, "tracks": [], "direct_answer": 0, "confidence": 0.2}]}
    a = ca.to_annotations(parsed, meta)[5]
    assert a.spec.is_3d and a.spec.target.kind == "other" and a.spec.target.unit == "cm"
    assert [(d.object, d.distance_m, d.time) for d in a.spec.depth] == [("man", 4.2, 0.5)]
    assert a.direct_answer is None and {"target_kind_teleport", "prior_value_model_mismatch"} <= set(a.flags)
    assert a.spec.prior.value_si == 1.8  # the prior text wins over the model's 18.0


def test_prior_value_consistent():
    assert ca.prior_value_consistent("billiard ball diameter = 57.2mm", 0.0572)
    assert ca.prior_value_consistent("t=1.5, ball acceleration = 3.0m/s^2", 3.0)
    assert ca.prior_value_consistent("diameter of the red ball = 7cm", 0.07)
    assert not ca.prior_value_consistent("diameter of the red ball = 7cm", 7.5)
    assert not ca.prior_value_consistent("speed = 6m/s", None)
    # unit slips and times taken as the value are inconsistent (they used to pass)
    for text, wrong in [("billiard ball diameter = 57.2mm", 57.2), ("billiard ball diameter = 57.2mm", 0.572),
                        ("diameter of the red ball = 7cm", 7.0), ("diameter of the red ball = 7cm", 0.007),
                        ("diameter of the ping pong ball = 40mm", 0.4), ("speed of the bird =6m/s", 0.06),
                        ("t=1.5, ball acceleration = 3.0m/s^2", 1.5), ("ruler calibre = 1cm", 1.0)]:
        assert not ca.prior_value_consistent(text, wrong), (text, wrong)


@pytest.mark.parametrize("text,expected", [
    ("billiard ball diameter = 57.2mm", (0.0572, "L")), ("diameter of the red ball = 7cm", (0.07, "L")),
    ("diameter of the ping pong ball = 40mm", (0.04, "L")), ("speed of the bird =6m/s", (6.0, "V")),
    ("t=1.5, ball acceleration = 3.0m/s^2", (3.0, "A")), ("gravity acc = 9.8m/s^2", (9.8, "A")),
    ("pedestrian walking speed ~1.1 m/s", (1.1, "V")), ("velocity of the soccer ball at 1.5s = 5.21", (5.21, "")),
    ("velocity of the yoga ball at 0.6s = 2.5104m/s", (2.5104, "V")), ("ball acceleration = 3.0m/s^2, t=1.5", (3.0, "A")),
    ("speed = 3m/s at t=1.5s", (3.0, "V")), ("speed of the car = 3 meters per second", (3.0, "V")),
    ("speed = 36 km/h", (10.0, "V")), ("speed = 5 mph", None), ("the car is 4.5m long", None), ("", None),
])
def test_prior_si(text, expected):
    got = ca.prior_si(text)
    assert got == expected if expected is None else (got[0] == pytest.approx(expected[0]) and got[1] == expected[1])


def test_prior_si_on_every_validation_prior():
    csv = ROOT / "external" / "QuantiPhy" / "model_outputs" / "gpt-5.1.csv"
    if not csv.exists():
        pytest.skip("validation CSV not present")
    for p in set(pd.read_csv(csv).ground_truth_prior):
        assert ca.prior_si(p) is not None and ca.prior_si(p)[0] > 0, p


def test_prior_value_from_text_overrides_model():
    meta = dict(META, questions=[{"qid": 1, "target_unit": "cm", "prior": "billiard ball diameter = 57.2mm"},
                                 {"qid": 2, "target_unit": "cm", "prior": "billiard ball diameter = 57.2mm"},
                                 {"qid": 3, "target_unit": "cm", "prior": "the ball is big"}])
    def q(qid, value_si, kind="size"):
        return {"qid": qid, "spec": {"target": _q("distance", ["a", "b"], unit="cm"),
                                     "prior": _q(kind, ["ball"], "diameter", value_si=value_si), "depth": [], "notes": ""},
                "tracks": [], "direct_answer": 1.0, "confidence": 0.5}
    anns = ca.to_annotations({"questions": [q(1, 0.572), q(2, 0.0572, kind="speed"), q(3, 0.3)]}, meta)
    assert anns[1].spec.prior.value_si == pytest.approx(0.0572) and "prior_value_model_mismatch" in anns[1].flags
    assert anns[2].spec.prior.value_si == pytest.approx(0.0572) and "prior_value_model_mismatch" not in anns[2].flags
    assert "prior_kind_unit_mismatch" in anns[2].flags and anns[2].spec.prior.kind == "size"  # unit decides
    assert anns[3].spec.prior.value_si == 0.3 and "prior_value_unverified" in anns[3].flags  # unparsable: model kept


# --------------------------------------------------------------------------- track reuse (smoke-test shape)

def _spec(qid, target, prior, tracks):
    return {"qid": qid, "spec": {"target": target, "prior": prior, "depth": [], "notes": ""}, "tracks": tracks,
            "direct_answer": 1.0, "confidence": 0.5}


BIRD_META = {"video_id": "simulation_0012", "fps": 24.0, "video_type": "V2MC", "n_frames_total": 61, "scale": 1.0,
             "image_size": [472, 480], "frames": list(range(0, 61, 4)),
             "questions": [{"qid": i, "target_unit": "m", "prior": "speed of the bird =6m/s"} for i in range(4)]}
BIRD_PRIOR = _q("speed", ["bird"], value_si=6.0)
MOTION = [_obs(f, [185 + 4 * f, 270]) for f in range(0, 61, 4)]
LENGTH = [_obs(f, extent=[[168 + 4 * f, 270], [200 + 4 * f, 270]], box=[168 + 4 * f, 242, 200 + 4 * f, 304])
          for f in (0, 24)]


def test_reuse_takes_the_track_that_fits():
    """Live smoke response shape: q0 prior bird points; q1 target bird length extents; q2/q3 empty bird tracks."""
    parsed = {"questions": [
        _spec(0, _q("size", ["house"], "width", unit="m"), BIRD_PRIOR,
              [{"role": "prior", "object": "bird", "obs": MOTION},
               {"role": "target", "object": "house", "obs": [_obs(0, extent=[[98, 165], [340, 165]])]}]),
        _spec(1, _q("size", ["bird"], "length", unit="m"), BIRD_PRIOR,
              [{"role": "prior", "object": "bird", "obs": []}, {"role": "target", "object": "bird", "obs": LENGTH}]),
        _spec(2, _q("size", ["bird"], "wingspan", unit="m"), BIRD_PRIOR,
              [{"role": "prior", "object": "Bird", "obs": []}, {"role": "target", "object": "bird", "obs": []}]),
        _spec(3, _q("size", ["bird"], "Length", unit="m"), BIRD_PRIOR,
              [{"role": "prior", "object": "bird", "obs": []}, {"role": "target", "object": "bird", "obs": []}]),
    ]}
    anns = ca.to_annotations(parsed, BIRD_META)
    for qid in (1, 2, 3):  # the prior always gets q0's 16-point motion track, never q1's two size boxes
        prior = anns[qid].tracks[0]
        assert len(prior.obs) == 16 and all(o.point and o.extent is None for o in prior.obs), qid
        assert "reused_track" in anns[qid].flags
    assert anns[2].tracks[1].obs == [] and "reuse_unavailable" in anns[2].flags  # no wingspan extents anywhere
    target3 = anns[3].tracks[1]  # same dimension (case-insensitive) -> q1's length extents
    assert [o.extent for o in target3.obs] == [o["extent"] for o in LENGTH]
    assert "reuse_unavailable" not in anns[3].flags
    # reused obs are copies: changing one question's track leaves the others intact
    anns[1].tracks[0].obs[0].point[0] = -1
    assert anns[2].tracks[0].obs[0].point[0] == 185


def test_reuse_with_solver_does_not_measure_the_wrong_dimension():
    pytest.importorskip("qp.geometry")
    from qp.geometry import solve
    parsed = {"questions": [
        _spec(0, _q("size", ["bird"], "length", unit="m"), BIRD_PRIOR,
              [{"role": "prior", "object": "bird", "obs": MOTION}, {"role": "target", "object": "bird", "obs": LENGTH}]),
        _spec(1, _q("size", ["bird"], "wingspan", unit="m"), BIRD_PRIOR,
              [{"role": "prior", "object": "bird", "obs": []}, {"role": "target", "object": "bird", "obs": []}]),
    ]}
    anns = ca.to_annotations(parsed, dict(BIRD_META, questions=BIRD_META["questions"][:2]))
    a0, a1 = (solve(anns[q].spec, anns[q].tracks, (472, 480), 24.0) for q in (0, 1))
    assert a0.value is not None and a1.value is None  # wingspan unsolvable rather than the length again


def test_video_info_counts_frames_without_header(tmp_path, monkeypatch):
    path = make_video(tmp_path / "v.mp4", n=17)
    real = cv2.VideoCapture

    class NoCount:
        def __init__(self, p):
            self.cap = real(p)

        def get(self, prop):
            return 0.0 if prop == cv2.CAP_PROP_FRAME_COUNT else self.cap.get(prop)

        def __getattr__(self, name):
            return getattr(self.cap, name)

    monkeypatch.setattr(ca.cv2, "VideoCapture", NoCount)
    assert ca.video_info(str(path)) == (17, 64, 48)


def test_build_request_nan_fps_uses_container_fps(workspace):
    rows = _rows(workspace, "vid_a").assign(fps=float("nan"))
    params, meta = ca.build_request(rows, n_uniform=4)
    assert meta["fps"] == pytest.approx(FPS) and meta["fps_from_container"]
    assert {11, 12, 13} <= set(meta["frames"])
    assert ca.video_fps(24.0, "unused.mp4") == (24.0, False)
    with pytest.raises(ValueError):
        ca.video_fps(float("nan"), str(workspace.root / "missing.mp4"))


# --------------------------------------------------------------------------- runner with a fake client

def _fake_message(params, n=1, drop=()):
    qids = [int(q) for q in re.findall(r"qid=(\d+)", params["messages"][0]["content"][-1]["text"])
            if int(q) not in drop]
    frames = [int(m) for b in params["messages"][0]["content"] if b["type"] == "text"
              for m in re.findall(r"^Frame (\d+) ", b["text"])]
    resp = {"questions": [{"qid": q, "spec": {"target": _q("size", ["ball"], "diameter", unit="m"),
                                              "prior": _q("speed", ["ball"], value_si=2.0), "depth": [], "notes": ""},
                           "tracks": [{"role": "target", "object": "ball",
                                       "obs": [_obs(frames[0], extent=[[1, 2], [9, 2]])]}],
                           "direct_answer": 1.5 + q, "confidence": 0.5} for q in qids]}
    return SimpleNamespace(
        id=f"msg_{n}", stop_reason="end_turn", stop_details=None,
        content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=json.dumps(resp))],
        usage=SimpleNamespace(input_tokens=1000, output_tokens=2000, cache_creation_input_tokens=0,
                              cache_read_input_tokens=500, cache_creation=None))


class FakeBatches:
    def __init__(self):
        self.created, self.status, self.fail = [], {}, set()

    def create(self, requests):
        bid = f"msgbatch_{len(self.created) + 1}"
        self.created.append((bid, list(requests)))
        self.status[bid] = "in_progress"
        return SimpleNamespace(id=bid, processing_status="in_progress")

    def retrieve(self, bid):
        counts = SimpleNamespace(processing=0, succeeded=0, errored=0, expired=0, canceled=0)
        return SimpleNamespace(id=bid, processing_status=self.status[bid], request_counts=counts)

    def results(self, bid):
        reqs = dict(self.created)[bid]
        for r in reqs:
            if r["custom_id"] in self.fail:
                res = SimpleNamespace(type="errored", error={"type": "api_error"})
            else:
                res = SimpleNamespace(type="succeeded", message=_fake_message(r["params"]))
            yield SimpleNamespace(custom_id=r["custom_id"], result=res)


class FakeStream:
    def __init__(self, msg):
        self.msg, self.request_id = msg, "req_fake"

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get_final_message(self):
        return self.msg


class FakeClient:
    def __init__(self, drop=()):
        self.batches = FakeBatches()
        self.counted, self.streamed, self.drop = 0, [], set(drop)
        self.messages = SimpleNamespace(batches=self.batches, count_tokens=self._count, stream=self._stream)

    def _count(self, **params):
        assert "max_tokens" not in params and "output_config" in params
        self.counted += 1
        return SimpleNamespace(input_tokens=1200)

    def _stream(self, **params):
        self.streamed.append(params)
        return FakeStream(_fake_message(params, len(self.streamed), self.drop))


def _argv(ws, *extra):
    return ["--csv", str(ws.csv), "--video-dir", str(ws.videos), "--name", "fake", "--frames", "4",
            "--poll-interval", "0", *extra]


def test_sync_run_records_ledger_and_csv(workspace):
    client = FakeClient()
    res = rc.main(_argv(workspace), client=client)
    assert client.counted == 1 and len(client.streamed) == 2
    recs = rc.load_records(workspace.root / "runs" / "fake" / "qs" / "records")
    assert set(recs) == {"vid_a", "vid_b"} and all(r["status"] == "ok" for r in recs.values())
    assert recs["vid_a"]["request_id"] == "req_fake" and recs["vid_a"]["usd"] == pytest.approx(0.0441)
    led = budget.entries()
    assert len(led) == 2 and all(e["mode"] == "sync" for e in led)
    assert budget.spent() == pytest.approx(2 * (0.004 + 0.04 + 0.0001))
    assert list(res.columns) == ["id", "parsed_value", "geo_value", "direct_value", "method", "flags"]
    assert res.set_index("id").parsed_value.to_dict() == {101: 102.5, 102: 103.5, 103: 104.5}
    assert set(res.method) == {"direct"} and all("no_geometry_module" in f for f in res["flags"])
    assert (workspace.root / "runs" / "fake" / "qs.csv").exists()
    # rerun: everything cached, no API traffic
    client2 = FakeClient()
    rc.main(_argv(workspace), client=client2)
    assert client2.counted == 0 and not client2.streamed and len(budget.entries()) == 2


def test_geometry_value_preferred_when_valid(workspace, monkeypatch):
    geo = types.ModuleType("qp.geometry")
    geo.solve = lambda spec, tracks, image_size, fps: Answer(
        qid=spec.qid, value=None if spec.qid == 103 else 25.0, source="geo", method="2d_scale")
    monkeypatch.setitem(sys.modules, "qp.geometry", geo)
    res = rc.main(_argv(workspace), client=FakeClient()).set_index("id")
    assert res.loc[101, "parsed_value"] == 25.0 and res.loc[101, "method"] == "geometry:2d_scale"  # 4x off: kept
    assert res.loc[101, "direct_value"] == 102.5 and "geo_direct_disagree" in res.loc[101, "flags"]
    assert res.loc[103, "parsed_value"] == 104.5 and res.loc[103, "method"] == "direct"


def test_refuses_over_budget(workspace, monkeypatch):
    monkeypatch.setenv("QP_BUDGET_USD", "0.01")
    client = FakeClient()
    res = rc.main(_argv(workspace), client=client)
    assert not client.streamed and budget.entries() == [] and res.parsed_value.isna().all()


def test_batch_resume_collect_and_retry(workspace):
    client = FakeClient()
    out = workspace.root / "runs" / "fake" / "qs"
    rc.main(_argv(workspace, "--mode", "batch", "--no-wait"), client=client)
    assert len(client.batches.created) == 1
    state = json.loads((out / "batch.json").read_text())
    (bid, reqs), = client.batches.created
    assert state["batches"][0]["id"] == bid and not state["batches"][0]["collected"]
    assert {r["custom_id"] for r in reqs} == {"vid_a", "vid_b"}
    assert reqs[0]["params"]["output_config"]["format"]["type"] == "json_schema"
    assert list(budget.open_holds()) == [bid] and budget.spent() == 0
    assert not rc.load_records(out / "records")

    # rerun while still running: polls the same batch, creates nothing new
    rc.main(_argv(workspace, "--mode", "batch", "--no-wait"), client=client)
    assert len(client.batches.created) == 1

    # batch ended (one request errored): rerun collects instead of creating a new batch
    client.batches.status[bid] = "ended"
    client.batches.fail = {"vid_b"}
    res = rc.main(_argv(workspace, "--mode", "batch", "--no-wait"), client=client)
    assert len(client.batches.created) == 1
    recs = rc.load_records(out / "records")
    assert recs["vid_a"]["status"] == "ok" and recs["vid_b"]["status"] == "errored"
    assert recs["vid_a"]["batch_id"] == bid and recs["vid_a"]["custom_id"] == "vid_a"
    assert json.loads((out / "batch.json").read_text())["batches"][0]["collected"]
    usage = [e for e in budget.entries() if e["type"] == "usage"]
    assert len(usage) == 1 and usage[0]["mode"] == "batch" and usage[0]["usd"] == pytest.approx(0.0441 / 2)
    assert budget.open_holds() == {}
    assert res.set_index("id").method.to_dict() == {101: "direct", 102: "direct", 103: "missing"}

    # collecting again is idempotent
    entry = json.loads((out / "batch.json").read_text())["batches"][0]
    cfg = SimpleNamespace(name="fake", model=ca.MODEL, effort="medium", label="qs", frames=4, max_frames=32)
    assert rc.collect(client, entry, cfg, out / "records") == {"already_collected": 2}
    assert len([e for e in budget.entries() if e["type"] == "usage"]) == 1

    # failed video is retried only on request, in a new batch with just that video
    rc.main(_argv(workspace, "--mode", "batch", "--no-wait"), client=client)
    assert len(client.batches.created) == 1
    client.batches.fail = set()
    rc.main(_argv(workspace, "--mode", "batch", "--no-wait", "--retry-failed"), client=client)
    assert len(client.batches.created) == 2
    bid2, reqs2 = client.batches.created[1]
    assert [r["custom_id"] for r in reqs2] == ["vid_b"]
    client.batches.status[bid2] = "ended"
    rc.main(_argv(workspace, "--mode", "batch", "--no-wait"), client=client)
    recs = rc.load_records(out / "records")
    assert recs["vid_b"]["status"] == "ok" and recs["vid_b"]["batch_id"] == bid2


def test_dry_run_sends_nothing(workspace):
    client = FakeClient()
    assert rc.main(_argv(workspace, "--dry-run"), client=client) is None
    assert client.counted == 1 and not client.streamed and not client.batches.created
    assert budget.entries() == []
    rc.main(_argv(workspace, "--dry-run", "--local-estimate"), client=client)
    assert client.counted == 1


def test_batch_splits_by_size(workspace):
    client = FakeClient()
    rc.main(_argv(workspace, "--mode", "batch", "--no-wait", "--batch-mb", "0.000001"), client=client)
    assert [len(reqs) for _, reqs in client.batches.created] == [1, 1]
    assert len(budget.open_holds()) == 2
    for bid, _ in client.batches.created:
        client.batches.status[bid] = "ended"
    res = rc.main(_argv(workspace, "--mode", "batch", "--no-wait"), client=client)
    assert len(client.batches.created) == 2 and budget.open_holds() == {}
    assert res.parsed_value.notna().all()


# --------------------------------------------------------------------------- regression: budget, recovery, caching

def _heavy(client):
    """Batch results that use their full max_tokens (thinking + output)."""
    orig = client.batches.results

    def results(bid):
        reqs = {q["custom_id"]: q for q in dict(client.batches.created)[bid]}
        for r in orig(bid):
            if r.result.type == "succeeded":
                r.result.message.usage.output_tokens = reqs[r.custom_id]["params"]["max_tokens"]
            yield r
    client.batches.results = results


def test_batch_worst_case_holds_keep_spend_under_cap(workspace, monkeypatch):
    monkeypatch.setenv("QP_BUDGET_USD", "0.30")
    client = FakeClient()
    _heavy(client)
    rc.main(_argv(workspace, "--mode", "batch", "--no-wait", "--effort", "max"), client=client)
    (bid, reqs), = client.batches.created
    assert [r["custom_id"] for r in reqs] == ["vid_a"]  # vid_b's worst case did not fit next to it
    assert budget.open_holds()[bid] >= 20000 * 20 / 1e6 / 2  # held at max_tokens, not the output estimate
    client.batches.status[bid] = "ended"
    rc.main(_argv(workspace, "--mode", "batch", "--no-wait", "--effort", "max"), client=client)
    assert budget.spent() <= budget.cap() and budget.committed() <= budget.cap()
    assert len(client.batches.created) == 1  # vid_b still does not fit after vid_a's real cost


def test_batch_wait_mode_submits_in_rounds(workspace, monkeypatch):
    """Without --no-wait: submit what fits, wait, collect, then submit the rest."""
    monkeypatch.setenv("QP_BUDGET_USD", "0.26")  # one worst case (~$0.20) fits, both (~$0.37) do not
    client = FakeClient()
    orig = client.batches.retrieve

    def retrieve(bid):
        client.batches.status[bid] = "ended"
        return orig(bid)
    client.batches.retrieve = retrieve
    res = rc.main(_argv(workspace, "--mode", "batch", "--effort", "max"), client=client)
    assert [len(reqs) for _, reqs in client.batches.created] == [1, 1]
    assert res.parsed_value.notna().all() and budget.open_holds() == {}
    assert budget.spent() <= budget.cap()


def test_sync_holds_worst_case_per_request(workspace, monkeypatch):
    seen = []

    class Watching(FakeClient):
        def _stream(self, **params):
            seen.append((params["max_tokens"], budget.committed()))
            return super()._stream(**params)

    rc.main(_argv(workspace, "--workers", "1"), client=Watching())
    # while a request is in flight, its max_tokens output (at $20/MTok) is held against the cap
    assert len(seen) == 2 and all(held >= mt * 20 / 1e6 for mt, held in seen)
    monkeypatch.setenv("QP_LEDGER", str(workspace.root / "ledger2.jsonl"))
    monkeypatch.setenv("QP_BUDGET_USD", "0.35")  # expected cost fits, vid_a's worst case (~$0.41) does not
    client = FakeClient()
    rc.main(_argv(workspace, "--workers", "1", "--name", "tight"), client=client)
    assert [re.findall(r"qid=(\d+)", p["messages"][0]["content"][-1]["text"]) for p in client.streamed] == [["103"]]


def test_sync_rerun_does_not_resend_videos_in_pending_batch(workspace):
    client = FakeClient()
    out = workspace.root / "runs" / "fake" / "qs"
    rc.main(_argv(workspace, "--mode", "batch", "--no-wait"), client=client)
    (bid, _), = client.batches.created
    rc.main(_argv(workspace), client=client)  # same run, default sync mode
    assert client.streamed == [] and not rc.load_records(out / "records")
    client.batches.status[bid] = "ended"
    rc.main(_argv(workspace, "--mode", "batch", "--no-wait"), client=client)
    recs = rc.load_records(out / "records")
    assert {r["batch_id"] for r in recs.values()} == {bid}


def test_collect_keeps_ok_record_from_another_source(workspace):
    client = FakeClient()
    out = workspace.root / "runs" / "fake" / "qs"
    rc.main(_argv(workspace, "--mode", "batch", "--no-wait"), client=client)
    (bid, _), = client.batches.created
    entry = json.loads((out / "batch.json").read_text())["batches"][0]
    sync_rec = {"video_id": "vid_a", "status": "ok", "mode": "sync", "parsed": {"questions": []}, "meta": entry["meta"]["vid_a"]}
    rc.save_record(out / "records", sync_rec)
    client.batches.status[bid] = "ended"
    cfg = SimpleNamespace(name="fake", model=ca.MODEL, effort="medium", label="qs", frames=4, max_frames=32)
    assert rc.collect(client, entry, cfg, out / "records") == {"kept_existing": 1, "ok": 1}
    assert rc.load_records(out / "records")["vid_a"]["mode"] == "sync"
    assert len([e for e in budget.entries() if e["type"] == "usage"]) == 2  # paid usage is still recorded
    rc.collect(client, entry, cfg, out / "records")
    assert len([e for e in budget.entries() if e["type"] == "usage"]) == 2  # ... once


def test_batch_recovered_from_ledger_when_state_is_lost(workspace):
    """A reset loses runs/ (gitignored) while the batch runs: the rerun must collect, not buy again."""
    import shutil
    client = FakeClient()
    out = workspace.root / "runs" / "fake" / "qs"
    rc.main(_argv(workspace, "--mode", "batch", "--no-wait"), client=client)
    (bid, _), = client.batches.created
    hold = [e for e in budget.entries() if e["type"] == "hold"][0]
    assert hold["split"] == "qs" and set(hold["custom_ids"].values()) == {"vid_a", "vid_b"}
    assert hold["config"]["effort"] == "medium" and "meta" not in hold  # small ledger line
    shutil.rmtree(workspace.root / "runs")
    rc.main(_argv(workspace), client=client)  # sync rerun: not re-sent either
    assert client.streamed == [] and len(client.batches.created) == 1
    rc.main(_argv(workspace, "--mode", "batch", "--no-wait"), client=client)
    assert len(client.batches.created) == 1 and json.loads((out / "batch.json").read_text())["batches"][0]["recovered"]
    client.batches.status[bid] = "ended"
    res = rc.main(_argv(workspace, "--mode", "batch", "--no-wait"), client=client)
    assert len(client.batches.created) == 1 and budget.open_holds() == {}
    recs = rc.load_records(out / "records")
    assert {v: r["status"] for v, r in recs.items()} == {"vid_a": "ok", "vid_b": "ok"}
    assert res.parsed_value.notna().all()

    # records lost again after collection: re-collected from the (released) batch for free
    shutil.rmtree(workspace.root / "runs")
    n_usage = len([e for e in budget.entries() if e["type"] == "usage"])
    res = rc.main(_argv(workspace, "--mode", "batch", "--no-wait"), client=client)
    assert len(client.batches.created) == 1 and not client.streamed
    assert len([e for e in budget.entries() if e["type"] == "usage"]) == n_usage
    assert res.parsed_value.notna().all()


def test_recovered_meta_matches_submitted_meta(workspace):
    import shutil
    client = FakeClient()
    out = workspace.root / "runs" / "fake" / "qs"
    rc.main(_argv(workspace, "--mode", "batch", "--no-wait"), client=client)
    (bid, _), = client.batches.created
    submitted = json.loads((out / "batch.json").read_text())["batches"][0]["meta"]
    shutil.rmtree(workspace.root / "runs")
    client.batches.status[bid] = "ended"
    rc.main(_argv(workspace, "--mode", "batch", "--no-wait"), client=client)
    recs = rc.load_records(out / "records")
    assert {v: r["meta"] for v, r in recs.items()} == submitted


def test_lost_sync_records_are_not_rebought(workspace):
    import shutil
    rc.main(_argv(workspace), client=FakeClient())
    shutil.rmtree(workspace.root / "runs")
    client = FakeClient()
    res = rc.main(_argv(workspace), client=client)
    assert client.streamed == [] and res.parsed_value.isna().all()
    rc.main(_argv(workspace, "--rebuy-lost"), client=client)
    assert len(client.streamed) == 2


def test_out_root_and_env(workspace, monkeypatch):
    drive = workspace.root / "drive"
    rc.main(_argv(workspace, "--out-root", str(drive)), client=FakeClient())
    assert (drive / "fake" / "qs" / "records" / "vid_a.json").exists() and (drive / "fake" / "qs.csv").exists()
    monkeypatch.setenv("QP_RUNS", str(drive))
    client = FakeClient()
    rc.main(_argv(workspace), client=client)
    assert client.streamed == [] and not (workspace.root / "runs").exists()


def test_bad_fps_or_video_does_not_abort_run(workspace):
    df = pd.read_csv(workspace.csv)
    df.loc[df.video_id == "vid_b", "fps"] = float("nan")
    df.to_csv(workspace.csv, index=False)
    client = FakeClient()
    res = rc.main(_argv(workspace), client=client).set_index("id")
    assert len(client.streamed) == 2 and res.parsed_value.notna().all()
    rec = rc.load_records(workspace.root / "runs" / "fake" / "qs" / "records")["vid_b"]
    assert rec["meta"]["fps_from_container"] and "fps_from_container" in res.loc[103, "flags"]
    # an unreadable video is skipped and reported; the others still run
    (workspace.videos / "vid_a.mp4").write_bytes(b"not a video")
    client = FakeClient()
    rc.main(_argv(workspace, "--name", "other"), client=client)
    assert len(client.streamed) == 1


def test_partial_response_is_used_and_retried(workspace):
    client = FakeClient(drop={102})
    out = workspace.root / "runs" / "fake" / "qs"
    res = rc.main(_argv(workspace), client=client).set_index("id")
    recs = rc.load_records(out / "records")
    assert recs["vid_a"]["status"] == "partial" and recs["vid_a"]["missing_qids"] == [102]
    assert res.loc[101, "parsed_value"] == 102.5 and res.loc[102, "flags"] == "qid_not_in_response"
    client = FakeClient()
    rc.main(_argv(workspace), client=client)
    assert client.streamed == []  # only on request
    res = rc.main(_argv(workspace, "--retry-failed"), client=client).set_index("id")
    assert len(client.streamed) == 1 and res.loc[102, "parsed_value"] == 103.5
    assert rc.load_records(out / "records")["vid_a"]["status"] == "ok"


def test_cached_records_with_other_settings_are_refused(workspace):
    out = workspace.root / "runs" / "fake" / "qs"
    rc.main(_argv(workspace), client=FakeClient())
    first_config = (out / "config.json").read_text()
    client = FakeClient()
    with pytest.raises(SystemExit, match="effort medium vs high"):
        rc.main(_argv(workspace, "--effort", "high"), client=client)
    with pytest.raises(SystemExit, match="max_frames 32 vs 16"):
        rc.main(_argv(workspace, "--max-frames", "16"), client=client)
    assert client.streamed == [] and (out / "config.json").read_text() == first_config
    rc.main(_argv(workspace, "--name", "fake_high", "--effort", "high"), client=client)
    assert len(client.streamed) == 2
    rec = rc.load_records(workspace.root / "runs" / "fake_high" / "qs" / "records")["vid_a"]
    assert rec["config"] == {"model": ca.MODEL, "effort": "high", "frames": 4, "max_frames": 32}


def test_output_estimate_by_effort_and_calibration():
    cfg = SimpleNamespace(est_output_per_question=0, effort="high", model=ca.MODEL)
    assert rc.output_per_question(cfg, {}) == (4000, "default for effort high")
    cfg.est_output_per_question = 1000
    assert rc.output_per_question(cfg, {})[0] == 1000
    recs = {f"v{i}": {"model": ca.MODEL, "effort": "high", "usage": {"output_tokens": 9000},
                      "meta": {"questions": [1, 2]}} for i in range(3)}
    assert rc.output_per_question(cfg, recs) == (4500, "observed on 3 videos")
    assert rc.output_per_question(cfg, dict(list(recs.items())[:2]))[0] == 1000  # too few to calibrate
