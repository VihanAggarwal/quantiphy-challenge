"""CPU tests of the Track B agentic measurement loop (qp/open/agent_loop.py, qp/open/run_agent.py) with a scripted fake
model: action parsing, the Python sandbox (timeout, guard), FRAME images, malformed replies, the step / time caps and
the forced ANSWERS turn, fallback filling, twins, batching and resume."""
from __future__ import annotations

import json
import math
import re
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import pytest

from qp.open import agent_loop as AL
from qp.open import run_agent as RA

FPS = 24.0


def _video(path: Path, n: int = 48, w: int = 320, h: int = 240) -> Path:
    vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (w, h))
    for i in range(n):
        im = np.full((h, w, 3), 40, np.uint8)
        cv2.circle(im, (20 + 5 * i, 120), 12, (0, 0, 255), -1)
        vw.write(im)
    vw.release()
    return path


def _df(tmp_path: Path, videos=("clip_a",), qids_per=2, twin=False) -> pd.DataFrame:
    rows, q = [], 1
    for v in list(videos) + ([f"{videos[0]}_segmented"] if twin else []):
        p = _video(tmp_path / f"{v}.mp4")
        for k in range(qids_per):
            rows.append({"qid": q, "video_id": v, "video_path": str(p), "video_type": "S2MC", "fps": FPS,
                         "inference_type": "SS", "question": f"What is the size {k} of the red ball in meters?",
                         "prior": "diameter of the red ball = 0.5m", "depth_info": "", "video_source": "simulation",
                         "category": "S2", "target_unit": "m", "answer": 1.0})
            q += 1
    return pd.DataFrame(rows)


def _text(req) -> str:
    c = req.messages[-1]["content"]
    return c if isinstance(c, str) else " ".join(x.get("text", "") for x in c)


def _qids(req) -> list[int]:
    first = req.messages[1]["content"][0]["text"]
    return [int(x) for x in re.findall(r"- qid (\d+)", first)]


class Scripted:
    """Replies by turn number of each conversation: script[i] (str or callable(req) -> str); the forced final prompt
    always gets `final(req)`."""

    def __init__(self, script, final=None, thinking_tag=False):
        self.script, self.final, self.calls, self.reqs = script, final, [], []
        self.tag = thinking_tag

    def generate(self, reqs):
        self.calls.append(len(reqs))
        out = []
        for r in reqs:
            self.reqs.append(r)
            if "STOP:" in _text(r):
                out.append(self.final(r) if self.final else "ANSWERS {}")
                continue
            n = sum(1 for m in r.messages if m["role"] == "assistant")
            s = self.script[min(n, len(self.script) - 1)]
            s = s(r) if callable(s) else s
            out.append(("thinking...</think>\n" + s) if self.tag else s)
        return out


def _answers(req, scale=1.0):
    return "ANSWERS " + json.dumps({str(q): 0.5 * scale * (i + 1) for i, q in enumerate(_qids(req))})


def _run(tmp_path, df, backend, extra=(), monkeypatch=None):
    monkeypatch.setattr("qp.data.load_split", lambda split: df)
    out = tmp_path / "out"
    argv = ["--split", "val_hires", "--out", str(out), "--ws-root", str(tmp_path / "ws"), "--no-thinking",
            "--tool-workers", "2", *extra]
    assert RA.main(argv, backend=backend) == 0
    return out


# --------------------------------------------------------------------------- parsing

def test_parse_action_kinds_and_first_wins():
    q = [12, 13]
    a = AL.parse_action("Let me check.\n```python\nprint(1)\n```", q)
    assert (a.kind, a.payload, a.n_actions) == ("python", "print(1)", 1)
    a = AL.parse_action("Zoom in.\nFRAME 1.5 100 200 400 500 3", q)
    assert a.kind == "frame" and a.payload == {"grid": True, "t": 1.5, "box": [100, 200, 400, 500], "scale": 3.0}
    a = AL.parse_action("**Action:** FRAME #37 nogrid", q)
    assert a.payload == {"grid": False, "idx": 37, "scale": 1.0}
    a = AL.parse_action("FRAME t=2.0 box=[1,2,30,40] scale=2", q)
    assert a.payload["t"] == 2.0 and a.payload["box"] == [1, 2, 30, 40] and a.payload["scale"] == 2
    a = AL.parse_action("FRAME 1.0\n```python\nprint(2)\n```", q)
    assert a.kind == "frame" and a.n_actions == 2
    a = AL.parse_action('```python\nprint("FRAME 1")\nprint("ANSWERS {1: 2}")\n```', q)
    assert a.kind == "python" and a.n_actions == 1
    assert AL.parse_action("I think the frame shows the ball. Frame 3 is clear.", q).kind == "none"
    a = AL.parse_action("FRAME\n", q)
    assert a.kind == "frame" and a.payload is None and a.error


def test_parse_answers_lenient():
    q = [12, 13]
    assert AL.parse_action('ANSWERS {"12": 3.4, "13": "0.85 m"}', q).payload == {12: 3.4, 13: 0.85}
    assert AL.parse_action('ANSWERS\n```json\n{12: -3.4, "13": 0,}\n```', q).payload == {12: 3.4}   # abs; 0 dropped
    assert AL.parse_action('ANSWERS {"12": 1.5, "13": 2', q).payload == {12: 1.5, 13: 2.0}           # cut off
    assert AL.parse_answers('ANSWERS {"12": NaN, "13": "inf", "99": 4}', q) == {}
    got = AL.parse_answers('{"answers": [{"qid": 12, "answer": 2.0}, {"qid": 13, "value": "5 cm"}]}', q, anywhere=True)
    assert got == {12: 2.0, 13: 5.0}
    assert AL.parse_answers("qid 12: 3.1, qid 13 = 4e-1", q, anywhere=True) == {12: 3.1, 13: 0.4}
    assert AL.parse_answers("no numbers here", q, anywhere=True) == {}


def test_split_reply_thinking():
    assert AL.split_reply("plan</think>\nFRAME 1", True) == ("plan", "FRAME 1", True)
    assert AL.split_reply("<think>long plan never closed", True)[2] is False      # cut at max_tokens
    assert AL.split_reply("no tags at all", True)[2] is False                     # template opened <think>
    assert AL.split_reply("FRAME 1", False) == ("", "FRAME 1", True)
    assert AL.split_reply(None, False)[2] is False


# --------------------------------------------------------------------------- tools

def _clip(tmp_path) -> AL.Clip:
    df = _df(tmp_path)
    return AL.clips_from_df(df.drop(columns=["answer"]))[0]


def test_sandbox_timeout_truncation_and_guard(tmp_path):
    ws = tmp_path / "ws" / "clip_a"
    AL.prepare_workspace(_clip(tmp_path), ws)
    t0 = time.time()
    txt, imgs, _ = AL.run_python("import time\nprint('start', flush=True)\ntime.sleep(30)", ws, 1, timeout=1.0)
    assert time.time() - t0 < 10 and txt.startswith("Python result: TIMEOUT") and "start" in txt and not imgs
    txt, _, _ = AL.run_python("print('x' * 20000)\nraise ValueError('boom')", ws, 2, timeout=20, max_chars=600)
    assert "bytes omitted" in txt and "ValueError: boom" in txt and len(txt) < 1400 and "<frozen runpy>" not in txt
    secret = tmp_path / "labels.csv"
    secret.write_text("qid,answer\n1,1.0\n")
    code = (f"try:\n    open({str(secret)!r}).read(); print('READ')\nexcept PermissionError as e: print('denied')\n"
            "import os\nprint('env', sorted(k for k in os.environ if 'TOKEN' in k or 'KEY' in k))\n"
            "import socket\ntry:\n    socket.create_connection(('example.com', 80), timeout=2); print('NET')\n"
            "except PermissionError: print('nonet')\n")
    txt, _, _ = AL.run_python(code, ws, 3, timeout=20, deny=[str(tmp_path)])
    assert "denied" in txt and "READ" not in txt and "env []" in txt and "nonet" in txt


