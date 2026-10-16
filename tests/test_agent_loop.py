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
    assert rec["end"] == "generation_failed" and rec["answers"] == {} and Fails.n == AL.AgentConfig().max_failed


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
