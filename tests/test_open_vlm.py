import ast
import importlib.util
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from qp import claude_annotate as ca
from qp.data import _finalize, target_unit
from qp.open import caw as C
from qp.open import qwen_vl as Q
from qp.prompts import DIRECT_SYSTEM
from qp.spec import KIND_DIM, KINDS, QuestionSpec

ROOT = Path(__file__).resolve().parents[1]
VAL_CSV = ROOT / "external/QuantiPhy/model_outputs/gpt-5.1.csv"
SAMPLE_CSV = ROOT / "external/QuantiPhy/model_run_example/GT_CIB_Ready/CIB_Ready - test4.csv"
SAMPLE_DIR = ROOT / "external/QuantiPhy/model_run_example/data/all_480p"
AUTHORS = Path("/home/user/ref/Code-as-World/code_as_world")

needs_val = pytest.mark.skipif(not VAL_CSV.exists(), reason="official repo not cloned into external/")
needs_sample = pytest.mark.skipif(not SAMPLE_CSV.exists(), reason="sample videos not available")


def val_rows() -> list:
    df = pd.read_csv(VAL_CSV).rename(columns={"Unnamed: 0": "qid", "ground_truth_prior": "prior"})
    df["depth_info"] = df["depth_info"].fillna("").astype(str)
    df["target_unit"] = [target_unit(q) for q in df.question]
    return list(df.drop(columns=["ground_truth_posterior", "parsed_value"]).itertuples(index=False))


def sample_df() -> pd.DataFrame:
    raw = pd.read_csv(SAMPLE_CSV)
    raw.insert(0, "qid", range(len(raw)))
    raw = raw.rename(columns={"ground_truth_prior": "prior", "ground_truth_posterior": "answer"})
    return _finalize(raw, SAMPLE_DIR).drop(columns=["answer"])