def test_qptools_and_show_images(tmp_path):
    ws = tmp_path / "ws" / "clip_a"
    AL.prepare_workspace(_clip(tmp_path), ws)
    code = ("from qptools import *\nprint(W, H, N, FPS, len(QUESTIONS), t2i(1.0))\n"
            "im = frame(t2i(1.0)); r = im[:, :, 2] > 200; ys, xs = np.nonzero(r); print('cx', int(xs.mean()))\n"
            "print('n', sum(1 for _ in frames(0, None, 4)))\nshow(r, 'mask'); show(grid(im), 'grid'); show(im, 'x')")
    txt, imgs, caps = AL.run_python(code, ws, 1, timeout=60, show_max=2)
    assert "320 240 48 24.0 2 24" in txt and "cx 140" in txt and "n 12" in txt
    assert len(imgs) == 2 and "mask" in caps[0] and "1 more" in caps[2]
    img, cap = AL.render_frame(str(ws / "video.mp4"), FPS, 48, t=1.0, box=[100, 80, 180, 160], scale=3)
    assert img.size == (240, 240) and "crop x 100..180" in cap and "Frame #24" in cap
    img, cap = AL.render_frame(str(ws / "video.mp4"), FPS, 48, idx=999, max_side=160)
    assert max(img.size) == 160 and "Frame #47" in cap


# --------------------------------------------------------------------------- the loop

def test_scripted_clip_python_frame_malformed_answers(tmp_path, monkeypatch):
    df = _df(tmp_path)
    be = Scripted(["Measure.\n```python\nfrom qptools import *\nprint('W', W)\n```",
                   "Zoom.\nFRAME 1.0 100 80 180 160 2",
                   "hmm, I am not sure what to do",
                   _answers])
    out = _run(tmp_path, df, be, monkeypatch=monkeypatch)
    rec = json.loads((out / "answers" / "clip_a.json").read_text())
    assert rec["answers"] == {"1": 0.5, "2": 1.0} and rec["end"] == "done" and rec["n_steps"] == 4
    assert rec["forced"] is None and set(rec["source"].values()) == {"agent"}
    # the python result, the frame image and the no-action note reached the model
    texts = [_text(r) for r in be.reqs]
    assert "W 320" in texts[1] and "FRAME shown above" in texts[2] and "No action found" in texts[3]
    assert [len(r.images) for r in be.reqs] == [1, 1, 2, 2]          # overview sheet, then + the FRAME crop
    tr = json.loads((out / "transcripts" / "clip_a.json").read_text())
    assert [t.get("action") for t in tr["turns"] if t["role"] == "assistant"] == ["python", "frame", "none", "answers"]
    a = pd.read_csv(out / "agent.csv")
    assert a.columns[:2].tolist() == ["id", "parsed_value"] and a.parsed_value.tolist() == [0.5, 1.0]
    assert not (tmp_path / "ws" / "clip_a").exists()                   # workspace removed after the clip


def test_step_cap_forces_final_and_fallback_fills(tmp_path, monkeypatch):
    df = _df(tmp_path)
    fb = tmp_path / "fb.csv"
    pd.DataFrame({"id": [1, 2], "parsed_value": [7.0, -9.0]}).to_csv(fb, index=False)
    be = Scripted(["```python\nprint(1)\n```"], final=lambda r: 'Sure. ANSWERS {"1": "2.5 m"}')
    out = _run(tmp_path, df, be, ["--max-steps", "3", "--fallback-csv", str(fb)], monkeypatch)
    rec = json.loads((out / "answers" / "clip_a.json").read_text())
    assert rec["n_steps"] == 3 and "action budget" in rec["forced"] and rec["answers"] == {"1": 2.5}
    assert rec["missing"] == [2] and rec["source"] == {"1": "forced"}
    final_req = be.reqs[-1]
    assert "STOP:" in _text(final_req) and final_req.temperature == 0.0 and not final_req.thinking
    a = pd.read_csv(out / "agent.csv").set_index("id")
    f = pd.read_csv(out / "agent_filled.csv").set_index("id")
    assert math.isnan(a.parsed_value[2]) and f.parsed_value.to_dict() == {1: 2.5, 2: 9.0}
    assert f.source.to_dict() == {1: "forced", 2: "fallback"}


def test_partial_answers_asked_again_then_workspace_file(tmp_path, monkeypatch):
    df = _df(tmp_path)
    be = Scripted(['ANSWERS {"1": 3}', "```python\nimport json\njson.dump({'2': 4.5}, open('answers.json','w'))\n```",
                   "nothing"], final=lambda r: "I cannot.")
    out = _run(tmp_path, df, be, ["--max-steps", "3"], monkeypatch)
    rec = json.loads((out / "answers" / "clip_a.json").read_text())
    assert "qid(s) [2] have no valid" in _text(be.reqs[1])
    assert rec["answers"] == {"1": 3.0, "2": 4.5} and rec["source"] == {"1": "agent", "2": "workspace_file"}


def test_thinking_cut_reply_retries_without_thinking(tmp_path, monkeypatch):
    df = _df(tmp_path)
    replies = iter(["<think>endless reasoning", "short</think>\nANSWERS {\"1\": 1, \"2\": 2}"])
    be = Scripted([lambda r: next(replies)] * 2)
    monkeypatch.setattr("qp.data.load_split", lambda split: df)
    out = tmp_path / "out"
    RA.main(["--split", "val_hires", "--out", str(out), "--ws-root", str(tmp_path / "ws")], backend=be)
    assert be.reqs[0].thinking and not be.reqs[1].thinking and "cut off" in _text(be.reqs[1])
    assert json.loads((out / "answers" / "clip_a.json").read_text())["answers"] == {"1": 1.0, "2": 2.0}


def test_malformed_cap_and_wall_time_cap(tmp_path, monkeypatch):
    df = _df(tmp_path, videos=("clip_a",))
    be = Scripted(["no action"], final=_answers)
    out = _run(tmp_path, df, be, [], monkeypatch)
    rec = json.loads((out / "answers" / "clip_a.json").read_text())
    assert "without an action" in rec["forced"] and rec["n_steps"] == AL.AgentConfig().max_malformed
    (tmp_path / "b").mkdir()
    df2 = _df(tmp_path / "b", videos=("clip_b",))
    be2 = Scripted(["```python\nprint(1)\n```"], final=_answers)
    out2 = _run(tmp_path / "b", df2, be2, ["--clip-minutes", "0"], monkeypatch)
    rec2 = json.loads((out2 / "answers" / "clip_b.json").read_text())
    assert "time budget" in rec2["forced"] and rec2["n_steps"] == 0 and len(rec2["answers"]) == 2


def test_batching_concurrency_resume_and_generation_failures(tmp_path, monkeypatch):
    df = _df(tmp_path, videos=("v1", "v2", "v3"))
    be = Scripted(["```python\nprint('hi')\n```", _answers])
    out = _run(tmp_path, df, be, ["--concurrency", "2"], monkeypatch)
    assert max(be.calls) == 2 and len(list((out / "answers").glob("*.json"))) == 3
    assert pd.read_csv(out / "agent.csv").parsed_value.notna().all()

    class Boom:
        def generate(self, reqs):
            raise AssertionError("finished clips must not be run again")
    _run(tmp_path, df, Boom(), [], monkeypatch)                        # resume: nothing to do, no model call

    class Fails:
        n = 0

        def generate(self, reqs):
            Fails.n += 1
            return [None] * len(reqs)
    (tmp_path / "f").mkdir()
    df4 = _df(tmp_path / "f", videos=("v4",))
    out4 = _run(tmp_path / "f", df4, Fails(), [], monkeypatch)
    rec = json.loads((out4 / "answers" / "v4.json").read_text())
    # max_failed failed generations, then ONE forced final turn before giving up; the clip is "failed", not "done"
    assert rec["end"] == "generation_failed" and rec["answers"] == {} and Fails.n == AL.AgentConfig().max_failed + 1
    assert rec["status"] == "failed" and "failed to reply" in rec["forced"] and AL.load_answers(out4) == {}
    be = Scripted([_answers])                                          # a re-run retries the failed clip
    _run(tmp_path / "f", df4, be, [], monkeypatch)
    assert len(be.reqs) == 1 and AL.load_answers(out4)["v4"]["end"] == "done"
    old = dict(rec, status="done")                    # a record of the first version: "done" + generation_failed
    (out4 / "answers" / "v4.json").write_text(json.dumps(old))
    assert AL.load_answers(out4) == {} and set(AL.load_answers(out4, ("failed",))) == {"v4"}


def test_segmented_twins_reuse_original_answers(tmp_path, monkeypatch):
    df = _df(tmp_path, videos=("clip_a",), twin=True)
    df.loc[df.video_id.str.endswith("_segmented") & (df.qid == 4), "question"] = "What is the speed of the ball?"
    clips = AL.plan_twins(AL.clips_from_df(df.drop(columns=["answer"])))
    tw = clips[1]
    assert tw.reuse == {3: ("clip_a", 1)} and tw.qids == [4]
    be = Scripted([_answers])
    out = _run(tmp_path, df, be, [], monkeypatch)
    rec = json.loads((out / "answers" / "clip_a_segmented.json").read_text())
    assert rec["answers"] == {"4": 0.5, "3": 0.5} and rec["source"]["3"] == "twin:clip_a:1"
    asked = [_qids(r) for r in be.reqs]
    assert sorted(map(tuple, asked)) == [(1, 2), (4,)]                  # qid 3 never asked


