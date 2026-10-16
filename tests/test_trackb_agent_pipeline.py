"""CPU tests of the Track B agent's routing pipeline (research/trackb_agent: make_base, evaluate, build_sub, common)
and of the notebook's agent stage (section 13e): validation base at full resolution, rows without a base value, twin
routing by the original clip's type, the transcript audit (flagged clips keep the base), the validation gate before
test and the explicit --prefix-caching flag. End to end with a scripted fake model through qp.open.run_agent."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
TBA = ROOT / "research" / "trackb_agent"
FPS = 24.0


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"_tba_{name}", TBA / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def EV():
    return _load("evaluate")


@pytest.fixture(scope="module")
def BS():
    return _load("build_sub")


@pytest.fixture(scope="module")
def C(EV):
    assert Path(EV.C.__file__).resolve() == TBA / "common.py"
    return EV.C


# --------------------------------------------------------------------------- synthetic questions / runs

def _q(qid, vid, source, vtype, cat, question, answer=None, path=""):
    r = {"qid": qid, "video_id": vid, "video_path": path, "video_type": vtype, "fps": FPS, "inference_type": "SS",
         "question": question, "prior": "diameter of the red ball = 0.5m", "depth_info": "", "video_source": source,
         "category": cat, "target_unit": "m"}
    if answer is not None:
        r["answer"] = answer
    return r


def _video(path: Path, n: int = 24) -> str:
    vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (160, 120))
    for i in range(n):
        im = np.full((120, 160, 3), 40, np.uint8)
        cv2.circle(im, (20 + 4 * i, 60), 8, (0, 0, 255), -1)
        vw.write(im)
    vw.release()
    return str(path)


def _write_run(split_dir: Path, recs: dict, transcripts: dict) -> None:
    """answers/<vid>.json records {vid: (answers, sources, end)} and transcripts/<vid>.json {vid: turns}."""
    (split_dir / "answers").mkdir(parents=True, exist_ok=True)
    (split_dir / "transcripts").mkdir(parents=True, exist_ok=True)
    for vid, (ans, src, end) in recs.items():
        rec = {"video_id": vid, "status": "done", "end": end, "forced": None,
               "answers": {str(k): v for k, v in ans.items()},
               "source": {str(k): s for k, s in src.items()}, "n_steps": 3}
        (split_dir / "answers" / f"{vid}.json").write_text(json.dumps(rec))
    for vid, turns in transcripts.items():
        (split_dir / "transcripts" / f"{vid}.json").write_text(json.dumps({"video_id": vid, "turns": turns}))


CLEAN = [{"role": "user", "text": "Video ..."}, {"role": "assistant", "text": "```python\nprint(1)\n```",
                                                  "thinking_tail": "", "action": "python"},
         {"role": "user", "text": "Python result: exit code 0 (0.1 s)\nstdout:\n1"},
         {"role": "assistant", "text": "ANSWERS {}", "action": "answers"}]


def _leaky(path="/content/drive/MyDrive/quantiphy/data/QuantiPhy-validation/x.csv"):
    return [{"role": "user", "text": "Video ..."},
            {"role": "assistant", "text": f"```python\nprint(open({path!r}).read())\n```", "action": "python"},
            {"role": "user", "text": f"Python result: exit code 1\nstderr:\nPermissionError: outside the workspace: {path}"}]


# --------------------------------------------------------------------------- fix 1: validation base at full resolution

def test_make_base_takes_the_test_value_for_duplicated_questions():
    MB = _load("make_base")
    val = pd.DataFrame([_q(1, "clip_a", "simulation", "S2MC", "S2", "What is the speed at 1.0s in m/s?"),
                        _q(2, "clip_a", "simulation", "S2MC", "S2", "What is the width of the box in meters?"),
                        _q(3, "clip_b", "simulation", "S2MC", "S2", "What is the height in meters?"),
                        _q(4, "clip_c", "simulation", "S2MC", "S2", "What is the height in meters?")])
    test = pd.DataFrame([_q(11, "clip_a", "simulation", "S2MC", "S2", "What is the speed at 1s in m/s ?"),   # same
                         _q(12, "clip_a", "simulation", "S2MC", "S2", "What is the depth of the box in meters?"),
                         _q(13, "clip_c", "simulation", "S2MC", "S2", "What is the height in meters?"),     # twice:
                         _q(14, "clip_c", "simulation", "S2MC", "S2", "What is the height in meters?")])    # ambiguous
    vmap = MB.val_test_map(val, test)
    assert vmap == {1: 11}
    val2 = val.assign(inference_type=["DS", "SS", "SS", "SS"])
    assert MB.val_test_map(val2, test) == {}             # another inference type is another question
    comb = pd.DataFrame({"qid": [1, 2, 3, 4], "video_id": ["clip_a", "clip_a", "clip_b", "clip_c"],
                         "base": [5.0, 6.0, np.nan, 7.0], "stated": [0, 1, 0, 0]})
    bt = pd.DataFrame({"id": [11, 12, 13, 14], "base": [9.0, 1.0, 1.0, 1.0], "stated": [1, 0, 0, 0]})
    out = MB.with_test_values(comb, bt, vmap)
    assert out.base.tolist()[:2] == [9.0, 6.0] and np.isnan(out.base[2]) and out.base[3] == 7.0
    assert out.stated.tolist() == [1, 1, 0, 0]
    assert out.test_id.tolist()[0] == 11 and out.test_id.isna().tolist() == [False, True, True, True]


def test_regenerated_base_val_uses_base_test_on_duplicates():
    bv = pd.read_csv(TBA / "base_val.csv")
    bt = pd.read_csv(TBA / "base_test.csv").set_index("id")
    assert len(bv) == 159 and len(bt) == 3289 and "test_id" in bv
    dup = bv[bv.test_id.notna()]
    assert len(dup) == 131
    assert np.allclose(dup.base.to_numpy(), bt.base.reindex(dup.test_id.astype(int)).to_numpy(), rtol=1e-12)
    assert (dup.stated.to_numpy() == bt.stated.reindex(dup.test_id.astype(int)).to_numpy()).all()
    assert bv.qid[bv.base.isna()].tolist() == [2607]


# --------------------------------------------------------------------------- fix 2: rows without a base value

def _val_setup(EV, C, monkeypatch, rows, base):
    gt = pd.DataFrame(rows)
    monkeypatch.setattr("qp.data.load_validation", lambda *a, **k: gt.copy())
    monkeypatch.setattr(C, "load_base", lambda name: base.copy())
    return gt


def test_row_without_base_is_left_out_of_the_type_means(EV, C, monkeypatch, tmp_path):
    rows = [_q(1, "captured_0001", "lab", "S3MC", "S3", "q1", 1.0), _q(2, "captured_0001", "lab", "S3MC", "S3", "q2", 2.0),
            _q(3, "captured_0001", "lab", "S3MC", "S3", "q3", 3.0), _q(4, "captured_0002", "lab", "S3MC", "D3", "q4", 4.0),
            _q(5, "simulation_0001", "simulation", "S2MC", "S2", "q5", 1.0),
            _q(6, "simulation_0001", "simulation", "D2MC", "D2", "q6", 1.0)]
    base = pd.DataFrame({"qid": [1, 2, 3, 4, 5, 6], "video_id": [r["video_id"] for r in rows],
                         "base": [1.0, 2.0, 3.0, np.nan, 1.0, 1.0], "stated": 0})
    _val_setup(EV, C, monkeypatch, rows, base)
    root = tmp_path / "run"
    # the agent answers only the row without a base value (exactly): before the fix lab scored agent 1.0 vs base .75
    _write_run(root / "val", {"captured_0002": ({4: 4.0}, {4: "agent"}, "done")}, {"captured_0002": CLEAN})
    routing = tmp_path / "routing.json"
    assert EV.main(["--root", str(root), "--write", "--routing", str(routing)]) == 0
    R = json.loads(routing.read_text())
    lab = next(r for r in R["scores"] if r["type"] == "lab")
    assert lab["questions"] == 3 and lab["no_base"] == 1 and lab["agent_rows"] == 0
    assert lab["base"] == pytest.approx(1.0) and lab["agent"] == pytest.approx(1.0)
    assert R["decision"]["lab"] == "base"


def test_per_type_counts_only_rows_with_base(EV, C):
    v = pd.DataFrame({"type": ["lab"] * 4, "base": [1.0, 1.0, np.nan, 2.0], "agent_raw": [np.nan, 1.1, 5.0, 2.0],
                      "video_id": ["a", "a", "b", "b"]}, index=[1, 2, 3, 4])
    S = pd.DataFrame({"base": [1.0, 0.5, 0.0, 0.2], "agent": [1.0, 1.0, 1.0, 1.0], "gm": [1.0, 0.8, 1.0, 0.6]},
                     index=v.index)
    R, dec = EV.per_type(v, S, pd.Series(False, index=v.index))
    lab = R.set_index("type").loc["lab"]
    assert lab.questions == 3 and lab.no_base == 1 and lab.agent_rows == 2
    assert lab.base == pytest.approx(1.7 / 3) and lab.agent == pytest.approx(1.0) and dec["lab"] == "agent"


# --------------------------------------------------------------------------- fix 3: twin routing

def _test_questions():
    return pd.DataFrame([
        _q(101, "internet_0001", "internet", "S2MC", "S2", "What is the speed of the ball in m/s?"),
        _q(102, "internet_0001", "internet", "S2MC", "S2", "What is the width of the ball in meters?"),
        _q(103, "internet_0001_segmented", "segmentation", "S2MC", "S2", "What is the speed of the ball in m/s?"),
        _q(104, "internet_0001_segmented", "segmentation", "S2MC", "S2", "What is the width of the ball in meters?"),
        _q(105, "internet_0001_segmented", "segmentation", "S2MC", "S2", "What is the height of the ball in meters?"),
        _q(106, "simulation_0001", "simulation", "S2MC", "S2", "What is the width of the box in meters?"),
        _q(107, "simulation_0001_segmented", "segmentation", "S2MC", "S2", "What is the width of the box in meters?"),
        _q(108, "simulation_0009_segmented", "segmentation", "S3MC", "S3", "What is the width of the box in meters?"),
        _q(109, "internet_0002", "internet", "S2MC", "S2", "What is the speed of the car in m/s?"),
    ]).set_index("qid")


def test_route_types_follow_the_original_clip(C):
    t = _test_questions()
    assert C.twin_origin("twin:internet_0001:101") == ("internet_0001", 101)
    assert C.twin_origin("agent") is None and C.twin_origin(None) is None and C.twin_origin("twin:x") is None
    own = [C.clip_type(s, v) for s, v in zip(t.video_source, t.video_type)]
    assert own[2:5] == ["sim2"] * 3                      # what the old build_sub routed the internet twin by
    rt = C.route_types(t)
    assert rt.tolist() == ["internet"] * 5 + ["sim2", "sim2", "sim3", "internet"]
    # a twin-sourced row is routed by the original row's type even without the segmented-name rule
    t2 = t.copy()
    t2.loc[107, "video_id"] = "other_clip"
    src = pd.Series({107: "twin:internet_0001:102"})
    assert C.route_types(t2, src)[107] == "internet" and C.route_types(t2)[107] == "sim2"
    vids = C.agent_test_videos(t, {"internet": "agent", "sim2": "base", "sim3": "base", "lab": "base"})
    assert vids == ["internet_0001", "internet_0001_segmented", "internet_0002"]
    vids = C.agent_test_videos(t, {"sim2": "gm"})
    assert vids == ["simulation_0001", "simulation_0001_segmented"]
    assert C.agent_test_videos(t, {k: "base" for k in C.TYPES}) == []


def _build(BS, C, monkeypatch, tmp_path, t, decision, recs, transcripts, stated=()):
    monkeypatch.setattr("qp.data.load_split", lambda split: t.reset_index())
    bt = pd.DataFrame({"id": t.index, "base": 1.0, "stated": [int(q in stated) for q in t.index]})
    monkeypatch.setattr(C, "load_base", lambda name: bt.copy())
    root = tmp_path / "run"
    _write_run(root / "test", recs, transcripts)
    routing = tmp_path / "routing.json"
    routing.write_text(json.dumps({"decision": decision, "written": "test"}))
    sent = []

    def fake_run(cmd, **kw):   # make_submission: keep the file it would fill the template from
        sent.append(pd.read_csv(cmd[2]).set_index("id").parsed_value)
        return type("R", (), {"returncode": 0})

    monkeypatch.setattr(BS.subprocess, "run", fake_run)
    assert BS.main(["--root", str(root), "--routing", str(routing), "--out", str(tmp_path / "sub.csv")]) == 0
    return sent[0]


def test_build_sub_routes_twins_by_the_original_type(BS, C, monkeypatch, tmp_path, capsys):
    t = _test_questions()
    recs = {"internet_0001": ({101: 4.0, 102: 2.0}, {101: "agent", 102: "agent"}, "done"),
            # agent loop: 103 copied from the original (source twin:...), 105 the twin's own question; 104 left for
            # build_sub's fill
            "internet_0001_segmented": ({103: 4.0, 105: 3.0}, {103: "twin:internet_0001:101", 105: "agent"}, "done"),
            "simulation_0001": ({106: 5.0}, {106: "agent"}, "done"),
            "simulation_0001_segmented": ({107: 5.0}, {107: "twin:simulation_0001:106"}, "twin")}
    trs = {v: CLEAN for v in ("internet_0001", "internet_0001_segmented", "simulation_0001")}
    dec = {"sim3": "base", "sim2": "base", "internet": "agent", "lab": "base"}
    out = _build(BS, C, monkeypatch, tmp_path, t, dec, recs, trs, stated=(102,))
    assert out[101] == 4.0 and out[102] == 1.0                          # stated row keeps the base
    assert out[103] == 4.0 and out[105] == 3.0                          # internet twin: internet decision
    assert out[104] == 2.0                    # filled here from 102 (twin:internet_0001:102): internet decision
    assert out[106] == 1.0 and out[107] == 1.0 and out[108] == 1.0      # sim2 / sim3 -> base
    o = capsys.readouterr().out
    assert "rows routed by their original clip's type (twins)" in o
    # gm on internet, and the build_sub fill (source twin:<orig>:<qid>) follows the original's type too
    recs["internet_0001"] = ({101: 4.0, 102: 9.0}, {101: "agent", 102: "agent"}, "done")
    out = _build(BS, C, monkeypatch, tmp_path, t, {**dec, "internet": "gm"}, recs, trs)
    assert out[104] == pytest.approx(3.0) and out[102] == pytest.approx(3.0) and out[101] == pytest.approx(2.0)
    assert "1 filled from twins here" in capsys.readouterr().out


def test_build_sub_fill_twins_records_the_source(BS):
    t = _test_questions()
    ag = pd.Series(np.nan, index=t.index)
    ag[101], ag[102] = 4.0, 2.0
    src = pd.Series(None, index=t.index, dtype=object)
    a2, s2, n = BS.fill_twins(t, ag, src)
    assert n == 2 and a2[103] == 4.0 and s2[104] == "twin:internet_0001:102" and np.isnan(a2[105])
    a3, _, n3 = BS.fill_twins(t, ag, src, exclude={"internet_0001_segmented"})
    assert n3 == 0 and np.isnan(a3[103])


# --------------------------------------------------------------------------- fix 6: transcript audit

def test_scan_transcript_and_audit_result_shapes(C):
    assert C.scan_transcript({"turns": CLEAN}) == []
    hits = C.scan_transcript({"turns": _leaky()})
    assert any("/content/drive" in h for h in hits) and any("outside the workspace" in h for h in hits)
    tail = [{"role": "assistant", "text": "FRAME 1", "thinking_tail": "maybe read ../other_clip/answers.json"}]
    assert C.scan_transcript({"turns": tail})
    net = [{"role": "user", "text": "PermissionError: network access is disabled in this sandbox"}]
    assert C.scan_transcript({"turns": net})
    # questions in the first user turn are not scanned against LEAK
    assert C.scan_transcript({"turns": [{"role": "user", "text": "ground_truth of ../x"}]}) == []
    R = C._audit_result
    assert R(True) == ["flagged by audit_transcript"] and R(False) == [] and R([]) == [] and R(["x"]) == ["x"]
    assert R({"hits": [], "denied": 2}) == [] and R({"hits": ["a"]}) == ["a"]
    assert R({"flagged": True}) == ["flagged by audit_transcript"] and R({"flagged": False, "hits": ["a"]}) == []
    assert R({"ok": False, "reasons": ["r"]}) == ["r"] and R({"ok": True}) == []
    assert R(None) is None and R({"n_turns": 3}) is None and R(3) is None
    # verifier: only a list of findings is a findings list; (hits, n_denied) / (leaks, refusals) pairs are not
    assert R(([], 0)) is None and R(([], [])) is None and R((["x"], 2)) is None
    assert R([(3, "../")]) == ["(3, '../')"] and R([{"turn": 3}]) == ["{'turn': 3}"]


def test_audit_clips_uses_agent_loop_audit_transcript(C, monkeypatch, tmp_path, capsys):
    from qp.open import agent_loop as AL
    seen = []

    def fake_audit(tr):
        seen.append(tr["video_id"])
        return ["fake hit"] if tr["video_id"] == "b" else []

    monkeypatch.setattr(AL, "audit_transcript", fake_audit, raising=False)
    d = tmp_path / "val"
    _write_run(d, {"a": ({1: 1.0}, {}, "done"), "b": ({2: 1.0}, {}, "done"), "c": ({3: 1.0}, {}, "done"),
                   "d_segmented": ({4: 1.0}, {4: "twin:a:1"}, "twin")},
               {"a": _leaky(), "b": CLEAN})
    recs = C.agent_answers(d)[2]
    fl = C.audit_clips(d, recs)
    assert sorted(seen) == ["a", "b"]
    # b: flagged by audit_transcript; a: the fake says clean but the local scan flags it (either flags -> excluded)
    assert fl["b"] == ["fake hit"] and fl["c"] == ["no transcript: its answers cannot be audited"]
    assert set(fl) == {"a", "b", "c"} and fl["a"] == C.scan_transcript({"turns": _leaky()})
    assert "qp.open.agent_loop.audit_transcript" in capsys.readouterr().out
    # an unrecognised result or an exception -> the local scan for that transcript
    monkeypatch.setattr(AL, "audit_transcript", lambda tr: None, raising=False)
    assert set(C.audit_clips(d, recs)) == {"a", "c"}
    monkeypatch.setattr(AL, "audit_transcript", lambda path, other: [], raising=False)
    assert set(C.audit_clips(d, recs)) == {"a", "c"}
    # verifier: a clean (hits, n_denied) pair is not a findings list (it used to flag EVERY clip), and a refusal the
    # function reports under a key not understood here (it used to read as clean) is still caught by the scan
    monkeypatch.setattr(AL, "audit_transcript", lambda tr: ([], 0), raising=False)
    assert set(C.audit_clips(d, recs)) == {"a", "c"}
    monkeypatch.setattr(AL, "audit_transcript", lambda tr: {"hits": [], "denied": 1}, raising=False)
    assert set(C.audit_clips(d, recs)) == {"a", "c"}
    monkeypatch.setattr(AL, "audit_transcript", lambda tr: {"leaks": [], "refusals": ["outside the workspace"]},
                        raising=False)
    assert set(C.audit_clips(d, recs)) == {"a", "c"}
    # a clean verdict of audit_transcript does not clear a sandbox refusal (os.listdir('..') names no path pattern)
    (d / "transcripts" / "b.json").write_text(json.dumps({"video_id": "b", "turns": [
        {"role": "assistant", "text": "```python\nimport os\nprint(os.listdir('..'))\n```", "action": "python"},
        {"role": "user", "text": "Python result: exit code 1\nstderr:\nPermissionError: outside the workspace: .."}]}))
    monkeypatch.setattr(AL, "audit_transcript", lambda tr: [], raising=False)
    fl = C.audit_clips(d, recs)
    assert set(fl) == {"a", "b", "c"} and fl["b"] == ["turn 1 tool result: 'outside the workspace'"]


def test_audit_clips_falls_back_when_the_import_fails(C, monkeypatch, tmp_path, capsys):
    monkeypatch.setitem(sys.modules, "qp.open.agent_loop", None)       # import raises ImportError
    d = tmp_path / "val"
    _write_run(d, {"a": ({1: 1.0}, {}, "done"), "b": ({2: 1.0}, {}, "done")}, {"a": _leaky(), "b": CLEAN})
    (d / "transcripts" / "zz.json").write_text("{not json")
    fl = C.audit_clips(d, C.agent_answers(d)[2])
    assert set(fl) == {"a", "zz"} and fl["zz"] == ["unreadable transcript"]
    o = capsys.readouterr().out
    assert "local scan_transcript" in o and "EXCLUDED a" in o


def test_agent_answers_drops_excluded_clips_and_their_twin_copies(C, tmp_path):
    d = tmp_path / "test"
    _write_run(d, {"a": ({1: 2.0, 2: 3.0}, {1: "agent", 2: "forced"}, "done"),
                   "a_segmented": ({3: 2.0, 4: 7.0}, {3: "twin:a:1", 4: "agent"}, "done"),
                   "b": ({5: 1.5}, {5: "agent"}, "done")}, {})
    ag, src, recs = C.agent_answers(d)
    assert sorted(ag.index) == [1, 2, 3, 4, 5] and src[3] == "twin:a:1"
    ag, src, recs = C.agent_answers(d, exclude={"a": ["x"]})
    assert sorted(ag.index) == [4, 5] and set(recs) == {"a", "a_segmented", "b"}


def test_evaluate_excludes_flagged_clips(EV, C, monkeypatch, tmp_path, capsys):
    rows = [_q(1, "internet_0001", "internet", "S2MC", "S2", "q1", 1.0),
            _q(2, "internet_0001", "internet", "D2MC", "D2", "q2", 1.0),
            _q(3, "simulation_0001", "simulation", "S3MC", "S3", "q3", 1.0),
            _q(4, "simulation_0001", "simulation", "D3MC", "D3", "q4", 1.0)]
    base = pd.DataFrame({"qid": [1, 2, 3, 4], "video_id": [r["video_id"] for r in rows], "base": 2.0, "stated": 0})
    _val_setup(EV, C, monkeypatch, rows, base)
    root = tmp_path / "run"
    _write_run(root / "val", {"internet_0001": ({1: 1.0, 2: 1.0}, {1: "agent", 2: "agent"}, "done"),
                              "simulation_0001": ({3: 1.0, 4: 1.0}, {3: "agent", 4: "agent"}, "done")},
               {"internet_0001": CLEAN, "simulation_0001": _leaky("/content/quantiphy-challenge/outputs/x.csv")})
    routing = tmp_path / "routing.json"
    assert EV.main(["--root", str(root), "--write", "--routing", str(routing)]) == 0
    R = json.loads(routing.read_text())
    assert R["decision"]["internet"] == "agent" and R["decision"]["sim3"] == "base"
    assert list(R["excluded"]) == ["simulation_0001"]
    assert next(r for r in R["scores"] if r["type"] == "sim3")["agent_rows"] == 0
    assert "EXCLUDED simulation_0001" in capsys.readouterr().out


# --------------------------------------------------------------------------- fix 4: the validation gate (evaluate --gate)

def test_evaluate_gate_json(EV, C, monkeypatch, tmp_path):
    rows = [_q(1, "internet_0001", "internet", "S2MC", "S2", "q1", 1.0),
            _q(2, "simulation_0001", "simulation", "D2MC", "D2", "q2", 1.0),
            _q(3, "simulation_0002", "simulation", "S3MC", "S3", "q3", 1.0),
            _q(4, "captured_0001", "lab", "D3MC", "D3", "q4", 1.0)]
    base = pd.DataFrame({"qid": [1, 2, 3, 4], "video_id": [r["video_id"] for r in rows], "base": 1.05, "stated": 0})
    _val_setup(EV, C, monkeypatch, rows, base)
    t = _test_questions().reset_index()
    monkeypatch.setattr("qp.data.load_split", lambda split: t.copy())
    root = tmp_path / "run"
    gate = tmp_path / "gate.json"
    _write_run(root / "val", {"internet_0001": ({1: 1.0}, {1: "agent"}, "done")}, {"internet_0001": CLEAN})
    assert EV.main(["--root", str(root), "--gate", str(gate)]) == 0
    g = json.loads(gate.read_text())
    assert g["run_test"] and g["decision"]["internet"] == "agent" and g["decision"]["sim2"] == "base"
    assert g["test_videos"] == ["internet_0001", "internet_0001_segmented", "internet_0002"]
    assert g["val_clips"] == 4 and g["val_clips_done"] == 1 and not g["val_complete"]
    # the agent loses everywhere -> every type routes to base, no test clip
    _write_run(root / "val", {"internet_0001": ({1: 9.0}, {1: "agent"}, "done")}, {"internet_0001": CLEAN})
    assert EV.main(["--root", str(root), "--gate", str(gate)]) == 0
    g = json.loads(gate.read_text())
    assert not g["run_test"] and g["test_videos"] == [] and g["reason"].startswith("every clip type routes to the base")


# --------------------------------------------------------------------------- fixes 4, 5: the notebook's agent stage

def _nb():
    spec = importlib.util.spec_from_file_location("_tba_nb", ROOT / "notebooks" / "_build_notebook.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _agent_cell(mod) -> str:
    return next(s for k, s in mod.CELLS if k == "code" and "def agent_gate" in s)


def _run_agent_cell(tmp_path, monkeypatch, gate, limit=0, routed_only=True, splits=("val", "test"), stage_on=True):
    mod = _nb()
    cfg = next(s for k, s in mod.CELLS if k == "code" and s.startswith("RUN_NAME = "))
    ns: dict = {}
    exec(cfg.replace('RUN_PRESET = ""', 'RUN_PRESET = "agent"', 1), ns)
    ns["STAGES"]["agent"] = stage_on
    monkeypatch.chdir(tmp_path)
    stages, cmds = [], []

    def sh(cmd, check=True, cwd=None):
        cmds.append(cmd)
        if "evaluate.py" in cmd:
            assert "--gate " in cmd and f"--root outputs/{ns['RUN_NAME']}" in cmd
            if gate is None:
                return 1
            p = Path(cmd.split("--gate ")[1].split()[0])
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(gate))
        return 0

    import os
    ns.update(os=os, SPLITS=list(splits), LIMIT_VIDEOS=limit, LIM=f" --limit-videos {limit}" if limit else "",
              FAILED=[], AGENT_TEST_ROUTED_ONLY=routed_only, sh=sh,
              out_dir=lambda split, name: f"outputs/{ns['RUN_NAME']}/{split}/{name}",
              stage=lambda name, split, cmd: stages.append((name, split, cmd)) or 0,
              push_outputs=lambda tag="final": None)
    exec(_agent_cell(mod), ns)
    return stages, cmds, ns


def _gate(run_test, vids=(), complete=True):
    return {"decision": {"sim3": "base", "sim2": "base", "internet": "agent" if run_test else "base", "lab": "base"},
            "run_test": run_test, "reason": "r", "val_clips": 24, "val_clips_done": 24 if complete else 20,
            "val_complete": complete, "excluded": [], "test_videos": list(vids), "n_test_videos": len(vids)}


def test_notebook_gate_skips_test_when_every_type_routes_to_base(tmp_path, monkeypatch, capsys):
    stages, cmds, ns = _run_agent_cell(tmp_path, monkeypatch, _gate(False))
    assert [(n, s) for n, s, _ in stages] == [("agent", "val")]
    assert any("evaluate.py" in c for c in cmds)
    assert "TEST SKIPPED" in capsys.readouterr().out and not ns["FAILED"]


def test_notebook_gate_restricts_test_and_passes_prefix_caching(tmp_path, monkeypatch):
    stages, _, _ = _run_agent_cell(tmp_path, monkeypatch, _gate(True, ["internet_0001", "internet_0001_segmented"]))
    assert [(n, s) for n, s, _ in stages] == [("agent", "val"), ("agent", "test")]
    val_cmd, test_cmd = stages[0][2], stages[1][2]
    for c in (val_cmd, test_cmd):
        assert "python -m qp.open.run_agent" in c and " --prefix-caching on " in c
    assert "--videos" not in val_cmd and " --videos internet_0001,internet_0001_segmented" in test_cmd
    stages, _, _ = _run_agent_cell(tmp_path, monkeypatch, _gate(True, ["internet_0001"]), routed_only=False)
    assert "--videos" not in stages[1][2]


def test_notebook_gate_not_applied_in_smoke_runs_failures_or_incomplete_val(tmp_path, monkeypatch, capsys):
    stages, _, _ = _run_agent_cell(tmp_path, monkeypatch, _gate(False), limit=2)
    assert [s for _, s, _ in stages] == ["val", "test"]
    assert "--limit-videos 2" in stages[1][2] and "--videos" not in stages[1][2]
    assert "smoke run" in capsys.readouterr().out
    stages, _, ns = _run_agent_cell(tmp_path, monkeypatch, None)        # evaluate.py failed
    assert [s for _, s, _ in stages] == ["val", "test"] and "--videos" not in stages[1][2]
    assert any("evaluate.py failed" in f for f in ns["FAILED"])
    stages, _, _ = _run_agent_cell(tmp_path, monkeypatch, _gate(False, complete=False))
    assert [s for _, s, _ in stages] == ["val", "test"] and "--videos" not in stages[1][2]
    stages, cmds, _ = _run_agent_cell(tmp_path, monkeypatch, _gate(False), splits=("test",))
    assert [s for _, s, _ in stages] == ["test"] and not any("evaluate.py" in c for c in cmds)
    stages, cmds, _ = _run_agent_cell(tmp_path, monkeypatch, _gate(False), stage_on=False)   # GPU too small
    assert [s for _, s, _ in stages] == ["val", "test"] and not any("evaluate.py" in c for c in cmds)


def test_notebook_config_and_generated_notebook(tmp_path):
    mod = _nb()
    src = "\n".join(s for k, s in mod.CELLS if k == "code")
    assert 'AGENT_PREFIX_CACHING = "on"' in src and "--prefix-caching {AGENT_PREFIX_CACHING}" in src
    assert "AGENT_TEST_ROUTED_ONLY = True" in src
    nb = json.loads((ROOT / "notebooks" / "colab_pipeline.ipynb").read_text())
    built = mod.build()
    assert [c["source"] for c in nb["cells"]] == [c["source"] for c in built["cells"]], \
        "colab_pipeline.ipynb is stale: run python notebooks/_build_notebook.py"


# --------------------------------------------------------------------------- end to end with a scripted fake model

class FakeModel:
    """Scripted open-model stand-in: per clip id a list of replies (by assistant turn number); 'ANSWERS' replies are
    built from `truth` (qid -> value) times the clip's factor."""

    def __init__(self, plans, truth):
        self.plans, self.truth = plans, truth

    def generate(self, reqs):
        out = []
        for r in reqs:
            first = r.messages[1]["content"][0]["text"]
            vid = re.search(r"Video (\S+):", first).group(1)
            qids = [int(x) for x in re.findall(r"- qid (\d+)", first)]
            n = sum(1 for m in r.messages if m["role"] == "assistant")
            plan, factor = self.plans[vid]
            s = plan[min(n, len(plan) - 1)]
            if s == "ANSWERS":
                s = "ANSWERS " + json.dumps({str(q): self.truth[q] * factor for q in qids})
            out.append(s)
        return out