def _load_script():
    spec = importlib.util.spec_from_file_location("run_open_vlm", ROOT / "scripts" / "run_open_vlm.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakeBackend:
    """Replies via `fn(request) -> str`; keeps every request."""

    def __init__(self, fn):
        self.fn, self.calls = fn, []

    def generate(self, reqs):
        self.calls.append(list(reqs))
        return [self.fn(r) for r in reqs]


def _text(req) -> str:
    content = req.messages[-1]["content"]
    return content if isinstance(content, str) else " ".join(c.get("text", "") for c in content)


# --------------------------------------------------------------------------- importability

def test_import_without_gpu_deps():
    code = ("import sys, importlib.util; sys.path.insert(0, %r); import qp.open.qwen_vl, qp.open.caw; "
            "s = importlib.util.spec_from_file_location('r', %r); m = importlib.util.module_from_spec(s); "
            "s.loader.exec_module(m); "
            "bad = [k for k in ('torch', 'vllm', 'transformers', 'qwen_vl_utils', 'decord') if k in sys.modules]; "
            "print(bad); sys.exit(1 if bad else 0)") % (str(ROOT), str(ROOT / "scripts" / "run_open_vlm.py"))
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


# --------------------------------------------------------------------------- JSON extraction

@pytest.mark.parametrize("text,expected", [
    ('{"a": 1}', {"a": 1}),
    ('```json\n[{"bbox_2d": [1, 2, 3, 4], "label": "bird"}]\n```', [{"bbox_2d": [1, 2, 3, 4], "label": "bird"}]),
    ('Sure! Here it is:\n{"target": {"kind": "size"}, "notes": "a {brace} in text"}\nHope this helps.',
     {"target": {"kind": "size"}, "notes": "a {brace} in text"}),
    ('{"a": [1, 2,], "b": None, "c": True,}', {"a": [1, 2], "b": None, "c": True}),
    ("{'a': 'x', 'b': null}", {"a": "x", "b": None}),
    ('<think>maybe {"wrong": 1}</think>{"right": 2}', {"right": 2}),
    ('```json\n[{"bbox_2d": [1, 2, 3, 4], "label": "a"}, {"bbox_2d": [5, 6, 7', [{"bbox_2d": [1, 2, 3, 4], "label": "a"}]),
    ('{"x": 1, "y": Infinity}', {"x": 1, "y": math.inf}),
])
def test_extract_json(text, expected):
    assert Q.extract_json(text) == expected


def test_non_finite_numbers_become_none():
    d = Q.extract_json('{"value_si": NaN, "time": "1.5s"}')
    assert Q._num(d["value_si"]) is None and Q._time(d["time"]) == 1.5 and Q._time("at the end") == math.inf


@pytest.mark.parametrize("text,expected", [
    ('The spec for "speed [m/s]":\n{"a": 1}', {"a": 1}),
    ('Coordinates [0-1000 grid]: [{"bbox_2d": [1, 2, 3, 4]}]', [{"bbox_2d": [1, 2, 3, 4]}]),
    ("{not json} but {'b': 2}", {"b": 2}),
])
def test_extract_json_skips_bracketed_prose(text, expected):
    assert Q.extract_json(text) == expected


@pytest.mark.parametrize("text", [None, "", "no json here", "{broken", "[1, 2"])
def test_extract_json_none(text):
    assert Q.extract_json(text) is None


def test_parse_grounding_formats():
    assert Q.parse_grounding('```json\n[\n\t{"bbox_2d": [74, 361, 324, 808], "label": "plate"}\n]\n```') == [
        {"box": [74.0, 361.0, 324.0, 808.0], "point": None, "label": "plate"}]
    assert Q.parse_grounding('{"bbox_2d": [1, 2, 3, 4]}')[0]["box"] == [1, 2, 3, 4]
    assert Q.parse_grounding("[10, 20, 30, 40]")[0]["box"] == [10, 20, 30, 40]
    assert Q.parse_grounding('[{"point_2d": [346, 328], "label": "person"}]')[0]["point"] == [346, 328]
    assert Q.parse_grounding('garbage "bbox_2d": [5, 6, 7, 8] trailing')[0]["box"] == [5, 6, 7, 8]
    assert Q.parse_grounding("I cannot see a ball.") == []
    assert Q.parse_grounding("[]") == []


# --------------------------------------------------------------------------- coordinates / frames

def test_to_pixels_rel1000_maps_to_original_size():
    assert Q.to_pixels([500, 500], (854, 480)) == pytest.approx([427.0, 240.0])
    assert Q.box_to_pixels([300, 400, 100, 200], (1000, 500)) == pytest.approx([100, 100, 300, 200])
    assert Q.to_pixels([1200, -5], (854, 480)) == pytest.approx([854.0, 0.0])          # clipped
    # independent of the size the model saw
    assert Q.to_pixels([250, 750], (854, 480), sent=(427, 240)) == pytest.approx([213.5, 360.0])


def test_to_pixels_abs_mode_rescales_from_sent_image():
    assert Q.to_pixels([100, 50], (854, 480), sent=(427, 240), mode="abs") == pytest.approx([200.0, 100.0])
    with pytest.raises(ValueError):
        Q.to_pixels([1, 1], (10, 10), mode="nope")


def test_smart_resize():
    h, w = Q.smart_resize(480, 854)
    assert h % 32 == 0 and w % 32 == 0 and h * w <= Q.FRAME_PIXELS
    assert abs(w / h - 854 / 480) < 0.1
    assert Q.smart_resize(20, 20, min_pixels=128 * 32 * 32) == (384, 384)


def test_annotate_frames_keeps_uniform_and_adds_asked_times():
    idxs = Q.annotate_frames(n_total=100, fps=10, times=[2.0], n_uniform=5, max_frames=40)
    assert set(Q.uniform_indices(100, 5)) <= set(idxs)
    assert {18, 19, 20, 21, 22} <= set(idxs)
    assert len(Q.annotate_frames(100, 10, [1.0, 2.0, 3.0, 4.0, 5.0], n_uniform=5, max_frames=12)) == 12
    assert max(Q.annotate_frames(30, 10, [9.0], 4, 10)) == 29                    # clipped to the clip


# --------------------------------------------------------------------------- rule-based parsing on real text

@needs_val
def test_prior_value_for_every_validation_prior():
    priors = sorted({r.prior for r in val_rows()})
    assert len(priors) >= 20
    for p in priors:
        d = Q.parse_prior_text(p)
        assert d["value_si"] is not None and d["value_si"] > 0, p
        assert ca.prior_value_consistent(p, d["value_si"]), p
        assert d["kind"] in KINDS
        if d["unit"]:
            assert KIND_DIM[d["kind"]] == Q._unit_dim(d["unit"]), p
        assert d["objects"] or d["gravity"], p


@pytest.mark.parametrize("prior,value,kind,objects,time", [
    ("billiard ball diameter = 57.2mm", 0.0572, "size", ["billiard ball"], None),
    ("t=1.5, ball acceleration = 3.0m/s^2", 3.0, "acceleration", ["ball"], 1.5),
    ("velocity of the soccer ball at 1.5s = 5.21", 5.21, "speed", ["soccer ball"], 1.5),
    ("pedestrian walking speed ~1.1 m/s", 1.1, "speed", ["pedestrian"], None),
    ("speed of the bubble in the drop = 0.00144m/s", 0.00144, "speed", ["bubble in the drop"], None),
    ("gravity acc = 9.8m/s^2", 9.8, "acceleration", [], None),
    ("diameter of the red ball = 7cm", 0.07, "size", ["red ball"], None),
    ("speed of the bird =6m/s", 6.0, "speed", ["bird"], None),
])
def test_prior_examples(prior, value, kind, objects, time):
    d = Q.parse_prior_text(prior)
    assert d["value_si"] == pytest.approx(value) and d["kind"] == kind
    assert d["objects"] == objects and d["time"] == time


@pytest.mark.parametrize("prior,value,objects,time", [
    ("speed of the car = 3 m/s (t = 2 s)", 3.0, ["car"], 2.0),            # a trailing time is not the value
    ("speed of the car = 3m/s at t=2s", 3.0, ["car"], 2.0),
    ("ball diameter = 6.7 cm, t = 0s", 0.067, ["ball"], 0.0),
    ("width of door=0.9 m, t=1s", 0.9, ["door"], 1.0),
    ("height of the person: 1.8m", 1.8, ["person"], None),
    ("length of the car is 4.5 meters", 4.5, ["car"], None),
    ("the ball's diameter is 22 cm", 0.22, ["ball"], None),
    ("speed of car = 3, t=2", 3.0, ["car"], 2.0),                          # unitless, then a time
])
def test_prior_value_formats(prior, value, objects, time):
    d = Q.parse_prior_text(prior)
    assert d["value_si"] == pytest.approx(value) and d["objects"] == objects and d["time"] == time
    assert not d["ambiguous"]


def test_prior_value_ambiguity():
    d = Q.parse_prior_text("speed of the 10m long boat = 3m/s")
    assert d["value_si"] == 3.0 and d["kind"] == "speed" and d["ambiguous"]
    assert d["values_si"] == [(10.0, "L"), (3.0, "V")]
    assert Q.parse_prior_text("mass of the ball = 0.5kg")["value_si"] is None


@needs_val
def test_no_validation_prior_is_ambiguous():
    assert not any(Q.parse_prior_text(r.prior)["ambiguous"] for r in val_rows())


@needs_val
def test_depth_for_every_validation_depth_string():
    depths = sorted({r.depth_info for r in val_rows() if r.depth_info})
    assert len(depths) >= 10
    for s in depths:
        entries = Q.parse_depth(s)
        assert len(entries) == s.count("distance_"), s
        for e, line in zip(entries, [ln for ln in s.splitlines() if "distance_" in ln]):
            assert e.distance_m > 0 and e.object and "_" not in e.object and "camera" not in e.object
            assert (e.time is not None) == bool(re.search(r"\bt\s*=", line)), line
    e = Q.parse_depth("t = 1.0s, distance_car_camera = 17.8278 m\ndistance_pier_camera = 1890cm")
    assert [(x.object, round(x.distance_m, 6), x.time) for x in e] == [("car", 17.8278, 1.0), ("pier", 18.9, None)]


@needs_val
def test_rule_spec_for_every_validation_question():
    for r in val_rows():
        s = Q.rule_spec(r)
        assert s.target.kind in KINDS and s.prior.kind in KINDS
        # the official inference_type says static (S, a length) or dynamic (D) for prior and target
        assert (KIND_DIM[s.target.kind] == "L") == (r.inference_type[1] == "S"), r.question
        assert (KIND_DIM[s.prior.kind] == "L") == (r.inference_type[0] == "S"), r.prior
        if s.target.unit:
            assert Q._unit_dim(s.target.unit) == KIND_DIM[s.target.kind], r.question
        assert s.prior.value_si and s.prior.value_si > 0
        assert s.target.objects and all(s.target.objects), r.question
        if s.target.kind == "distance":
            assert len(s.target.objects) == 2, r.question
        assert s.is_3d == (r.video_type[1] == "3")
        assert bool(s.depth) == bool(r.depth_info.strip())
        QuestionSpec.from_dict(json.loads(json.dumps(s.to_dict())))  # serialisable round trip


@pytest.mark.parametrize("q,kind,objects,time,window,axis", [
    ("What is the white ball's average velocity in 1.00s to 2.00s in cm/s?", "speed", ["white ball"], None,
     [1.0, 2.0], "any"),
    ("What is the distance between the two black road signs in meters?", "distance",
     ["black road sign", "black road sign"], None, None, "any"),
    ("When t=3s, what is the minimum distance from the outer end of the pier to the boat in meters?", "distance",
     ["outer end of the pier", "boat"], 3.0, None, "any"),
    ("What is the final distance between the purple ball and the black ball in cm?", "distance",
     ["purple ball", "black ball"], math.inf, None, "any"),
    ("What is the eagle’s wingspan (the distance from the tip of one wing to the tip of the other when fully "
     "spread) in meters?", "size", ["eagle"], None, None, "any"),
    ("What is the total distance traveled by the left tennis ball in cm?", "path_length", ["left tennis ball"],
     None, None, "any"),
    ("What is the soccer ball's diasplacement between 1.5s and 1.6s in meters? ", "displacement", ["soccer ball"],
     None, [1.5, 1.6], "any"),
    ("What is the velolicty of the ball at 1.5s in cm/s? ", "speed", ["ball"], 1.5, None, "any"),
    ("What is the (average) horizontal velocity of the ball in m/s?", "speed", ["ball"], None, None, "horizontal"),
])
def test_question_examples(q, kind, objects, time, window, axis):
    d = Q.parse_question_text(q)
    assert (d["kind"], d["objects"], d["time"], d["window"], d["axis"]) == (kind, objects, time, window, axis)


# --------------------------------------------------------------------------- model spec validation

def _row(question, prior, depth="", video_type="V2SC", qid=1):
    return SimpleNamespace(qid=qid, question=question, prior=prior, depth_info=depth, video_type=video_type,
                           target_unit=target_unit(question))


def _q(kind, objects, **kw):
    return {"kind": kind, "objects": objects, "dimension": "", "time": None, "window": None, "axis": "any",
            "value_si": None, "unit": "", **kw}


def test_validate_spec_repairs_from_text():
    row = _row("What is the white ball's average velocity in 1.00s to 2.00s in cm/s?",
               "billiard ball diameter = 57.2mm")
    parsed = {"target": _q("velocity", "white ball", unit="m/s", window=["1.00s", "2.00s"]),
              "prior": _q("size", ["billiard ball"], value_si=57.2, dimension="diameter"), "notes": ""}
    spec, flags = Q.validate_spec(parsed, row)
    assert spec.target.kind == "speed" and spec.target.objects == ["white ball"]
    assert spec.target.window == [1.0, 2.0] and spec.target.unit == "cm/s"          # unit from the question
    assert spec.prior.value_si == pytest.approx(0.0572) and "prior_value_from_text" in flags


def test_validate_spec_prior_value_kept_or_replaced():
    q = "What is the length of the boat in meters?"
    cases = [("speed of the car = 3 m/s (t = 2 s)", 2.0, 3.0, True),        # wrong model value -> text
             ("speed of the car = 3 m/s (t = 2 s)", 3.0, 3.0, False),
             ("speed of the 10m long boat = 3m/s", 3.0, 3.0, False),
             ("speed of the 10m long boat = 3m/s", 10.0, 3.0, True),        # a length is no speed
             ("speed of the boat = 3m/s, later 5m/s", 5.0, 5.0, False),     # ambiguous text: model's pick kept
             ("billiard ball diameter = 57.2mm", 57.2, 0.0572, True)]
    for prior, model, want, flagged in cases:
        spec, flags = Q.validate_spec({"target": _q("size", ["boat"]), "prior": _q("speed", ["car"], value_si=model)},
                                      _row(q, prior))
        assert spec.prior.value_si == pytest.approx(want) and ("prior_value_from_text" in flags) == flagged, prior


@pytest.mark.parametrize("q,unit,kind", [
    ("What is the speed of the car in meters per second?", "m/s", "speed"),
    ("What is the speed of the car in cm per second?", "cm/s", "speed"),
    ("What is the acceleration of the car in m/s2?", "m/s^2", "acceleration"),
    ("What is the acceleration of the car in meters per second squared?", "m/s^2", "acceleration"),
    ("What is the length of the car in meters?", "m", "size"),
    ("What is the speed of the car in km/h?", "km/h", "speed"),
])
def test_spelled_out_units_keep_the_model_kind(q, unit, kind):
    row = _row(q, "length of the car = 4m")
    spec, flags = Q.validate_spec({"target": _q(kind, ["car"]), "prior": _q("size", ["car"], value_si=4.0)}, row)
    assert (spec.target.kind, spec.target.unit) == (kind, unit) and "target_kind_from_rules" not in flags
    rs = Q.rule_spec(row)
    assert (rs.target.kind, rs.target.unit) == (kind, unit)


@needs_val
def test_question_unit_matches_data_loader_on_validation():
    for r in val_rows():
        assert Q._row_unit(r) == r.target_unit, r.question


@pytest.mark.parametrize("q,prior,model,kind", [
    ("What is the total distance traveled by the left tennis ball in cm?", "diameter of the tennis ball = 6.7cm",
     _q("distance", ["left tennis ball"]), "path_length"),
    ("What is the soccer ball's diasplacement between 1.5s and 1.6s in meters?",
     "velocity of the soccer ball at 1.5s = 5.21", _q("distance", ["soccer ball"], window=[1.5, 1.6]), "displacement"),
])
def test_validate_spec_single_object_distance_takes_rule_kind(q, prior, model, kind):
    spec, flags = Q.validate_spec({"target": model, "prior": _q("size", ["tennis ball"])}, _row(q, prior))
    assert spec.target.kind == kind and "target_kind_from_rules" in flags


def test_validate_spec_fixes_inconsistent_kinds_and_missing_fields():
    row = _row("What is the speed of the car at 2s, in m/s?", "acceleration of the car = 5m/s^2",
               depth="t=2s, distance_car_camera = 23.2m", video_type="A3SX")
    parsed = {"target": _q("size", []), "prior": _q("speed", ["car"], value_si=5), "notes": None}
    spec, flags = Q.validate_spec(parsed, row)
    assert spec.target.kind == "speed" and spec.target.objects == ["car"] and spec.target.time == 2.0
    assert spec.prior.kind == "acceleration" and spec.is_3d and spec.depth[0].distance_m == 23.2
    assert {"target_kind_from_rules", "target_objects_from_rules", "target_time_from_rules",
            "prior_kind_from_rules"} <= set(flags)


def test_validate_spec_times_and_gravity():
    row = _row("What is the final distance between the purple ball and the black ball in cm?", "gravity acc = 9.8m/s^2")
    parsed = {"target": _q("distance", ["purple ball", "black ball"], time="final"),
              "prior": _q("acceleration", ["falling object"], value_si=9.8), "notes": ""}
    spec, _ = Q.validate_spec(parsed, row)
    assert spec.target.time == math.inf and spec.prior.axis == "vertical"
    assert not any(Q.groundable(o) for o in spec.prior.objects) and Q.is_gravity(spec, row.prior)
    spec, _ = Q.validate_spec({"target": _q("distance", ["a", "b"], time=1e9), "prior": _q("size", ["x"])},
                              _row("What is the distance between a and b in m?", "x width = 1m"))
    assert spec.target.time == math.inf


@pytest.mark.parametrize("parsed", [None, [], {}, {"target": "size"}, {"target": {}, "prior": {}},
                                    {"target": _q("blah", []), "prior": _q("nope", [])}])
def test_validate_spec_rejects_unusable(parsed):
    spec, _ = Q.validate_spec(parsed, _row("What is the length of the bird in meters?", "speed of the bird =6m/s"))
    assert spec is None


def test_spec_request_and_fewshot_examples_are_valid():
    row = _row("What is the length of the bird in meters?", "speed of the bird =6m/s")
    req = Q.spec_request(row)
    assert req.messages[0] == {"role": "system", "content": Q.SPEC_SYSTEM} and req.json_schema == Q.SPEC_SCHEMA
    assert req.messages[-1]["role"] == "user" and "speed of the bird =6m/s" in req.messages[-1]["content"]
    assert "none (2D video)" in req.messages[-1]["content"] and req.temperature == 0
    for prior, depth, question, out in Q._FEWSHOT:
        spec, flags = Q.validate_spec(json.loads(json.dumps(out)), _row(question, prior, depth))
        assert spec is not None and not [f for f in flags if f != "prior_objects_from_rules"], (question, flags)
    assert Q.spec_request(row, guided=False).json_schema is None


@needs_val
def test_parse_specs_retries_then_falls_back():
    rows = val_rows()[:3]
    good = json.dumps({"target": _q("size", ["wood block"], dimension="length", unit="cm"),
                       "prior": _q("size", ["ruler"], value_si=0.01), "notes": ""})
    seen = {}

    def reply(req):
        q = req.messages[-1]["content"]
        seen.setdefault(q, 0)
        seen[q] += 1
        if rows[0].question in q:
            return good                                        # first attempt OK
        if rows[1].question in q:
            return "sorry" if seen[q] == 1 else "```json\n" + good + "\n```"   # OK on the retry
        return "I don't know"                                  # never -> rule-based

    fake = FakeBackend(reply)
    out = Q.QwenVL(backend=fake).parse_specs(pd.DataFrame(rows), retries=2)
    a, b, c = (out[int(r.qid)] for r in rows)
    assert a["attempts"] == 1 and a["source"] == Q.DEFAULT_MODEL and a["spec"].prior.value_si == pytest.approx(0.01)
    assert b["attempts"] == 2 and len(b["raw"]) == 2
    assert c["source"] == "rules" and c["flags"] == ["rule_fallback"] and len(c["raw"]) == 3
    assert c["spec"].target.kind == "speed"
    assert [len(x) for x in fake.calls] == [3, 2, 1]
    assert fake.calls[0][0].temperature == 0 and fake.calls[1][0].temperature > 0


# --------------------------------------------------------------------------- annotate (fake model, real video)

def _moving_box_fake(boxes_per_call=None):
    """Grounding replies whose box moves 10 units per call of the same object (calls come in frame order)."""
    counts = {}

    def reply(req):
        t = _text(req)
        if req.video is not None:
            return "The red ball."
        name = re.search(r'Locate (?:the (.+?) in the image|every instance .*?"(.+?)")', t)
        name = name.group(1) or name.group(2)
        counts[name] = counts.get(name, -1) + 1
        k = counts[name]
        if boxes_per_call == 2:
            return json.dumps([{"bbox_2d": [600 + 5 * k, 400, 650 + 5 * k, 450], "label": name},
                               {"bbox_2d": [100, 400, 150, 450], "label": name}])
        return '```json\n[{"bbox_2d": [%d, 200, %d, 400], "label": "%s"}]\n```' % (100 + 10 * k, 300 + 10 * k, name)
    return reply


@needs_sample
def test_annotate_on_sample_video_maps_coordinates_and_times():
    df = sample_df()
    rows = df[df.video_id == "simulation_0012"]
    specs = {int(r.qid): Q.rule_spec(r) for r in rows.itertuples()}
    fake = FakeBackend(_moving_box_fake())
    rec = Q.QwenVL(backend=fake).annotate_videos([rows], specs, n_uniform=8, max_frames=12)["simulation_0012"]
    W, H = rec["meta"]["image_size"]
    assert (W, H) == (472, 480) and rec["meta"]["fps"] == 24.0
    frames = rec["meta"]["frames"]
    assert len(frames) == 8 and frames[0] == 0 and frames[-1] == 60
    reqs = fake.calls[0]
    assert len(reqs) == len(rec["objects"]) * len(frames)
    assert reqs[0].messages[0]["content"][0] == {"type": "image"} and reqs[0].images[0].size == (472, 480)
    for qid, tracks in rec["tracks"].items():
        roles = {t["role"]: t for t in tracks}
        assert {"prior", "target"} <= set(roles), qid
        assert roles["prior"]["object"] == "bird"
        obs = roles["prior"]["obs"]
        assert [o["t"] for o in obs] == pytest.approx([i / 24 for i in frames])
        assert obs[0]["box"] == pytest.approx([100 / 1000 * W, 200 / 1000 * H, 300 / 1000 * W, 400 / 1000 * H])
        assert obs[1]["box"][0] == pytest.approx(110 / 1000 * W)
    json.dumps(rec)


@needs_sample
def test_annotate_identifies_object_for_gravity_prior():
    df = sample_df()
    rows = df[df.video_id == "simulation_0020"]                    # gravity prior; asks a person's height
    specs = {int(r.qid): Q.rule_spec(r) for r in rows.itertuples()}
    assert specs[int(rows.qid.iloc[0])].prior.objects == []
    fake = FakeBackend(_moving_box_fake())
    rec = Q.QwenVL(backend=fake).annotate_videos([rows], specs, n_uniform=6, max_frames=6)["simulation_0020"]
    ident = fake.calls[0][0]
    frames, meta = ident.video
    assert len(fake.calls[0]) == 1 and meta["fps"] == 30.0 and len(meta["frames_indices"]) % 2 == 0
    assert frames.shape[0] == len(meta["frames_indices"]) and frames.shape[1] % 32 == 0
    assert rec["identified_prior_object"] == "red ball"
    roles = {t["role"]: t for t in rec["tracks"][str(int(rows.qid.iloc[0]))]}
    assert roles["prior"]["object"] == "red ball" and roles["target"]["object"] == "person"
    assert len(roles["prior"]["obs"]) == 6


@needs_sample
def test_annotate_two_instances_of_one_name():
    df = sample_df()
    rows = df[df.video_id == "simulation_0012"].head(1).copy()
    rows["question"] = "What is the distance between the two black cars at 1.0s in meters?"
    rows["target_unit"] = "m"
    spec = Q.rule_spec(next(rows.itertuples()))
    assert spec.target.objects == ["black car", "black car"]
    fake = FakeBackend(_moving_box_fake(boxes_per_call=2))
    rec = Q.QwenVL(backend=fake).annotate_videos([rows], {spec.qid: spec}, n_uniform=5, max_frames=5)
    tracks = {t["role"]: t for t in rec["simulation_0012"]["tracks"][str(spec.qid)]}
    a, b = tracks["target"]["obs"], tracks["target2"]["obs"]
    assert len(a) == len(b) == 5
    assert all(o["box"][0] < 100 for o in a) and all(o["box"][0] > 250 for o in b)  # A = leftmost, kept
    assert 'Locate every instance' in _text(fake.calls[0][-1])


def test_pick_continuous_follows_nearest():
    c = lambda x: {"box": [x, 0, x + 10, 10], "point": None, "label": ""}  # noqa: E731
    got = Q.pick_continuous({0: [c(0), c(500)], 1: [c(490), c(15)], 2: [], 3: [c(30)]})
    assert [got[i][0]["box"][0] for i in (0, 1, 3)] == [0, 15, 30] and got[1][1] == 2 and 2 not in got


def test_roles_and_keys():
    spec = Q.rule_spec(_row("What is the distance between the cat and the dog at 2s in meters?",
                            "length of the dog = 0.8m"))
    assert Q.roles_for(spec) == [("prior", "dog"), ("target", "cat"), ("target2", "dog")]
    assert Q._key("Black  Car 2") == "black car 2" and Q._key("car 1") != Q._key("car 2")
    assert Q._base("Black  Car 2") == "Black Car" and Q._base("ball #1") == "ball" and Q._base("car") == "car"
    assert not Q.groundable("gravity") and not Q.groundable("falling object") and Q.groundable("red ball")


@needs_sample
def test_annotate_keeps_numbered_objects_apart():
    """'car 1' (prior) and 'car 2' (target) are two objects; 'ball 1' / 'ball 2' of one distance are a pair."""
    df = sample_df()
    rows = df[df.video_id == "simulation_0012"].head(2).copy()
    rows["prior"] = "speed of car 1 = 5m/s"
    rows["question"] = ["What is the speed of car 2 in m/s?",
                        "What is the distance between ball 1 and ball 2 in meters?"]
    rows["target_unit"] = ["m/s", "m"]
    specs = {int(r.qid): Q.rule_spec(r) for r in rows.itertuples()}
    fake = FakeBackend(lambda r: '[{"bbox_2d": [100, 100, 200, 200]}]')
    rec = Q.QwenVL(backend=fake).annotate_videos([rows], specs, n_uniform=3, max_frames=3)["simulation_0012"]
    asked = {_text(r).strip() for r in fake.calls[0]}
    assert {Q.GROUND_PROMPT.format(name="car 1"), Q.GROUND_PROMPT.format(name="car 2"),
            Q.GROUND_ALL_PROMPT.format(name="ball")} == asked
    assert set(rec["objects"]) == {"car 1", "car 2", "ball [pair]#1", "ball [pair]#2"}
    q0 = {t["role"]: t["object"] for t in rec["tracks"][str(int(rows.qid.iloc[0]))]}
    assert q0 == {"prior": "car 1", "target": "car 2"}


@needs_sample
def test_annotate_extents_per_asked_dimension():
    """One object asked in two dimensions (prior: its width, target: its height): each size role gets the
    extents of its own dimension (with only the first dimension's, the height came out as the prior)."""
    from qp.geometry import solve
    df = sample_df()
    rows = df[df.video_id == "simulation_0012"].head(2).copy()
    rows["prior"] = "width of the car = 2m"
    rows["question"] = ["What is the height of the car in meters?", "What is the speed of the car in m/s?"]
    rows["target_unit"] = ["m", "m/s"]
    specs = {int(r.qid): Q.rule_spec(r) for r in rows.itertuples()}

    def reply(r):
        text = _text(r)
        if "ends of the width" in text:
            return '[{"point_2d": [100, 500], "label": "end 1"}, {"point_2d": [300, 500], "label": "end 2"}]'
        if "ends of the height" in text:
            return '[{"point_2d": [200, 400], "label": "end 1"}, {"point_2d": [200, 450], "label": "end 2"}]'
        return '[{"bbox_2d": [100, 400, 300, 450], "label": "car"}]'

    fake = FakeBackend(reply)
    rec = Q.QwenVL(backend=fake).annotate_videos([rows], specs, n_uniform=4, max_frames=4, extents=True,
                                                 n_extent=2)["simulation_0012"]
    asked = [_text(r) for r in fake.calls[0] if "Point to the two ends" in _text(r)]
    assert sum("width" in a for a in asked) == sum("height" in a for a in asked) == 2
    W, H = rec["meta"]["image_size"]
    qid = int(rows.qid.iloc[0])
    roles = {t["role"]: t for t in rec["tracks"][str(qid)]}
    lengths = {role: {round(math.dist(*o["extent"]), 6) for o in t["obs"] if o["extent"]} for role, t in roles.items()}
    assert lengths == {"prior": {round(0.2 * W, 6)}, "target": {round(0.05 * H, 6)}}
    ans = solve(specs[qid], [Q.RoleTrack.from_dict(t) for t in rec["tracks"][str(qid)]], (W, H), rec["meta"]["fps"])
    assert ans.value == pytest.approx(2.0 * 0.05 * H / (0.2 * W))


@needs_sample
@pytest.mark.parametrize("reply", ["\n", " ", ""])
def test_identify_tolerates_blank_replies(reply):
    df = sample_df()
    rows = df[df.video_id == "simulation_0020"]
    specs = {int(r.qid): Q.rule_spec(r) for r in rows.itertuples()}
    box = _moving_box_fake()
    fake = FakeBackend(lambda r: reply if r.video is not None else box(r))
    rec = Q.QwenVL(backend=fake).annotate_videos([rows], specs, n_uniform=4, max_frames=4)["simulation_0020"]
    assert rec["identified_prior_object"] is None and "error" not in rec


def test_parse_grounding_skips_malformed_numbers():
    assert Q.parse_grounding('"bbox_2d": [-, -, -, -]') == []
    assert Q.parse_grounding("point_2d: [., .]") == []
    got = Q.parse_grounding('"bbox_2d": [-, ., -, -] then "bbox_2d": [10, 20, 30, 40] "label": x}')
    assert [g["box"] for g in got] == [[10, 20, 30, 40]]


class Boom(Q.HFBackend):
    """HF backend whose every request raises (CUDA OOM), without loading a model."""

    def __init__(self):
        self.torch, self.n = SimpleNamespace(cuda=SimpleNamespace(is_available=lambda: False)), 0

    def _one(self, r):
        self.n += 1
        raise RuntimeError("CUDA out of memory")


@needs_sample
def test_failed_generations_are_marked_not_blank():
    assert Boom().generate([Q.Request(messages=[])] * 2) == [None, None]
    df = sample_df()
    rows = df[df.video_id == "simulation_0012"]
    vl = Q.QwenVL(backend=Boom())
    out = vl.direct_answer([rows], n_frames=4)
    assert all(a["error"] and a["value"] is None for a in out.values())
    specs = vl.parse_specs(rows, retries=1)
    assert all(s["error"] and s["source"] == "rules" for s in specs.values())
    rec = vl.annotate_videos([rows], {q: s["spec"] for q, s in specs.items()}, n_uniform=3, max_frames=3)
    assert set(rec["simulation_0012"]) == {"video_id", "error"}
    fake = FakeBackend(lambda r: None if "bird" in _text(r) else '[{"bbox_2d": [1, 2, 3, 4]}]')  # partial failure
    rec = Q.QwenVL(backend=fake).annotate_videos([rows], {q: s["spec"] for q, s in specs.items()}, 3, 3)
    assert "error" in rec["simulation_0012"]


# --------------------------------------------------------------------------- direct answers

@needs_sample
def test_direct_answer_prompt_and_parsing():
    df = sample_df()
    rows = df[df.video_id == "simulation_0012"]
    fake = FakeBackend(lambda r: "150 cm" if "length of the bird" in _text(r) else "20 m")
    out = Q.QwenVL(backend=fake).direct_answer([rows], n_frames=32)
    req = fake.calls[0][0]
    assert req.messages[0] == {"role": "system", "content": DIRECT_SYSTEM}
    assert req.messages[1]["content"][0] == {"type": "video"}
    text = req.messages[1]["content"][1]["text"]
    assert text.startswith("The clip is 2.54 s long at 24 fps; 32 frames are shown. Given that speed of the bird =6m/s.")
    assert text.endswith("Please answer the question with numbers and units ONLY. No explanation needed.")
    frames, meta = req.video
    assert meta["fps"] == 24.0 and len(meta["frames_indices"]) == frames.shape[0] == 32
    assert frames.dtype == np.uint8 and frames.shape[1] % 32 == 0 and frames.shape[2] % 32 == 0
    kw = Q.video_kwargs(frames)                       # processor keeps the frames as sent
    assert kw["do_sample_frames"] is False and kw["size"]["longest_edge"] == 32 * frames.shape[1] * frames.shape[2]
    by_q = {r.question: out[int(r.qid)]["value"] for r in rows.itertuples()}
    assert by_q["What is the length of the bird in meters?"] == pytest.approx(1.5)        # cm -> m
    assert by_q["What is the width between the two widest eaves of the house in meters?"] == pytest.approx(20)


@needs_sample
def test_direct_answer_without_unit_is_read_in_si():
    df = sample_df()
    rows = df[df.video_id == "simulation_0012"].head(1).copy()
    rows["question"], rows["target_unit"] = "What is the orbital diameter of the Io model?", ""
    assert Q.answer_unit(next(rows.itertuples())) == "m"
    out = Q.QwenVL(backend=FakeBackend(lambda r: "331 cm")).direct_answer([rows], n_frames=4)
    assert out[int(rows.qid.iloc[0])]["value"] == pytest.approx(3.31)


# --------------------------------------------------------------------------- Code-as-World recipe

def _caw_row(prior="speed of the bird =6m/s", question="What is the length of the bird in meters", depth=""):
    return SimpleNamespace(prior=prior, question=question, depth_info=depth, qid=1, fps=24, target_unit="m")


def test_caw_prompt_text():
    assert C.format_prompt(_caw_row()) == (
        "<video> Given that speed of the bird =6m/s. What is the length of the bird in meters?\n\n"
        "Please answer the question with numbers and units ONLY. No explanation needed.")
    r = _caw_row("diameter of the ball = 0.21m", "Given that diameter of the ball = 0.21m, what is the speed?",
                 "t=1s, distance_ball_camera = 2m")
    assert C.content(r) == ("Given that diameter of the ball = 0.21m. Additionally, you have the following "
                            "information about the distance between the objects in the video and the shooting "
                            "camera: t=1s, distance_ball_camera = 2m. What is the speed?")
    msgs = C.build_messages(_caw_row())
    assert msgs[0] == {"role": "system", "content": C.SYSTEM_PROMPT}
    assert msgs[1]["content"][0] == {"type": "video"} and msgs[1]["content"][1]["text"].startswith(" Given that")


def _authors_namespace() -> dict:
    """The authors' text functions, executed from their evaluation.py without its vLLM imports."""
    tree = ast.parse((AUTHORS / "evaluation.py").read_text())
    keep = {"_clean_text", "_normalise_question", "_content_from_record", "_strip_answer_tags", "_parse_prediction"}
    names = {"SYSTEM_PROMPT", "NUMBER_PATTERN", "_GIVEN_THAT_RE_TEMPLATE", "DEPTH_PREFIX"}
    body = [n for n in tree.body if (isinstance(n, ast.FunctionDef) and n.name in keep) or (
        isinstance(n, ast.Assign) and any(getattr(t, "id", "") in names for t in n.targets))]
    ns = {"re": re, "Any": object}
    exec(compile(ast.Module(body=body, type_ignores=[]), "evaluation.py", "exec"), ns)
    return ns


@needs_val
@pytest.mark.skipif(not AUTHORS.exists(), reason="Code-as-World not cloned into /home/user/ref")
def test_caw_matches_authors_on_validation_rows():
    ns = _authors_namespace()
    template = (AUTHORS / "templates" / "quantiphy_video.jinja").read_text().strip()
    assert C.SYSTEM_PROMPT == ns["SYSTEM_PROMPT"] and C.DEPTH_PREFIX == ns["DEPTH_PREFIX"]
    for r in val_rows():
        rec = {"ground_truth_prior": ns["_clean_text"](r.prior), "question": r.question,
               "raw_question": ns["_clean_text"](r.question), "depth_info": ns["_clean_text"](r.depth_info)}
        theirs = template.replace("{{ content | trim }}", ns["_content_from_record"](rec).strip())
        assert C.format_prompt(r) == theirs
    for reply in ("1.5 m", "<answer>2.27e3 cm</answer>", "about 3", "none", "-0.5 m/s"):
        assert C.parse_prediction(reply) == ns["_parse_prediction"](reply)


def test_caw_parse_and_retry():
    assert C.parse("150 cm", "m")["value"] == pytest.approx(1.5)
    assert C.parse("150 cm", "m")["authors_value"] == 150.0
    assert C.parse("<answer>2.27×10^3 m</answer>", "m")["value"] == pytest.approx(2270)
    assert C.parse("about 0", "m")["value"] is None and C.parse(None, "m")["value"] is None
    assert C.retry_nframes("nframes should in interval [2, 12], but got 16.") == 12
    assert C.retry_nframes("nframes should in interval [2, 15], but got 14.") is None
    assert C.retry_nframes("other error") is None


def test_caw_token_layout():
    assert C.calculate_timestamps([0, 2, 4], 2.0) == [0.5, 2.0]
    enc = lambda s: [900 + len(s)]  # noqa: E731
    ids = C.expand_video_tokens([1, 7, 8, 9, 2], (2, 4, 4), [0.5, 2.0], enc, start=7, pad=8, end=9)
    assert ids == [1, 900 + len("<0.5 seconds>"), 7, 8, 8, 8, 8, 9, 900 + len("<2.0 seconds>"), 7, 8, 8, 8, 8, 9, 2]
    with pytest.raises(ValueError):
        C.expand_video_tokens([1, 2], (1, 2, 2), [0.0], enc, 7, 8, 9)


def test_caw_direct_answer_with_fake_engine():
    class Fake(C.CAW):
        def read(self, path):
            return np.zeros((16, 3, 28, 28)), {"fps": 30.0, "frames_indices": list(range(0, 32, 2)),
                                               "total_num_frames": 32, "video_backend": "decord", "junk": 1}, 2.0, None

        def prompt_ids(self, row):
            return [1, 2, 3]

    eng = FakeBackend(lambda item: "1.2 m")
    rows = pd.DataFrame([{"qid": 5, "video_id": "v", "video_path": "x.mp4", "fps": 24.0, "prior": "p = 1m",
                          "question": "How long?", "depth_info": "", "target_unit": "cm"}])
    out = Fake(backend=eng).direct_answer([rows])
    (row, ids, (video, meta), pkw), = eng.calls[0]
    assert pkw == {"fps": 24.0, "do_sample_frames": False} and meta["fps"] == 24.0 and "junk" not in meta
    assert out[5]["value"] == pytest.approx(120.0) and out[5]["authors_value"] == 1.2
    rows = rows.assign(question="What is the orbital diameter of the Io model?", target_unit="")
    assert Fake(backend=FakeBackend(lambda item: "331 cm")).direct_answer([rows])[5]["value"] == pytest.approx(3.31)
    out = Fake(backend=FakeBackend(lambda item: None)).direct_answer([rows])          # no engine output
    assert out[5]["value"] is None and out[5]["error"]


# --------------------------------------------------------------------------- CLI

class FakeRunner:
    """Stands in for QwenVL in the CLI: real QwenVL task code over a fake backend."""

    def __init__(self):
        good = lambda r: json.dumps({"target": _q("size", ["bird"], unit="m"),  # noqa: E731
                                     "prior": _q("speed", ["bird"], value_si=6.0), "notes": ""})
        boxes = _moving_box_fake()
        self.fake = FakeBackend(lambda r: good(r) if r.json_schema else (
            "50 m" if r.video is not None and r.messages[0]["role"] == "system" else boxes(r)))
        self.vl = Q.QwenVL(backend=self.fake)
        self.model = self.vl.model

    def __getattr__(self, name):
        return getattr(self.vl, name)


@needs_sample
def test_cli_direct_annotate_geometry_and_resume(tmp_path):
    mod = _load_script()
    base = ["--csv", str(SAMPLE_CSV), "--video-dir", str(SAMPLE_DIR), "--name", "t", "--out", str(tmp_path)]
    runner = FakeRunner()
    res = mod.main(base + ["--task", "direct", "--frames", "8"], runner=runner)
    assert list(res.columns) == ["id", "parsed_value"] and (res.parsed_value == 50.0).all()
    assert (tmp_path / "direct.csv").exists() and len(list((tmp_path / "direct").glob("*.json"))) == 2
    n = len(runner.fake.calls)
    mod.main(base + ["--task", "direct"], runner=runner)                       # cached: no new calls
    assert len(runner.fake.calls) == n

    res = mod.main(base + ["--task", "annotate", "--geometry", "--ground-frames", "6", "--max-ground-frames", "8"],
                   runner=runner)
    assert len(list((tmp_path / "specs").glob("*.json"))) == 2
    assert len(list((tmp_path / "annotate").glob("*.json"))) == 2
    assert list(res.columns) == ["id", "parsed_value", "geo_value", "direct_value", "method", "flags"]
    assert len(res) == 4 and res.parsed_value.notna().all() and (res.direct_value == 50.0).all()
    # simulation_0012 (472x480, 24 fps), 6 uniform frames 12 apart: the bird box moves 10/1000 * 472 px per
    # 0.5 s = 9.44 px/s = 6 m/s; the box is 94.4 px wide (qid 0 asks a width) and 96 px tall (max side)
    bird = res[res.id.isin([0, 1, 2])].sort_values("id")
    assert bird.method.str.startswith("geometry").all()
    assert bird.geo_value.tolist() == pytest.approx([94.4 * 6 / 9.44, 96 * 6 / 9.44, 96 * 6 / 9.44], rel=0.02)
    spec_rec = json.loads(next((tmp_path / "specs").glob("simulation_0012.json")).read_text())
    assert all(q["spec"]["prior"]["value_si"] == 6.0 for q in spec_rec["questions"].values())
    n = len(runner.fake.calls)
    res2 = mod.main(base + ["--task", "geometry"])                             # CPU only, no runner
    assert len(runner.fake.calls) == n and len(res2) == 4
    assert res2.parsed_value.tolist() == pytest.approx(res.parsed_value.tolist())


class FailingRunner(FakeRunner):
    """FakeRunner whose backend fails every request (HF backend, CUDA OOM)."""

    def __init__(self):
        super().__init__()
        self.vl = Q.QwenVL(backend=Boom())


@needs_sample
def test_cli_failed_generations_are_not_cached(tmp_path):
    mod = _load_script()
    base = ["--csv", str(SAMPLE_CSV), "--video-dir", str(SAMPLE_DIR), "--name", "t", "--out", str(tmp_path)]
    res = mod.main(base + ["--task", "direct", "--frames", "4"], runner=FailingRunner())
    assert res.parsed_value.isna().all()
    assert all(not json.loads(p.read_text())["questions"] for p in (tmp_path / "direct").glob("*.json"))
    mod.main(base + ["--task", "annotate", "--ground-frames", "3", "--max-ground-frames", "3"], runner=FailingRunner())
    assert all(not json.loads(p.read_text())["questions"] for p in (tmp_path / "specs").glob("*.json"))
    assert all(not json.loads(p.read_text())["tracks"] for p in (tmp_path / "annotate").glob("*.json"))
    runner = FakeRunner()                                     # the next run redoes everything
    assert (mod.main(base + ["--task", "direct", "--frames", "4"], runner=runner).parsed_value == 50.0).all()
    mod.main(base + ["--task", "annotate", "--ground-frames", "3", "--max-ground-frames", "3"], runner=runner)
    assert all(len(json.loads(p.read_text())["tracks"]) for p in (tmp_path / "annotate").glob("*.json"))


@needs_sample
def test_cli_loads_specs_once_and_skips_missing_videos(tmp_path, monkeypatch, capsys):
    mod = _load_script()
    calls = []
    real = mod.specs_from
    monkeypatch.setattr(mod, "specs_from", lambda d: (calls.append(d), real(d))[1])
    vids = tmp_path / "videos"
    vids.mkdir()
    (vids / "simulation_0012.mp4").symlink_to(SAMPLE_DIR / "simulation_0012.mp4")   # simulation_0020 missing
    base = ["--csv", str(SAMPLE_CSV), "--video-dir", str(vids), "--name", "t", "--out", str(tmp_path / "out")]
    runner = FakeRunner()
    mod.main(base + ["--task", "specs"], runner=runner)                  # text only: both videos
    assert len(list((tmp_path / "out" / "specs").glob("*.json"))) == 2
    calls.clear()
    mod.main(base + ["--task", "annotate", "--chunk-videos", "1", "--ground-frames", "3", "--max-ground-frames", "3"],
             runner=runner)
    assert len(calls) == 1                                             # not once per chunk
    assert [p.stem for p in (tmp_path / "out" / "annotate").glob("*.json")] == ["simulation_0012"]
    assert "1 videos not found locally" in capsys.readouterr().out
    res = mod.main(base + ["--task", "direct", "--frames", "4"], runner=runner)
    assert len(res) == 4 and res.parsed_value.isna().sum() == 1       # simulation_0020's question
    with pytest.raises(SystemExit):
        mod.main(["--csv", str(SAMPLE_CSV), "--video-dir", str(tmp_path / "none"), "--name", "t",
                  "--out", str(tmp_path / "o2"), "--task", "direct"], runner=runner)


def test_run_geometry_rejects_blowups_and_bad_direct_path(tmp_path, monkeypatch):
    import qp.geometry as G
    from qp.spec import Answer, Obs, RoleTrack
    mod = _load_script()
    geo = {1: 9.76e14, 2: 50.0, 3: 8.0, 4: 50.0}                       # in m (SI)
    monkeypatch.setattr(G, "solve", lambda spec, tracks, size, fps: Answer(
        qid=spec.qid, value=geo[spec.qid], source="geometry", method="2d_scale", debug={"value_si": geo[spec.qid]}))
    qs, tracks = {}, {}
    for q in geo:
        spec = Q.rule_spec(_row("What is the length of the bird in meters?", "speed of the bird =6m/s", qid=q))
        qs[str(q)] = {"spec": spec.to_dict()}
        tracks[str(q)] = [RoleTrack("prior", "bird", [Obs(t=0.0, box=[0, 0, 10, 10])], "qwen3vl").to_dict()]
    mod.save_json(tmp_path / "specs" / "v.json", {"video_id": "v", "questions": qs})
    mod.save_json(tmp_path / "annotate" / "v.json", {"video_id": "v", "meta": {"image_size": [472, 480], "fps": 24.0},
                                                     "tracks": tracks})
    pd.DataFrame({"id": [1, 2, 3], "parsed_value": [0.9, 2.0, 2.0]}).to_csv(tmp_path / "direct.csv", index=False)
    df = pd.DataFrame({"qid": list(geo), "video_id": "v"})
    res = mod.run_geometry(df, tmp_path).set_index("id")
    assert res.parsed_value.tolist() == [0.9, 2.0, 8.0, 50.0]
    assert res.method.tolist() == ["direct", "direct", "geometry:2d_scale", "geometry:2d_scale"]
    assert "geo_rejected_implausible" in res["flags"][1] and "geo_rejected_disagree" in res["flags"][2]
    assert "geo_direct_disagree" in res["flags"][3] and "rejected" not in res["flags"][3]
    assert res.geo_value[1] == 9.76e14                                   # raw geometry kept for diagnostics
    assert mod.run_geometry(df, tmp_path, max_disagree=0).parsed_value.tolist() == [0.9, 50.0, 8.0, 50.0]
    with pytest.raises(SystemExit, match="not found"):
        mod.run_geometry(df, tmp_path, direct_from=str(tmp_path / "typo.csv"))