def test_generation_time_is_charged_by_reply_length():
    class C:
        active_s = 0.0
    a, b, c = C(), C(), C()
    AL.charge_generation([a, b, c], ["x" * 100, "x" * 25, None], 8.0)
    assert (a.active_s, b.active_s) == (8.0, 2.0) and c.active_s == pytest.approx(0.08)


def test_context_budget_drops_old_images(tmp_path):
    cfg = AL.AgentConfig(max_images=3, keep_images=2, thinking=False)
    c = AL.Conversation(_clip(tmp_path), tmp_path / "ws" / "c", cfg, [])
    c.start()
    for k in range(4):
        img, cap = AL.render_frame(str(c.ws / "video.mp4"), FPS, 48, t=k * 0.2)
        c._user("FRAME shown above.", [img], [cap])
    req = c.request()
    n_ph = sum(1 for m in req.messages if isinstance(m["content"], list) for x in m["content"] if x["type"] == "image")
    assert len(req.images) == n_ph == 2 and c.dropped_images == 3
    tight = AL.AgentConfig(max_model_len=3000, thinking=False)
    c2 = AL.Conversation(_clip(tmp_path), tmp_path / "ws" / "c2", tight, [])
    c2.start()
    c2._user("x" * 20000)
    c2.request()
    assert c2.final_mode and "context is full" in c2.forced


def test_only_open_models_and_prompt_facts():
    for m in ("claude-opus-4", "gpt-4o", "gemini-2.5-pro"):
        with pytest.raises(SystemExit):
            RA.check_open(m)
    RA.check_open("Qwen/Qwen3.6-27B-FP8")
    p = AL.system_prompt(AL.AgentConfig())
    for fact in ("prior is exactly true", "range vs optical-axis depth Z", "axis-aligned bounding-box",
                 "backward", "change of the speed magnitude", "camera motion", "84 deg", "711 px",
                 "forward differences at 25 fps", "background removed", "ANSWERS", "FRAME", "```python"):
        assert fact in p, fact