PY_OK = "Measure.\n```python\nimport json\nprint(json.load(open('inputs.json'))['n_frames'])\n```"
PY_LEAK = ("Read the labels.\n```python\nprint(open('/content/drive/MyDrive/quantiphy/data/QuantiPhy-validation/"
           "validation.csv').read())\n```")


def test_end_to_end_fake_model_gate_and_build(EV, BS, C, monkeypatch, tmp_path, capsys):
    from qp.open import run_agent as RA
    vids = tmp_path / "videos"
    vids.mkdir()
    P = {v: _video(vids / f"{v}.mp4") for v in ("internet_0001", "internet_0001_segmented", "internet_0002",
                                                "simulation_0001", "captured_0001")}
    val = pd.DataFrame([_q(1, "internet_0001", "internet", "S2MC", "S2", "What is the speed of the ball in m/s?",
                           2.0, P["internet_0001"]),
                        _q(2, "internet_0001", "internet", "D2MC", "D2", "What is the width of the ball in meters?",
                           0.5, P["internet_0001"]),
                        _q(3, "simulation_0001", "simulation", "S3MC", "S3", "What is the width of the box in meters?",
                           1.0, P["simulation_0001"]),
                        _q(4, "captured_0001", "lab", "D3MC", "D3", "What is the height of the cup in meters?",
                           0.1, P["captured_0001"])])
    test = pd.DataFrame([_q(101, "internet_0001", "internet", "S2MC", "S2", "What is the speed of the ball in m/s?",
                            path=P["internet_0001"]),
                         _q(102, "internet_0001_segmented", "segmentation", "S2MC", "S2",
                            "What is the speed of the ball in m/s?", path=P["internet_0001_segmented"]),
                         _q(103, "internet_0001_segmented", "segmentation", "S2MC", "S2",
                            "What is the height of the ball in meters?", path=P["internet_0001_segmented"]),
                         _q(104, "internet_0002", "internet", "S2MC", "S2", "What is the speed of the car in m/s?",
                            path=P["internet_0002"]),
                         _q(105, "simulation_0001", "simulation", "S3MC", "S3", "What is the width of the box in meters?",
                            path=P["simulation_0001"])])
    truth = {1: 2.0, 2: 0.5, 3: 1.0, 4: 0.1, 101: 2.0, 102: 2.0, 103: 0.3, 104: 7.0, 105: 1.0}
    monkeypatch.setattr("qp.data.load_validation", lambda *a, **k: val.copy())
    monkeypatch.setattr("qp.data.load_split", lambda split: (test if split == "test" else val).copy())
    root = tmp_path / "outputs" / "trackb_agent"
    common = ["--ws-root", str(tmp_path / "ws"), "--no-thinking", "--tool-workers", "2", "--prefix-caching", "on"]
    # validation: internet exact, the sim clip tries to read the labels (flagged), lab 3x off
    fake = FakeModel({"internet_0001": ([PY_OK, "ANSWERS"], 1.0), "simulation_0001": ([PY_LEAK, "ANSWERS"], 1.0),
                      "captured_0001": ([PY_OK, "ANSWERS"], 3.0)}, truth)
    assert RA.main(["--split", "val_hires", "--out", str(root / "val"), *common], backend=fake) == 0
    tr = json.loads((root / "val" / "transcripts" / "simulation_0001.json").read_text())
    assert any("outside the workspace" in (t.get("text") or "") for t in tr["turns"] if t["role"] == "user")
    base_val = pd.DataFrame({"qid": [1, 2, 3, 4], "video_id": val.video_id, "base": [3.0, 0.75, 1.5, 0.1],
                             "stated": 0})
    base_test = pd.DataFrame({"id": test.qid, "base": 5.0, "stated": 0})
    monkeypatch.setattr(C, "load_base", lambda name: (base_val if name == "base_val.csv" else base_test).copy())
    gate, routing = root / "val" / "gate.json", tmp_path / "routing.json"
    assert EV.main(["--root", str(root), "--write", "--routing", str(routing), "--gate", str(gate)]) == 0
    g, R = json.loads(gate.read_text()), json.loads(routing.read_text())
    assert R["decision"] == {"sim3": "base", "sim2": "base", "internet": "agent", "lab": "base"}
    assert list(R["excluded"]) == ["simulation_0001"] and g["val_complete"] and g["run_test"]
    assert g["test_videos"] == ["internet_0001", "internet_0001_segmented", "internet_0002"]
    # test, restricted by the gate as the notebook does; internet_0002's agent tries the parent directory (flagged)
    fake = FakeModel({"internet_0001": ([PY_OK, "ANSWERS"], 1.0), "internet_0001_segmented": ([PY_OK, "ANSWERS"], 1.0),
                      "internet_0002": (["```python\nimport os\nprint(os.listdir('..'))\n```", "ANSWERS"], 1.0)},
                     truth)
    assert RA.main(["--split", "test", "--out", str(root / "test"), "--videos", ",".join(g["test_videos"]), *common],
                   backend=fake) == 0
    rec = json.loads((root / "test" / "answers" / "internet_0001_segmented.json").read_text())
    assert rec["source"]["102"] == "twin:internet_0001:101" and rec["source"]["103"] == "agent"
    assert not (root / "test" / "answers" / "simulation_0001.json").exists()
    sent = []
    monkeypatch.setattr(BS.subprocess, "run", lambda cmd, **kw: sent.append(pd.read_csv(cmd[2])) or None)
    assert BS.main(["--root", str(root), "--routing", str(routing), "--out", str(tmp_path / "sub.csv")]) == 0
    out = sent[0].set_index("id").parsed_value
    assert out[101] == pytest.approx(2.0)
    assert out[102] == pytest.approx(2.0) and out[103] == pytest.approx(0.3)   # internet twin: internet decision
    assert out[104] == 5.0 and out[105] == 5.0                                 # excluded clip / sim3 base
    o = capsys.readouterr().out
    assert "EXCLUDED internet_0002" in o and "EXCLUDED simulation_0001" in o


# --------------------------------------------------------------------------- fixes 7, 8: the documents

def test_pre_registration_and_run_instructions_name_the_fixes():
    res = " ".join((TBA / "RESULT.md").read_text().split())
    for s in ("B2route TEST value", ".6431", "2607", "route_types", "ORIGINAL clip's type", "internet decision",
              "audit_transcript", "EXCLUDED", "no validation or test answer of the agent exists yet"):
        assert s in res, s
    ri = " ".join((TBA / "RUN_INSTRUCTIONS.md").read_text().split())
    for s in ("AUTO_TERMINATE = False", "AUTO_TERMINATE = True", "2 validation clips and 2 test clips",
              "ESTIMATE", "--prefix-caching on", 'AGENT_PREFIX_CACHING = "off"', "align", "No action found",
              "too long", "generation_failed", "Send back", "TEST SKIPPED"):
        assert s in ri, s
