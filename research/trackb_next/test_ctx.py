"""CPU tests of the RUN_PRESET "ctx" code (qp/open/ctx_annot.py, run_ctx.py, ctx_merge.py) with mock models.

    .venv/bin/python -m pytest -q research/trackb_next/test_ctx.py
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from qp.open import ctx_annot as C  # noqa: E402
from qp.open import ctx_merge as M  # noqa: E402
from qp.spec import Obs, Quantity, QuestionSpec, RoleTrack  # noqa: E402

VAL_VIDEO = ROOT / "data" / "QuantiPhy" / "simulation_0089.mp4"
needs_video = pytest.mark.skipif(not VAL_VIDEO.exists(), reason="test videos not downloaded")


def row(qid=1, question="What is the length of the bird in meters?", prior="speed of the bird = 6 m/s",
        depth="", vtype="S2MC", unit="m", video_id="v", path="", fps=24.0):
    return SimpleNamespace(qid=qid, question=question, prior=prior, depth_info=depth, video_type=vtype,
                           target_unit=unit, video_id=video_id, video_path=path, fps=fps, video_source="simulation")


def meta_for(rows, W=2000, H=1000, w=1000, h=500, frames=(0, 10, 20), fps=10.0):
    return {"video_id": "v", "fps": fps, "fps_from_container": False, "video_type": rows[0].video_type,
            "n_frames_total": 30, "scale": w / W, "image_size": [W, H], "sent_size": [w, h], "frames": list(frames),
            "questions": [{"qid": r.qid, "target_unit": r.target_unit, "prior": r.prior, "depth_info": r.depth_info}
                          for r in rows], "prompt_version": "v1"}


# --------------------------------------------------------------------------- import / thinking

def test_import_without_gpu_deps():
    code = ("import sys; sys.path.insert(0, %r); import qp.open.ctx_annot, qp.open.run_ctx, qp.open.ctx_merge; "
            "bad = [k for k in ('torch', 'vllm', 'transformers') if k in sys.modules]; print(bad); "
            "sys.exit(1 if bad else 0)") % str(ROOT)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.parametrize("text,exp", [
    ("reasoning here</think>\n\n{\"a\": 1}", ("reasoning here", '{"a": 1}', True)),
    ("<think>r</think>ans", ("r", "ans", True)),
    ("<think>never closes", ("never closes", "", False)),
    ("plain answer", ("", "plain answer", True)),
    (None, ("", "", False)),
])
def test_split_thinking(text, exp):
    assert C.split_thinking(text) == exp


# --------------------------------------------------------------------------- ta parsing

def ta_reply(obs_prior, obs_target, qid=1, think="ok", answer=0.5):
    q = {"qid": qid, "target": {"kind": "size", "objects": ["bird"], "dimension": "length", "time": None,
                                "window": None, "axis": "any"},
         "prior": {"kind": "speed", "objects": ["bird"], "dimension": "", "time": None, "window": None, "axis": "any"},
         "tracks": [{"role": "prior", "object": "bird", "obs": obs_prior},
                    {"role": "target", "object": "bird", "obs": obs_target}],
         "answer": answer, "confidence": 0.7}
    return f"{think}</think>\n```json\n" + json.dumps({"questions": [q]}) + "\n```"


def test_parse_ta_maps_grid_to_original_pixels_and_times():
    rows = [row()]
    meta = meta_for(rows)
    prior = [{"frame": f, "point": [100 + 10 * f, 500], "extent": None, "box": [90 + 10 * f, 450, 110 + 10 * f, 550]}
             for f in (0, 10, 20)]
    target = [{"frame": 10, "point": None, "extent": [[100, 500], [300, 500]], "box": [100, 450, 300, 550]}]
    out, info = C.parse_ta(ta_reply(prior, target), meta, rows)
    a = out[1]
    assert info["closed"] and info["n_answered"] == 1 and a["direct"] == 0.5 and a["spec_source"] == "model"
    assert a["spec"].prior.value_si == pytest.approx(6.0) and a["spec"].target.unit == "m"
    tr = {t.role: t for t in a["tracks"]}
    p = tr["prior"].obs
    assert [o.t for o in p] == pytest.approx([0.0, 1.0, 2.0])                  # frame / fps
    assert p[1].point == pytest.approx([200 / 1000 * 2000, 500 / 1000 * 1000])  # grid -> original pixels
    assert tr["target"].obs[0].extent == [pytest.approx([200.0, 500.0]), pytest.approx([600.0, 500.0])]


def test_parse_ta_drops_unknown_frames_flags_outside_grid_and_fills_missing():
    rows = [row(1), row(2, question="What is the speed of the bird at 1s in m/s?")]
    meta = meta_for(rows)
    prior = [{"frame": 5, "point": [1, 1], "extent": None, "box": None},          # not a sent frame
             {"frame": 10, "point": [1500, 1], "extent": None, "box": None}]       # outside the grid
    out, info = C.parse_ta(ta_reply(prior, []), meta, rows)
    assert "unknown_frame" in out[1]["flags"] and "coord_outside_grid" in out[1]["flags"]
    assert out[2]["flags"] == ["missing_in_reply"] and out[2]["spec_source"] == "rules"
    assert out[2]["spec"].target.kind == "speed" and info["n_answered"] == 1
    prior_obs = {t.role: t for t in out[1]["tracks"]}["prior"].obs
    assert len(prior_obs) == 1 and prior_obs[0].point[0] == pytest.approx(2000.0)   # clipped to the frame


@pytest.mark.parametrize("text", [None, "", "<think>cut at max tokens", "Sure, here you go: 5 m", '{"questions": 3}'])
def test_parse_ta_unusable_replies(text):
    rows = [row()]
    out, info = C.parse_ta(text, meta_for(rows), rows)
    assert info["n_answered"] == 0 and out[1]["flags"] == ["missing_in_reply"] and out[1]["tracks"] == []


def test_parse_ta_json_inside_unclosed_reply():
    rows = [row()]
    text = ta_reply([], [{"frame": 0, "point": None, "extent": [[0, 0], [10, 0]], "box": None}]).replace("</think>", "")
    out, info = C.parse_ta("<think>" + text, meta_for(rows), rows)
    assert info.get("json_from_tail") and info["n_answered"] == 1


def test_ta_records_formats_load_in_run_open_vlm():
    rows = [row()]
    meta = meta_for(rows)
    out, info = C.parse_ta(ta_reply([], [{"frame": 0, "point": None, "extent": [[0, 0], [10, 0]], "box": None}]),
                           meta, rows)
    recs = C.ta_records("v", out, meta, "m", "x</think>{}", info)
    spec = QuestionSpec.from_dict(recs["specs"]["questions"]["1"]["spec"])
    assert spec.target.kind == "size"
    tracks = [RoleTrack.from_dict(t) for t in recs["annotate"]["tracks"]["1"]]
    assert tracks and recs["annotate"]["meta"]["image_size"] == [2000, 1000]
    assert recs["direct"]["questions"]["1"]["value"] == 0.5
    json.dumps(recs)


# --------------------------------------------------------------------------- cx

def test_cx_items_and_task_text():
    spec = QuestionSpec(1, Quantity("size", ["lane"], dimension="width", unit="m"),
                        Quantity("size", ["ruler"], dimension="calibre", value_si=0.01))
    items = C.cx_items(spec, row())
    assert [i["role"] for i in items] == ["target", "prior"]
    spec2 = QuestionSpec(2, Quantity("distance", ["cat", "dog"], time=1.0, unit="m"), Quantity("speed", ["cat"], value_si=1))
    it = C.cx_items(spec2, row())
    assert len(it) == 1 and it[0]["kind"] == "distance" and it[0]["objects"] == ["cat", "dog"]
    task, l1, l2 = C.cx_task(it[0])
    assert "first on the cat" in task and (l1, l2) == ("cat", "dog")
    req = C.cx_request(None, items[0], row(question="How wide is the lane?"))
    text = req.messages[0]["content"][1]["text"]
    assert "How wide is the lane?" in text and "speed of the bird" in text and req.thinking is False


def test_cx_frames_from_ta_record_and_fallbacks():
    item = {"qid": 1, "role": "target", "kind": "size", "objects": ["x"], "dimension": "length", "time": None}
    rec = {"tracks": {"1": [{"role": "target", "obs": [{"t": 0.0}, {"t": 1.0, "extent": [[0, 0], [1, 1]]},
                                                        {"t": 2.0, "extent": [[0, 0], [1, 1]]}]}]}}
    assert C.cx_frames(item, rec, 100, 10.0) == [10, 20]                 # extent frames first
    assert C.cx_frames(item, None, 101, 10.0) == [10, 50, 90]           # uniform 10%-90%
    d = {**item, "kind": "distance", "role": "distance", "time": 2.5}
    assert C.cx_frames(d, rec, 100, 10.0) == [25]                       # the asked time


def test_zoom_window_and_mapping_roundtrip():
    W, H = 1920, 1080
    p1, p2 = [900.0, 500.0], [1000.0, 520.0]
    box = C.zoom_window(p1, p2, W, H)
    x0, y0, x1, y1 = box
    assert x0 < 900 and x1 > 1000 and y0 < 500 and y1 > 520
    g = [(p1[0] - x0) / (x1 - x0) * 1000, (p1[1] - y0) / (y1 - y0) * 1000]
    assert C.grid_to_orig(g, box) == pytest.approx(p1)
    assert C.zoom_window([0, 0], [1900, 1000], W, H) is None              # nothing to gain
    img = C.crop_image(np.zeros((H, W, 3), np.uint8), box)
    assert max(img.size) == pytest.approx(min(C.CX_ZOOM_SIDE, 4 * max(x1 - x0, y1 - y0)), abs=1)


def test_choose_cx():
    full = [[0, 0], [100, 0]]
    assert C.choose_cx(full, [[0, 0], [110, 0]]) == ([[0, 0], [110, 0]], "zoom")
    assert C.choose_cx(full, [[0, 0], [300, 0]]) == (full, "full_zoom_rejected")
    assert C.choose_cx(full, None) == (full, "full")
    assert C.choose_cx(None, None) == (None, "full")


def test_two_points():
    assert C.two_points('[{"point_2d": [1, 2], "label": "end 1"}, {"point_2d": [3, 4], "label": "end 2"}]') == \
        [[1.0, 2.0], [3.0, 4.0]]
    assert C.two_points("[]") is None and C.two_points(None) is None
    assert C.two_points('[{"point_2d": [1, 2]}, {"point_2d": [1, 2]}]') is None


def test_cx_tracks_shared_prior_and_distance():
    rec = {"items": [
        {"qid": 1, "qids": [1, 2], "role": "prior", "kind": "size",
         "per_frame": {"10": {"chosen": [[0, 0], [10, 0]]}, "20": {"chosen": None}}},
        {"qid": 2, "qids": [2], "role": "distance", "kind": "distance",
         "per_frame": {"5": {"chosen": [[1, 1], [9, 9]]}}}]}
    t1, t2 = C.cx_tracks(rec, 1, 10.0), C.cx_tracks(rec, 2, 10.0)
    assert list(t1) == ["prior"] and t1["prior"][0].t == 1.0 and t1["prior"][0].extent == [[0, 0], [10, 0]]
    assert set(t2) == {"prior", "target", "target2"} and t2["target2"][0].point == [9, 9]


# --------------------------------------------------------------------------- merge

def _track(role, n=5, ext=False, src="s"):
    obs = [Obs(t=i / 10, point=[10.0 * i, 0.0], box=[10.0 * i - 1, -1, 10.0 * i + 1, 1],
               extent=[[0, 0], [5, 0]] if ext else None) for i in range(n)]
    return RoleTrack(role=role, object="x", obs=obs, source=src)


def test_merge_question_sources():
    spec = QuestionSpec(1, Quantity("size", ["bird"], dimension="length"), Quantity("speed", ["bird"], value_si=6))
    base = {"prior": _track("prior", src="ta"), "target": _track("target", 2, ext=True, src="ta")}
    sam = {"prior": _track("prior", 30, src="sam")}
    cx = {"target": [Obs(t=0.1, extent=[[0, 0], [7, 0]])]}
    out = {t.role: t for t in M.merge_question(spec, base, [sam], cx)}
    assert out["prior"].source == "sam" and len(out["prior"].obs) == 30 and out["prior"].object == "bird"
    assert out["target"].source == "ctx-cx" and out["target"].obs[0].extent == [[0, 0], [7, 0]]
    out2 = {t.role: t for t in M.merge_question(spec, base, [{}], {}, use_cx=False)}
    assert out2["prior"].source == "ta" and out2["target"].source == "ta"
    spec3 = QuestionSpec(3, Quantity("distance", ["cat", "dog"], time=0.1), Quantity("speed", ["cat"], value_si=1))
    cx3 = {"target": [Obs(t=0.1, point=[0, 0])], "target2": [Obs(t=0.1, point=[3, 4])]}
    out3 = {t.role: t for t in M.merge_question(spec3, {}, [sam], cx3)}
    assert out3["target2"].object == "dog" and out3["target2"].obs[0].point == [3, 4]


def test_tracks_rescaled_to_base_image_size():
    rec = {"meta": {"image_size": [854, 480]}, "tracks": {"1": [_track("prior").to_dict()]}}
    tr = M._tracks(rec, 1, (1708, 960))["prior"]
    assert tr.obs[1].point == pytest.approx([20.0, 0.0]) and tr.obs[1].box[2] == pytest.approx(22.0)


# --------------------------------------------------------------------------- real video, mock model

@needs_video
def test_ta_request_on_real_video():
    from qp.data import load_split
    df = load_split("val_hires")
    rows = df[df.video_id == "simulation_0089"]
    req, meta = C.ta_request(rows)
    imgs = [c for c in req.messages[1]["content"] if c["type"] == "image"]
    labels = [c["text"] for c in req.messages[1]["content"] if c["type"] == "text" and c["text"].startswith("Frame ")]
    assert len(imgs) == len(req.images) == len(meta["frames"]) == len(labels) <= C.TA_MAX_FRAMES
    assert max(req.images[0].size) <= C.TA_MAX_SIDE and meta["scale"] == pytest.approx(req.images[0].size[0] / meta["image_size"][0])
    assert req.thinking and req.max_tokens == C.ta_max_tokens(len(rows), True)
    assert all(f"qid={int(q)}" in req.messages[1]["content"][-1]["text"] for q in rows.qid)


@needs_video
def test_run_ctx_end_to_end_with_mock(tmp_path):
    """run_ctx on one real video with a mock model: records written, resumable, merge + geometry run."""
    from qp.open import run_ctx

    class Mock:
        def __init__(self):
            self.n = 0

        def generate(self, reqs):
            self.n += len(reqs)
            out = []
            for r in reqs:
                if r.messages[0].get("content") == C.TA_SYSTEM:
                    qids = [int(x) for x in __import__("re").findall(r"qid=(\d+)", r.messages[1]["content"][-1]["text"])]
                    frames = [int(c["text"].split()[1]) for c in r.messages[1]["content"]
                              if c["type"] == "text" and c["text"].startswith("Frame ")]
                    qs = [{"qid": q, "target": {"kind": "size", "objects": ["bird"], "dimension": "length"},
                           "prior": {"kind": "speed", "objects": ["bird"]},
                           "tracks": [{"role": "prior", "object": "bird",
                                       "obs": [{"frame": f, "point": [100 + 20 * k, 500], "box": None, "extent": None}
                                               for k, f in enumerate(frames)]},
                                      {"role": "target", "object": "bird",
                                       "obs": [{"frame": frames[0], "point": None, "box": [90, 480, 130, 520],
                                                "extent": [[90, 500], [130, 500]]}]}],
                           "answer": 1.0, "confidence": 0.5} for q in qids]
                    out.append("thought</think>" + json.dumps({"questions": qs}))
                else:
                    out.append('[{"point_2d": [400, 500], "label": "end 1"}, {"point_2d": [600, 500], "label": "end 2"}]')
            return out

    m = Mock()
    argv = ["--split", "val_hires", "--out", str(tmp_path), "--videos", "simulation_0089"]
    assert run_ctx.main(argv, backend=m) == 0
    n1 = m.n
    assert (tmp_path / "ta" / "annotate" / "simulation_0089.json").exists()
    assert (tmp_path / "cx" / "simulation_0089.json").exists() and (tmp_path / "ta" / "direct.csv").exists()
    run_ctx.main(argv, backend=m)
    assert m.n == n1                                                   # finished video skipped
    cx = json.loads((tmp_path / "cx" / "simulation_0089.json").read_text())
    assert cx["items"] and all(v["how"] in ("zoom", "full", "full_zoom_rejected")
                               for it in cx["items"] for v in it["per_frame"].values())
    M.main(["--split", "val_hires", "--root", str(tmp_path), "--variants", "ta,tacx"])
    import pandas as pd
    g = pd.read_csv(tmp_path / "tacx" / "geometry.csv")
    qids = [int(q) for q in json.loads((tmp_path / "ta" / "annotate" / "simulation_0089.json").read_text())["tracks"]]
    rows = g[g.id.isin(qids)]
    assert len(rows) and rows.geo_value.notna().any()