def test_notebook_agent_preset():
    import importlib.util
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("_nb_agent", root / "notebooks" / "_build_notebook.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    src = "\n".join(s for k, s in mod.CELLS if k == "code")
    assert 'elif RUN_PRESET == "agent":' in src and '"trackb_agent"' in src
    assert "python -m qp.open.run_agent --split {AGENT_SPLIT[split]}" in src and "{LIM}" in src
    assert 'push_outputs(f"interim-agent-{split}")' in src
    nb = json.loads((root / "notebooks" / "colab_pipeline.ipynb").read_text())
    assert "qp.open.run_agent" in "".join("".join(c["source"]) for c in nb["cells"])
    args = RA.parse_args(["--split", "test", "--out", "x"])
    assert args.model == "Qwen/Qwen3.6-27B-FP8" and args.max_steps == 30 and args.clip_minutes == 8


def test_trackb_agent_routing_rule():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_trackb_agent_common", Path(__file__).resolve().parents[1] / "research" / "trackb_agent" / "common.py")
    RC = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(RC)
    assert RC.decide(0.70, 0.68, 5) == "agent" and RC.decide(0.69, 0.68, 5) == "gm"
    assert RC.decide(0.66, 0.68, 5) == "base" and RC.decide(0.67, 0.68, 5) == "gm" and RC.decide(0.9, 0.5, 0) == "base"
    assert [RC.clip_type(s, v) for s, v in [("simulation", "S3MC"), ("segmentation", "S2MC"), ("internet", "S3MC"),
                                            ("lab", "D3MX"), ("segmentation", "D3MC")]] == \
        ["sim3", "sim2", "internet", "lab", "sim3"]
    idx = [1, 2, 3, 4, 5]
    base = pd.Series([1.0, 1.0, 1.0, 1.0, 1.0], index=idx)
    agent = pd.Series([4.0, 4.0, 4.0, np.nan, 4.0], index=idx)
    types = pd.Series(["sim3", "sim2", "lab", "sim3", "sim3"], index=idx)
    stated = pd.Series([0, 0, 0, 0, 1], index=idx)
    out = RC.routed(base, agent, types, stated, {"sim3": "agent", "sim2": "gm", "lab": "base", "internet": "agent"})
    assert out.tolist() == [4.0, 2.0, 1.0, 1.0, 1.0]


# =========================================================================== hardening (fixes after commit 44cdd90)

import os                                    # noqa: E402
import shutil                                # noqa: E402
import stat                                  # noqa: E402
import tempfile                              # noqa: E402
from types import SimpleNamespace            # noqa: E402

from PIL import Image                        # noqa: E402

from qp.open import ctx_annot as CA          # noqa: E402
from qp.open import qwen_vl as QV            # noqa: E402


def _req_text(req) -> str:
    return "\n".join(m["content"] if isinstance(m["content"], str) else "".join(x.get("text", "") for x in m["content"])
                     for m in req.messages)


def fake_count(req) -> int:
    """Approximate tokenizer for fake backends: digits 1 token each, other text 3 chars per token, images
    ceil(w / 32) * ceil(h / 32)."""
    n = 0
    for m in req.messages:
        c = m["content"]
        t = c if isinstance(c, str) else "".join(x.get("text", "") for x in c)
        d = sum(ch.isdigit() for ch in t)
        n += d + (len(t) - d) // 3 + 4
    return n + sum(math.ceil(im.size[0] / 32) * math.ceil(im.size[1] / 32) for im in req.images)


class ByClip:
    """Scripted replies per clip (video_id from the request tag); records every request and batch size."""

    def __init__(self, scripts: dict, final=None, count=False, fail=None):
        self.scripts, self.final, self.fail = scripts, final, fail
        self.calls, self.reqs = [], []
        if count:
            self.count_tokens = self._count
        self.counted = 0

    def _count(self, req):
        self.counted += 1
        return fake_count(req)

    def generate(self, reqs):
        self.calls.append(len(reqs))
        if self.fail is not None:
            self.fail(reqs)                      # may raise for the whole batch
        out = []
        for r in reqs:
            self.reqs.append(r)
            if "STOP:" in _text(r):
                out.append(self.final(r) if self.final else _answers(r))
                continue
            sc = self.scripts[r.tag["video_id"]]
            n = sum(1 for m in r.messages if m["role"] == "assistant")
            s = sc[min(n, len(sc) - 1)]
            out.append(s(r) if callable(s) else s)
        return out


# --------------------------------------------------------------------------- 1. prefix caching

def test_prefix_caching_defaults_on_and_is_logged(monkeypatch, capsys):
    args = RA.parse_args(["--split", "test", "--out", "x"])
    assert args.prefix_caching == "on"
    assert RA.prefix_caching_kwargs("on", {"mamba_cache_mode", "enable_prefix_caching"}) == (
        {"enable_prefix_caching": True, "mamba_cache_mode": "align"},
        "ON (enable_prefix_caching=True, mamba_cache_mode='align')")
    assert RA.prefix_caching_kwargs("on", set())[0] == {"enable_prefix_caching": True}   # older vLLM: no mamba mode
    assert RA.prefix_caching_kwargs("off", set())[0] == {"enable_prefix_caching": False}
    assert RA.prefix_caching_kwargs("auto", set())[0] == {}
    seen = []

    def make_backend(name, model, **kw):
        seen.append(kw)
        cc = SimpleNamespace(enable_prefix_caching=kw.get("enable_prefix_caching", False),
                             mamba_cache_mode=kw.get("mamba_cache_mode", "none"))
        return SimpleNamespace(llm=SimpleNamespace(llm_engine=SimpleNamespace(vllm_config=SimpleNamespace(
            cache_config=cc))))
    monkeypatch.setattr("qp.open.ctx_annot.make_backend", make_backend)
    monkeypatch.setattr(RA, "_engine_fields", lambda: {"mamba_cache_mode"})
    RA.load_backend(args)
    log = capsys.readouterr().out
    assert seen[-1]["enable_prefix_caching"] is True and seen[-1]["mamba_cache_mode"] == "align"
    assert "prefix caching: ON" in log and "enable_prefix_caching=True, mamba_cache_mode=align" in log
    RA.load_backend(RA.parse_args(["--split", "test", "--out", "x", "--prefix-caching", "off"]))
    assert seen[-1]["enable_prefix_caching"] is False and "prefix caching: OFF" in capsys.readouterr().out
    RA.load_backend(RA.parse_args(["--split", "test", "--out", "x", "--prefix-caching", "auto"]))
    assert "enable_prefix_caching" not in seen[-1] and "prefix caching: AUTO" in capsys.readouterr().out

    tried = []

    def picky(name, model, **kw):                  # an engine that refuses the prefix-caching options
        tried.append(kw)
        if "enable_prefix_caching" in kw:
            raise ValueError("mamba_cache_mode='align' is not supported for this model")
        return make_backend(name, model, **kw)
    monkeypatch.setattr("qp.open.ctx_annot.make_backend", picky)
    be, m = RA.load_backend(args)
    assert m == args.model and len(tried) == 2 and "enable_prefix_caching" not in tried[1]
    assert "engine refused it" in capsys.readouterr().out


# --------------------------------------------------------------------------- 2. exact token counting

def test_image_tokens_and_ctx_vllm_count_tokens():
    assert CA.image_tokens(1280, 720) == 40 * 23 and CA.image_tokens(320, 240) == 10 * 8
    assert CA.image_tokens(50, 50) == 8 * 8                     # upscaled to the processor's 65536 px minimum
    assert CA.image_tokens(1280, 720, max_pixels=409600) == 26 * 15   # downscaled by a max-pixels cap

    class Tok:
        unk_token_id = 0

        def __call__(self, text, add_special_tokens=False):
            return {"input_ids": [7 if w == "<|image_pad|>" else 1 for w in re.findall(r"<\|image_pad\|>|\S+", text)]}

        def convert_tokens_to_ids(self, t):
            return 7

    class Proc:
        tokenizer = Tok()
        image_processor = SimpleNamespace(patch_size=16, merge_size=2,
                                          size={"shortest_edge": 65536, "longest_edge": 16777216})

        def apply_chat_template(self, messages, tokenize, add_generation_prompt, enable_thinking):
            parts = []
            for m in messages:
                c = m["content"]
                parts += [c] if isinstance(c, str) else ["<|image_pad|>" if x["type"] == "image" else x["text"]
                                                         for x in c]
            return " ".join(parts)

    be = object.__new__(CA.CtxVLLM)
    be.processor, be._mm_kw = Proc(), {}
    req = CA.CtxRequest(messages=[{"role": "user", "content": [{"type": "text", "text": "a b c"}, {"type": "image"}]}],
                        images=[Image.new("RGB", (1280, 720))])
    assert be.count_tokens(req) == 3 + 40 * 23                  # the pad token replaced by the image's tokens
    be2 = object.__new__(CA.CtxVLLM)
    be2.processor, be2._mm_kw = Proc(), {"size": {"longest_edge": 409600, "shortest_edge": 65536}}
    assert be2.count_tokens(req) == 3 + 26 * 15                 # --mm-max-pixels is applied to the count


def test_fit_context_counts_with_the_backend_and_drops_old_outputs(tmp_path):
    cfg = AL.AgentConfig(thinking=False, max_model_len=7000, max_tokens_plain=512)
    c = AL.Conversation(_clip(tmp_path), tmp_path / "ws" / "c", cfg, [])
    c.start()
    for k in range(4):
        img, cap = AL.render_frame(str(c.ws / "video.mp4"), FPS, 48, t=k * 0.2)
        c.messages.append({"role": "assistant", "content": f"FRAME {k * 0.2}"})
        c._user(f"out{k} " + "y" * 3000, [img], [cap])
    calls = []

    def count(req):
        calls.append(1)
        return fake_count(req)
    req = c.request(count)
    budget = cfg.max_model_len - cfg.max_tokens_plain - cfg.ctx_margin
    assert calls and fake_count(req) <= budget and req.tag["prompt_tokens"] == fake_count(req)
    assert not c.final_mode and c.dropped_outputs > 0 and c.too_long == 1
    assert "out3 " + "y" * 100 in _text(req)                       # the latest result is kept
    assert "- qid 1" in req.messages[1]["content"][0]["text"]       # the task is kept
    # a context that cannot hold the task: forced final, then the clip ends "too_long" without a request
    tiny = AL.AgentConfig(thinking=False, max_model_len=1500)
    c2 = AL.Conversation(_clip(tmp_path), tmp_path / "ws" / "c2", tiny, [])
    c2.start()
    assert c2.request(fake_count) is None and c2.final_mode and c2.status == "too_long" and c2.state == "done"
    assert c2.record("m")[0]["status"] == "done"                  # a deterministic overflow is not retried


def test_too_long_prompt_is_isolated_shrunk_and_never_resent(tmp_path, monkeypatch):
    df = _df(tmp_path, videos=("v1", "v2"))
    big = "```python\nprint('{}' * 1500)\n```"
    marker = "MARKERMARKER"

    def fail(reqs):                   # the engine counts MARKER text much higher than our tokenizer does
        if any(marker in _req_text(r) for r in reqs):
            raise ValueError("The decoder prompt (length 70001) is longer than the maximum model length of 65536.")
    be = ByClip({"v1": [big.format("a"), big.format("b"), "```python\nprint(('MARK' + 'ERMARKER') * 1500)\n```",
                        _answers],
                 "v2": ["```python\nprint(1)\n```"] * 5 + [_answers]}, count=True, fail=fail)
    out = _run(tmp_path, df, be, ["--concurrency", "2"], monkeypatch)
    r1 = json.loads((out / "answers" / "v1.json").read_text())
    r2 = json.loads((out / "answers" / "v2.json").read_text())
    assert r2["end"] == "done" and len(r2["answers"]) == 2 and r2["too_long"] == 0
    assert r1["status"] == "done" and r1["too_long"] >= 1 and r1["failed_generations"] == 0 and len(r1["answers"]) == 2
    assert "context is full" in r1["forced"] and r1["dropped_outputs"] >= 1
    sent1 = [_req_text(r) for r in be.reqs if r.tag["video_id"] == "v1"]
    assert len(sent1) == len(set(sent1))                            # the rejected prompt is never sent again
    assert be.counted > 0 and 2 in be.calls[3:] and 1 in be.calls  # bisected, then batched again


# --------------------------------------------------------------------------- 3. / 4. batch failures, dead engine

def test_failing_request_is_bisected_out_of_the_batch(tmp_path, monkeypatch):
    df = _df(tmp_path, videos=("v1", "v2", "v3", "v4"))

    def fail(reqs):
        if any(r.tag["video_id"] == "v3" for r in reqs):
            raise RuntimeError("image processor failed")
    be = ByClip({v: [_answers] for v in ("v1", "v2", "v3", "v4")}, fail=fail)
    out = _run(tmp_path, df, be, ["--concurrency", "4"], monkeypatch)
    assert be.calls[:5] == [4, 2, 2, 1, 1]        # whole batch -> halves -> v3 alone; the rest stays batched
    recs = {v: json.loads((out / "answers" / f"{v}.json").read_text()) for v in ("v1", "v2", "v3", "v4")}
    assert all(recs[v]["end"] == "done" for v in ("v1", "v2", "v4"))
    assert recs["v3"]["status"] == "failed" and recs["v3"]["end"] == "generation_failed"
    assert set(AL.load_answers(out)) == {"v1", "v2", "v4"}


class EngineDeadError(Exception):
    pass


def test_dead_engine_stops_the_run_keeps_finished_clips_and_rerun_retries(tmp_path, monkeypatch):
    df = _df(tmp_path, videos=("v1", "v2", "v3", "v4"))
    n = [0]

    def fail(reqs):
        n[0] += 1
        if n[0] >= 2:
            raise EngineDeadError("EngineCore encountered an issue. See stack trace (above) for the root cause.")
    be = ByClip({"v1": [_answers], "v2": ["```python\nprint(1)\n```", _answers],
                 "v3": [_answers], "v4": [_answers]}, fail=fail)
    monkeypatch.setattr("qp.data.load_split", lambda split: df)
    out = tmp_path / "out"
    argv = ["--split", "val_hires", "--out", str(out), "--ws-root", str(tmp_path / "ws"), "--no-thinking",
            "--tool-workers", "2", "--concurrency", "2"]
    assert RA.main(argv, backend=be) == 3                           # non-zero exit
    assert be.calls == [2, 2]                                       # no bisection of a dead engine, no new clips
    assert set(AL.load_answers(out)) == {"v1"}
    assert AL.load_answers(out, ("failed",)).keys() == {"v2", "v3"} and not (out / "answers" / "v4.json").exists()
    summ = json.loads((out / "summary_agent.json").read_text())
    assert "EngineDeadError" in summ["aborted"] and summ["failed"] == ["v2", "v3"]
    good = Scripted([_answers])
    assert RA.main(argv, backend=good) == 0 and set(AL.load_answers(out)) == {"v1", "v2", "v3", "v4"}
    assert sorted(_qids(r)[0] for r in good.reqs) == [3, 5, 7]     # only the unfinished clips ran again

    class AllNone:
        calls = 0

        def generate(self, reqs):
            AllNone.calls += 1
            return [None] * len(reqs)
    (tmp_path / "n").mkdir()
    df2 = _df(tmp_path / "n", videos=("w1", "w2"))
    monkeypatch.setattr("qp.data.load_split", lambda split: df2)
    out2 = tmp_path / "n" / "out"
    argv2 = ["--split", "val_hires", "--out", str(out2), "--ws-root", str(tmp_path / "n" / "ws"), "--no-thinking"]
    assert RA.main(argv2, backend=AllNone()) == 3 and AllNone.calls == 3
    assert AL.load_answers(out2) == {} and set(AL.load_answers(out2, ("failed",))) == {"w1", "w2"}


# --------------------------------------------------------------------------- 5. robustness

def test_parsers_never_raise():
    assert QV._loads("[" * 100000) is None and QV._loads("1" * 5000) is None and QV._loads(None) is None
    assert AL._value(10 ** 400) is None and AL._value("1e999") is None and AL._value(float("nan")) is None
    deep: dict = {"value": 1.0}
    for _ in range(50):
        deep = {"value": deep}
    assert AL._value(deep) is None
    assert AL._json_after("{" + "[" * 50000, 0)[0] is None
    q = [12]
    assert AL.parse_answers('ANSWERS {"' + "9" * 5000 + '": 1, "12": 2}', q) == {12: 2.0}
    assert AL.parse_answers('ANSWERS {"12": ' + "9" * 5000 + "}", q) == {}
    assert AL.parse_answers("qid " + "1" * 5000 + ": 3", q, anywhere=True) == {}
    assert AL.parse_answers("ANSWERS {" * 3000, q, anywhere=True) == {}
    for t in ("FRAME 1e999", "FRAME #99999999999999", "FRAME t=nan 1 2 3 4", "FRAME 1 2 3 4 5 scale=1e400"):
        a = AL.parse_action(t, q)
        assert a.kind == "frame" and a.payload is None and a.error


def test_one_conversation_error_never_crashes_the_run(tmp_path, monkeypatch):
    df = _df(tmp_path, videos=("v1", "v2", "v3"))
    orig_reply, orig_obs, orig_req = AL.Conversation.on_reply, AL.Conversation.on_observation, AL.Conversation.request
    hit = {"reply": 0}

    def on_reply(self, text):
        if self.clip.video_id == "v1" and hit["reply"] == 0:
            hit["reply"] += 1
            raise KeyError("boom in on_reply")
        return orig_reply(self, text)

    def on_observation(self, obs):
        if self.clip.video_id == "v2":
            raise RuntimeError("boom in on_observation")
        return orig_obs(self, obs)

    def request(self, count=None):
        if self.clip.video_id == "v3":
            raise ValueError("boom in request")
        return orig_req(self, count)
    monkeypatch.setattr(AL.Conversation, "on_reply", on_reply)
    monkeypatch.setattr(AL.Conversation, "on_observation", on_observation)
    monkeypatch.setattr(AL.Conversation, "request", request)
    be = ByClip({"v1": [_answers], "v2": ["```python\nprint(1)\n```", _answers], "v3": [_answers]})
    out = _run(tmp_path, df, be, ["--concurrency", "3"], monkeypatch)
    recs = {v: json.loads((out / "answers" / f"{v}.json").read_text()) for v in ("v1", "v2", "v3")}
    assert recs["v1"]["end"] == "done" and recs["v1"]["errors"] == 1 and len(recs["v1"]["answers"]) == 2
    assert recs["v2"]["status"] == "failed" and recs["v2"]["end"] == "error"
    assert recs["v3"]["status"] == "failed" and recs["v3"]["end"] == "error"


# --------------------------------------------------------------------------- 6. parsing

def test_answers_keyword_strict_at_line_start():
    q = [12, 13]
    for t in ('The answers {"12": 1, "13": 2}', 'So my ANSWERS {"12": 1, "13": 2}', 'answers {"12": 1, "13": 2}',
              "ANSWERS will follow once I have checked the frame.", 'Answers: {"12": 1, "13": 2}'):
        assert AL.parse_action(t, q).kind == "none", t
    for t in ('**ANSWERS** {"12": 1, "13": 2}', '> ANSWERS {"12": 1, "13": 2}', '### ANSWERS:\n{"12": 1, "13": 2}',
              'ANSWERS\n```\n{"12": 1, "13": 2}\n```', 'Done.\n- ANSWERS = {"12": 1, "13": 2}',
              '`ANSWERS {"12": 1, "13": 2}`', 'ANSWERS ```json\n{"12": 1, "13": 2}\n```'):
        a = AL.parse_action(t, q)
        assert a.kind == "answers" and a.payload == {12: 1.0, 13: 2.0}, t
    assert AL.parse_answers('Final answers: {"12": 1}', q) == {}
    assert AL.parse_answers('Final answers: {"12": 1}', q, anywhere=True) == {12: 1.0}   # forced final turn only


def test_fences_pair_in_order_and_only_python_is_code():
    q = [12]
    t = 'Data:\n```json\n{"a": 1}\n```\nNow I measure the ball.\n```python\nprint(1)\n```'
    a = AL.parse_action(t, q)
    assert (a.kind, a.payload, a.n_actions) == ("python", "print(1)", 1)    # the json closer opens nothing
    t = "```text\nnotes\n```\nprose between\n```bash\nls\n```"
    assert AL.parse_action(t, q).kind == "none"
    assert AL.parse_action("```\nprint(2)\n```", q).payload == "print(2)"
    assert AL.parse_action("```py\nprint(3)\n```", q).payload == "print(3)"
    assert AL.parse_action("```Python3\nprint(4)\n```", q).payload == "print(4)"
    assert AL.parse_action("```python\nprint(5)", q).payload == "print(5)"       # a cut reply
    assert AL.parse_action("```\nFRAME 1.0\n```", q).kind == "frame"
    a = AL.parse_action("```output\nold\n```\nFRAME 2.0 10 10 50 50", q)
    assert a.kind == "frame" and a.payload["box"] == [10, 10, 50, 50]


def test_frame_label_prefixes_and_ranges():
    p = AL.parse_frame_args
    assert p("t=1.0 x0=100 y0=80 x1=180 y1=160 scale=2") == {"grid": True, "t": 1.0, "box": [100, 80, 180, 160],
                                                             "scale": 2.0}
    assert p("x0=100 x1=180 y0=80 y1=160 t=1")["box"] == [100, 80, 180, 160]
    got = p("1.0 x 100..180, y 80..160 3")                     # the format of the FRAME caption itself
    assert got["t"] == 1.0 and got["box"] == [100, 80, 180, 160] and got["scale"] == 3
    assert p("t=1 x=100..180 y=80..160")["box"] == [100, 80, 180, 160]
    assert p("1.0 100-180 80-160")["box"] == [100, 80, 180, 160]
    got = p("t: 2.5 box: (10, 20, 30, 40)")
    assert got["t"] == 2.5 and got["box"] == [10, 20, 30, 40] and got["scale"] == 1.0
    got = p("#24 x=100 y=80 w=80 h=80 nogrid")
    assert got["idx"] == 24 and got["box"] == [100, 80, 180, 160] and not got["grid"]
    assert p("t=0.5s") == {"grid": True, "t": 0.5, "scale": 1.0}
    with pytest.raises(ValueError):
        p("t=inf")


# --------------------------------------------------------------------------- 7. scheduler throughput

def test_cohort_waits_for_tools_before_generate(tmp_path, monkeypatch):
    df = _df(tmp_path, videos=("v1", "v2", "v3"))
    scripts = {"v1": ["```python\nimport time\ntime.sleep(2)\nprint('slow')\n```", _answers],
               "v2": ["FRAME 1.0", _answers],
               "v3": ["let me think first", _answers]}            # no action: ready again at once
    be = ByClip(scripts)
    _run(tmp_path, df, be, ["--concurrency", "3"], monkeypatch)
    assert be.calls == [3, 3]                       # v3 (ready) waited for the running tools: one cohort
    (tmp_path / "b").mkdir()
    df2 = _df(tmp_path / "b", videos=("v1", "v2", "v3"))
    be2 = ByClip(scripts)
    _run(tmp_path / "b", df2, be2, ["--concurrency", "3", "--tool-wait-s", "0"], monkeypatch)
    assert be2.calls[0] == 3 and be2.calls[1] < 3   # no wait (the old behaviour): the cohort splits


def test_thinking_tokens_and_elapsed_cap_scale_with_concurrency(tmp_path):
    args = RA.parse_args(["--split", "test", "--out", "x"])
    assert args.max_tokens_think == 4096 and AL.AgentConfig().max_tokens_think == 4096
    assert args.elapsed_factor == 4.0 and args.tool_wait_s == 15.0
    cfg = AL.AgentConfig()
    assert AL.elapsed_cap_s(cfg, 32) == 4 * 480 * 4 and AL.elapsed_cap_s(cfg, 4) == 4 * 480
    assert AL.elapsed_cap_s(AL.AgentConfig(max_elapsed_factor=0), 32) is None
    for conc, forced in ((32, False), (1, True)):
        c = AL.Conversation(_clip(tmp_path), tmp_path / "ws" / f"c{conc}", cfg, [])
        c.start()
        c.t0 = time.time() - 2 * 4 * 480                            # 64 min real time, no own time used
        c.elapsed_cap_s = AL.elapsed_cap_s(cfg, conc)
        c.request()
        assert c.final_mode is forced and (not forced or "time budget" in c.forced)


# --------------------------------------------------------------------------- 8. twins

def test_twin_reuse_needs_same_prior_depth_and_unit(tmp_path, monkeypatch):
    df = _df(tmp_path, videos=("clip_a",), twin=True)                      # qids 1, 2 original; 3, 4 twin
    seg = df.video_id.str.endswith("_segmented")
    df.loc[seg & (df.qid == 4), "prior"] = "diameter of the red ball =   0.5 m"        # whitespace only: same
    clips = AL.plan_twins(AL.clips_from_df(df.drop(columns=["answer"])))
    assert clips[1].reuse == {3: ("clip_a", 1), 4: ("clip_a", 2)} and clips[1].questions == []
    for col, val in (("prior", "diameter of the red ball = 0.6m"), ("depth_info", "ball: 3.0 m"),
                     ("target_unit", "cm")):
        d = df.copy()
        d.loc[seg & (d.qid == 4), col] = val
        clips = AL.plan_twins(AL.clips_from_df(d.drop(columns=["answer"])))
        assert clips[1].reuse == {3: ("clip_a", 1)} and clips[1].qids == [4], col
    d = df.copy()
    d.loc[seg & (d.qid == 4), "prior"] = "diameter of the red ball = 0.6m"
    be = Scripted([_answers])
    out = _run(tmp_path, d, be, [], monkeypatch)
    rec = json.loads((out / "answers" / "clip_a_segmented.json").read_text())
    assert rec["source"] == {"4": "agent", "3": "twin:clip_a:1"} and rec["answers"]["3"] == 0.5
    assert sorted(map(tuple, (_qids(r) for r in be.reqs))) == [(1, 2), (4,)]


# --------------------------------------------------------------------------- 9. sandbox

def test_sandbox_policy_decisions_and_argv():
    P = AL.sandbox_policy
    p = P(0, "auto", True, "/usr/bin/unshare")
    assert (p.uid, p.gid, p.netns) == (65534, 65534, "os")
    p = P(0, "auto", False, "/usr/bin/unshare")
    assert p.netns == "cmd" and AL.sandbox_argv(p, "py", "pass")[:3] == ["/usr/bin/unshare", "--net", "--"]
    p = P(0, "auto", False, None)
    assert p.uid == 65534 and p.netns == "" and "Python guard only" in p.notes[0]
    for p in (P(1000, "auto", True, "/usr/bin/unshare"), P(0, "off", True, "/usr/bin/unshare")):
        assert p.uid is None and p.netns == "" and p.notes
    boot = AL.sandbox_argv(P(0, "auto", True, None), "/usr/bin/python3", "print(1)")
    assert boot[:3] == ["/usr/bin/python3", "-s", "-c"]
    b = boot[3]
    assert b.index("os.nice(10)") < b.index("os.unshare(os.CLONE_NEWNET)") < b.index("os.setgroups([])") \
        < b.index("os.setgid(65534)") < b.index("os.setuid(65534)") < b.index("print(1)")
    assert "setuid" not in AL.sandbox_argv(P(1000), "py", "x")[3] and "unshare" not in AL.sandbox_argv(P(1000), "py",
                                                                                                      "x")[3]
    assert AL.sandbox_mem_mb(8, 150000) == 13750 and AL.sandbox_mem_mb(2, 200000) == 16384
    assert AL.sandbox_mem_mb(4, 30000) == 2048 and AL.sandbox_mem_mb(4, 41000) == 2048
    env = AL.sandbox_env(Path("/w"), [], 2048)
    for k, v in (("PIP_NO_INDEX", "1"), ("PIP_DISABLE_PIP_VERSION_CHECK", "1"), ("OPENCV_FOR_THREADS_NUM", "2"),
                 ("OPENCV_FFMPEG_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("PYTHONNOUSERSITE", "1")):
        assert env[k] == v


def test_unreachable_and_lock_deny_roots(tmp_path):
    d = tmp_path / "a" / "b"
    d.mkdir(parents=True)
    assert AL._unreachable(d, os.getuid(), os.getgid()) is None
    os.chmod(tmp_path / "a", 0o600)
    try:
        assert AL._unreachable(d, os.getuid(), os.getgid()) == str(tmp_path / "a")
    finally:
        os.chmod(tmp_path / "a", 0o700)
    repo, drive = tmp_path / "repo", tmp_path / "drive"
    (repo / "ws").mkdir(parents=True)
    drive.mkdir()
    os.chmod(repo, 0o755)
    os.chmod(drive, 0o755)
    locked = AL.lock_deny_roots([str(repo), str(drive), str(tmp_path / "missing")], [str(repo / "ws")])
    assert [p for p, _ in locked] == [os.path.realpath(drive)]           # repo holds the workspaces: left open
    assert stat.S_IMODE(os.stat(drive).st_mode) == 0o750 and stat.S_IMODE(os.stat(repo).st_mode) == 0o755
    AL.unlock_deny_roots(locked)
    assert stat.S_IMODE(os.stat(drive).st_mode) == 0o755


def test_workspace_copy_env_nice_threads_and_killpg(tmp_path):
    clip = _clip(tmp_path)
    ws = tmp_path / "ws" / "clip_a"
    AL.prepare_workspace(clip, ws)
    st, src = os.stat(ws / "video.mp4"), os.stat(clip.video_path)
    assert st.st_nlink == 1 and st.st_ino != src.st_ino and not (ws / "_qp_guard.py").exists()
    code = ("import os, subprocess, cv2\n"
            "e = os.environ\n"
            "print('ENV', e['PIP_NO_INDEX'], e['PIP_DISABLE_PIP_VERSION_CHECK'], e['OPENCV_FOR_THREADS_NUM'], "
            "e['OPENCV_FFMPEG_THREADS'], e['OMP_NUM_THREADS'])\n"
            "print('NICE', os.nice(0))\nprint('CVT', cv2.getNumThreads())\n"
            "p = subprocess.Popen(['sleep', '60'])\nopen('child.pid', 'w').write(str(p.pid))\n")
    base_nice = os.nice(0)
    txt, _, _ = AL.run_python(code, ws, 1, timeout=30)
    assert "ENV 1 1 2 2 2" in txt and "CVT 2" in txt, txt
    assert int(re.search(r"NICE (\d+)", txt).group(1)) == min(19, base_nice + 10)
    pid = int((ws / "child.pid").read_text())
    for _ in range(50):
        try:
            alive = "State:\tZ" not in Path(f"/proc/{pid}/status").read_text()
        except OSError:
            alive = False
        if not alive:
            break
        time.sleep(0.1)
    assert not alive                                       # the background child was killed with the session


def test_harness_never_follows_links_planted_in_the_workspace(tmp_path):
    clip = _clip(tmp_path)
    ws = tmp_path / "ws" / "clip_a"
    AL.prepare_workspace(clip, ws)
    secret = tmp_path / "labels.json"
    secret.write_text(json.dumps({"1": 0.123, "2": 0.456}))
    victim = tmp_path / "victim.txt"
    victim.write_text("keep")
    code = ("import os, cv2, numpy as np\nos.makedirs('_show', exist_ok=True)\n"
            "cv2.imwrite('_show/00.png', np.zeros((8, 8), np.uint8))\n"
            f"os.symlink({str(secret)!r}, '_show/00.txt')\nos.symlink({str(secret)!r}, 'answers.json')\n"
            f"os.symlink({str(victim)!r}, '_step02.py')\n")
    txt, imgs, caps = AL.run_python(code, ws, 1, timeout=30)
    assert len(imgs) == 1 and "0.123" not in caps[0] and "no label" in caps[0], (txt, caps)
    c = AL.Conversation(clip, ws, AL.AgentConfig(), [])
    assert c._answers_file() == {}                         # a link to a label file is not an answer
    AL.run_python("print(2)", ws, 2, timeout=30)
    assert victim.read_text() == "keep"                    # the planted _step02.py link was replaced, not followed
    os.unlink(ws / "answers.json")
    os.link(secret, ws / "answers.json")
    assert c._answers_file() == {}                         # hard links are refused too
    os.unlink(ws / "answers.json")
    os.mkfifo(ws / "answers.json")
    assert c._answers_file() == {}                         # a FIFO neither blocks nor counts
    os.unlink(ws / "answers.json")
    (ws / "answers.json").write_text(json.dumps({"1": 2.5}))
    assert c._answers_file() == {1: 2.5}


@pytest.mark.skipif(not hasattr(os, "geteuid") or os.geteuid() != 0, reason="needs root (Colab runs as root)")
def test_root_sandbox_runs_unprivileged_without_network(tmp_path):
    base = Path(tempfile.mkdtemp(prefix="qp_sbx_", dir="/tmp"))
    try:
        os.chmod(base, 0o755)
        ws_root = base / "ws"
        ws_root.mkdir()
        pol = AL.resolve_sandbox(ws_root)
        if pol.uid is None:
            pytest.skip(f"no unprivileged sandbox possible here: {pol.notes}")
        clip = _clip(tmp_path)
        ws = ws_root / "clip_a"
        AL.prepare_workspace(clip, ws, owner=pol.uid)
        assert os.stat(ws).st_uid == 65534 and os.stat(ws / "inputs.json").st_uid == 65534
        secret = base / "secret.txt"
        secret.write_text("TOPSECRET")
        os.chmod(secret, 0o600)
        code = ("import os, socket, _io\nprint('UID', os.getuid(), os.getgid(), os.getgroups())\n"
                f"try:\n    _io.FileIO({str(secret)!r}).read(); print('READ')\nexcept PermissionError:\n"
                "    print('denied')\n"
                "print('IF', sorted(n for _, n in socket.if_nameindex()))\nopen('w.txt', 'w').write('x')\n"
                "print('WROTE')\nfrom qptools import *\nprint('N', N)\n")
        txt, _, _ = AL.run_python(code, ws, 1, timeout=60, policy=pol)
        assert "UID 65534 65534 []" in txt and "denied" in txt and "READ" not in txt and "WROTE" in txt, txt
        assert "N 48" in txt and (not pol.netns or "IF ['lo']" in txt)
        repo = base / "repo"
        (repo / "data").mkdir(parents=True)
        (repo / "data" / "labels.csv").write_text("qid,answer\n1,2\n")
        os.chmod(repo, 0o755)
        locked = AL.lock_deny_roots([str(repo)], AL._sandbox_keep(ws_root))
        try:
            code = (f"import _io\ntry:\n    _io.FileIO({str(repo / 'data' / 'labels.csv')!r}).read(); print('LEAK')\n"
                    "except PermissionError:\n    print('closed')\n")
            txt, _, _ = AL.run_python(code, ws, 2, timeout=60, policy=pol)   # past the guard: the OS refuses
            assert "closed" in txt and "LEAK" not in txt, txt
        finally:
            AL.unlock_deny_roots(locked)
        assert stat.S_IMODE(os.stat(repo).st_mode) == 0o755
    finally:
        shutil.rmtree(base, ignore_errors=True)


@pytest.mark.skipif(not hasattr(os, "geteuid") or os.geteuid() != 0, reason="needs root (Colab runs as root)")
def test_root_run_clips_end_to_end_unprivileged(tmp_path):
    base = Path(tempfile.mkdtemp(prefix="qp_sbx_", dir="/tmp"))
    try:
        os.chmod(base, 0o755)
        repo = base / "repo"
        (repo / "data").mkdir(parents=True)
        labels = repo / "data" / "labels.csv"
        labels.write_text("qid,answer\n1,2\n")
        os.chmod(repo, 0o755)
        clips = AL.clips_from_df(_df(tmp_path).drop(columns=["answer"]))
        code = ("```python\nimport os, _io\nprint('UID', os.getuid())\n"
                f"try:\n    _io.FileIO({str(labels)!r}).read(); print('LEAK')\nexcept PermissionError:\n"
                "    print('closed')\n```")
        be = Scripted([code, _answers])
        cfg = AL.AgentConfig(thinking=False)
        stats = AL.run_clips(be, clips, base / "out", cfg, base / "ws", tool_workers=1, deny=[str(repo)])
        if AL.resolve_sandbox(base / "ws").uid is None:
            pytest.skip("no unprivileged sandbox possible here")
        assert stats["finished"] == 1 and stats["failed"] == 0
        obs = _text(be.reqs[1])
        assert "UID 65534" in obs and "closed" in obs and "LEAK" not in obs, obs
        assert stat.S_IMODE(os.stat(repo).st_mode) == 0o755              # restored after the run
        assert AL.audit_transcripts(base / "out") == {}
    finally:
        shutil.rmtree(base, ignore_errors=True)


# --------------------------------------------------------------------------- 9b. sandbox (verifier fixes)

def test_workspace_modules_cannot_shadow_the_boot_or_the_guard(tmp_path):
    """A types.py / runpy.py / socket.py / resource.py ... in the workspace must neither run before the script nor
    break later runs; the guard keeps working and the script still imports qptools and its own helper modules."""
    ws = tmp_path / "ws" / "clip_a"
    AL.prepare_workspace(_clip(tmp_path), ws)
    log = tmp_path / "planted.log"
    for m in ("types", "runpy", "pkgutil", "warnings", "socket", "resource", "cv2", "sitecustomize", "_qp_guard"):
        (ws / f"{m}.py").write_text(f"open({str(log)!r}, 'a').write('{m} ran\\n')\nModuleType = None\n")
    (ws / "helper.py").write_text("VALUE = 41\n")
    secret = tmp_path / "labels.csv"
    secret.write_text("qid,answer\n1,1.0\n")
    code = ("from qptools import *\nimport helper\nprint('OK', N, helper.VALUE + 1)\n"
            f"try:\n    open({str(secret)!r}).read(); print('READ')\nexcept PermissionError:\n    print('denied')\n"
            "import socket\ntry:\n    socket.create_connection(('example.com', 80), timeout=2); print('NET')\n"
            "except PermissionError:\n    print('nonet')\n")
    txt, _, _ = AL.run_python(code, ws, 1, timeout=60, deny=[str(tmp_path)])
    assert "OK 48 42" in txt and "denied" in txt and "nonet" in txt and "READ" not in txt, txt
    assert not log.exists(), log.read_text()                       # no planted module was imported
    assert "_qp_path0" in AL.sandbox_argv(AL.SandboxPolicy(), "py", "x")[3]


def _fake_proc(root: Path, pid, uid, start, env=b"", state="S"):
    d = root / str(pid)
    d.mkdir()
    (d / "status").write_text(f"Name:\tx\nUmask:\t0022\nUid:\t{uid}\t{uid}\t{uid}\t{uid}\nGid:\t{uid}\t{uid}\n")
    (d / "stat").write_text(f"{pid} (odd ) name) " + " ".join([state] + ["0"] * 18 + [str(start)] + ["0"] * 5))
    (d / "environ").write_bytes(env)


def test_sandbox_leftover_processes_are_found_and_killed(tmp_path, monkeypatch):
    proc = tmp_path / "proc"
    proc.mkdir()
    (proc / "uptime").write_text("12.50 40.00\n")
    assert AL.clock_ticks_now(str(proc)) == int(12.5 * os.sysconf("SC_CLK_TCK"))
    _fake_proc(proc, 101, 65534, 500)                                     # started during the run (env cleared)
    _fake_proc(proc, 102, 65534, 100, b"PATH=/bin\0QP_DENY=/repo\0")     # an older one with the sandbox env
    _fake_proc(proc, 103, 65534, 100, b"PATH=/bin\0")                     # a system daemon running as nobody
    _fake_proc(proc, 104, 1000, 500)                                      # another user
    _fake_proc(proc, 105, 65534, 500, state="Z")                          # a zombie
    (proc / "106").mkdir()                                                # unreadable entry
    (proc / "self").mkdir()
    assert AL.sandbox_pids(65534, 400, str(proc)) == [101, 102]
    assert AL.sandbox_pids(65534, None, str(proc)) == [102]
    sent = []
    monkeypatch.setattr(os, "kill", lambda pid, sig: sent.append((pid, sig)))
    assert AL.kill_sandbox_processes(65534, 400, str(proc), log=lambda s: None) == 2
    assert sorted(sent) == [(101, 9), (102, 9)]                           # once each, though they stay listed

    # run_clips (sandbox user set): leftovers are killed after the tools finished, BEFORE the deny roots reopen
    order = []
    monkeypatch.setattr(AL, "resolve_sandbox", lambda *a, **k: AL.SandboxPolicy(uid=54321, gid=54321))
    monkeypatch.setattr(AL, "_chown_tree", lambda *a: None)
    monkeypatch.setattr(AL, "kill_sandbox_processes", lambda uid, since, *a, **k: order.append(("kill", uid, since)))
    monkeypatch.setattr(AL, "unlock_deny_roots", lambda locked, *a, **k: order.append(("unlock",)))
    clips = AL.clips_from_df(_df(tmp_path).drop(columns=["answer"]))
    AL.run_clips(Scripted([_answers]), clips, tmp_path / "out", AL.AgentConfig(thinking=False, lock_deny=False),
                 tmp_path / "ws", tool_workers=1)
    assert [o[0] for o in order] == ["kill", "unlock"] and order[0][1] == 54321 and order[0][2] is not None


def test_prelude_caps_the_sandbox_users_processes():
    b = AL.sandbox_argv(AL.sandbox_policy(0, "auto", True, None), "py", "print(1)")[3]
    assert b.index("os.setuid(65534)") < b.index("RLIMIT_NPROC") < b.index("print(1)")
    assert "RLIMIT_NPROC" not in AL.sandbox_argv(AL.SandboxPolicy(), "py", "x")[3]     # no uid change: no cap
    assert "RLIMIT_NPROC" not in AL.sandbox_argv(AL.SandboxPolicy(uid=65534, nproc=0), "py", "x")[3]


def test_deny_roots_cover_the_notebook_scratch_clones():
    d = RA.deny_roots()
    for p in (str(RA.ROOT), "/content/drive", "/content/data_sync", "/content/outputs_push"):
        assert p in d, p
    hits = AL.audit_transcript({"turns": [{"role": "assistant", "text": "import os\nos.setsid()\n"
                                                                        "open('/content/data_sync/x.csv')"}]})
    assert {"setsid", "/content/data_sync"} <= {h["pattern"] for h in hits}


def test_count_tokens_reads_a_size_object_and_answers_scan_is_bounded():
    be = object.__new__(CA.CtxVLLM)
    be.processor = SimpleNamespace(image_processor=SimpleNamespace(
        patch_size=16, merge_size=2, size=SimpleNamespace(shortest_edge=65536, longest_edge=409600)))
    be._mm_kw = {}
    assert be._image_params() == (32, 65536, 409600)             # transformers SizeDict-style attributes
    be2 = object.__new__(CA.CtxVLLM)
    be2.processor = SimpleNamespace(image_processor=SimpleNamespace(patch_size=16, merge_size=2, size=None))
    be2._mm_kw = {"size": SimpleNamespace(longest_edge=1000000, shortest_edge=None)}
    assert be2._image_params() == (32, CA.IMAGE_MIN_PIXELS, 1000000)
    t0 = time.time()
    assert AL.parse_action("\nANSWERS {" * 1600, [12]).kind == "answers"
    assert AL.parse_answers('ANSWERS {"12": 2}\n' + "\nANSWERS {" * 1600, [12], anywhere=True) == {12: 2.0}
    assert time.time() - t0 < 2.0


@pytest.mark.skipif(not hasattr(os, "geteuid") or os.geteuid() != 0, reason="needs root (Colab runs as root)")
def test_root_setsid_escapee_does_not_outlive_run_clips(tmp_path):
    base = Path(tempfile.mkdtemp(prefix="qp_sbx_", dir="/tmp"))
    try:
        os.chmod(base, 0o755)
        (base / "ws").mkdir()
        if AL.resolve_sandbox(base / "ws").uid is None:
            pytest.skip("no unprivileged sandbox possible here")
        pidfile = base / "escapee.pid"
        code = ("```python\nimport os, time, resource\nprint('NPROC', resource.getrlimit(resource.RLIMIT_NPROC)[0])\n"
                "if os.fork() == 0:\n    os.setsid()\n    if os.fork() == 0:\n"
                f"        open({str(pidfile)!r}, 'w').write(str(os.getpid()))\n"
                "        os.execve('/bin/sleep', ['sleep', '300'], {})\n    os._exit(0)\ntime.sleep(0.5)\n```")
        os.chmod(base, 0o777)                                      # the sandbox user writes the pid file here
        be = Scripted([code, _answers])
        clips = AL.clips_from_df(_df(tmp_path).drop(columns=["answer"]))
        stats = AL.run_clips(be, clips, base / "out", AL.AgentConfig(thinking=False), base / "ws", tool_workers=1)
        assert stats["finished"] == 1 and "NPROC 2048" in _text(be.reqs[1])
        pid = int(pidfile.read_text())
        st = Path(f"/proc/{pid}/stat").read_text() if Path(f"/proc/{pid}").exists() else "gone"
        assert st == "gone" or st[st.rindex(")") + 2] in "ZX", st   # killed when run_clips ended
    finally:
        shutil.rmtree(base, ignore_errors=True)


# --------------------------------------------------------------------------- 10. transcript audit

def test_audit_transcript_flags_suspicious_accesses(tmp_path, monkeypatch):
    tr = {"turns": [{"role": "user", "text": "Video clip_a: 320x240 px"},
                    {"role": "assistant", "text": "```python\nimport subprocess\nopen('../../research/x.csv')\n```",
                     "thinking_tail": "maybe /content/drive/MyDrive has the ground_truth"},
                    {"role": "user", "text": "Python result: exit code 0"}]}
    p = tmp_path / "t.json"
    p.write_text(json.dumps(tr))
    hits = AL.audit_transcript(p)
    assert {"subprocess", "../", "research/", "/content/drive", "ground_truth"} <= {h["pattern"] for h in hits}
    assert {h["turn"] for h in hits} == {1} and {h["field"] for h in hits} == {"text", "thinking_tail"}
    clean = {"turns": [{"role": "assistant", "text": "```python\nfrom qptools import *\n```"}]}
    assert AL.audit_transcript(clean) == []
    assert AL.audit_transcript(tmp_path / "missing.json")[0]["pattern"] == "<unreadable transcript>"
    df = _df(tmp_path)
    out = _run(tmp_path, df, Scripted(["```python\nfrom qptools import *\nprint(W)\n```", _answers]), [], monkeypatch)
    assert AL.audit_transcripts(out) == {}                 # a normal run is clean


def test_qptools_measurement_helpers_on_a_synthetic_video(tmp_path):
    """the sandbox helper module's measurement functions recover a known motion (square moving 6 px/frame)"""
    import subprocess
    import sys
    import cv2
    import numpy as np
    from qp.open import agent_loop as al
    vid = tmp_path / "src.mp4"
    w, h, fps, n = 320, 240, 25, 30
    vw = cv2.VideoWriter(str(vid), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    for i in range(n):
        im = np.zeros((h, w, 3), np.uint8)
        x = 40 + 6 * i
        im[100:120, x:x + 20] = 255
        vw.write(im)
    vw.release()
    clip = al.Clip("synthetic_0001", str(vid), [dict(qid=1, question="What is the speed of the square in m/s?",
                   prior="", depth_info="", fps=fps, video_type="D2SS", target_unit="m/s", video_source="internet")])
    ws = tmp_path / "ws"
    al.prepare_workspace(clip, ws)
    (ws / "t.py").write_text(
        "from qptools import *\n"
        "bg = background(15)\n"
        "b = blobs(motion_mask(10, bg))[0]\n"
        "tr = track_motion(5, 25, (b['cx'], b['cy']), bg)\n"
        "v = speeds([(p['cx'], p['cy']) for p in tr if p], kind='backward')\n"
        "tt = track_template(10, 14, (b['x0'], b['y0'], b['x1'], b['y1']))\n"
        "fx, fy = fit_line_track(tr, 1)\n"
        "print(round(float(np.nanmedian(v)), 1), round(tt[-1]['cx'] - tt[0]['cx'], 1), round(float(fx.deriv()(0.5)), 1),\n"
        "      round(dist3d(backproject(W / 2, H / 2, 2.0, focal_from_hfov(90)), (0, 0, 0)), 3))\n")
    out = subprocess.run([sys.executable, "t.py"], cwd=ws, capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr
    med, dx, vx, rng = map(float, out.stdout.split())
    assert abs(med - 150.0) < 8 and abs(dx - 18.0) < 2 and abs(vx - 150.0) < 8 and abs(rng - 2.0) < 1e-6
