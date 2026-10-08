"""qp.claude_agent + scripts/run_claude_agent.py with a fake client (no API): tool implementations on a
synthetic video (coordinates of crops / ticks / marks map back to original pixels exactly; tracker and
segmentation accuracy), solve / submit, and the loop mechanics (append-only history, tool_result pairing,
cache / thinking / tool_choice parameters, turn cap, budget stops, nudges, records, ledger, resume)."""

from __future__ import annotations

import base64
import copy
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
from qp import claude_agent as ag

ROOT = Path(__file__).resolve().parents[1]
W, H, FPS, N = 320, 240, 30.0, 30
DIAM = 20.0                       # ball diameter, px
X0, VX, Y = 60.0, 3.0, 120.0      # ball centre x(f) = X0 + VX f, y = Y (px)


def ball_x(f: float) -> float:
    return X0 + VX * f


def ball_box(f: int) -> list[float]:
    return [ball_x(f) - DIAM / 2, Y - DIAM / 2, ball_x(f) + DIAM / 2, Y + DIAM / 2]


def make_video(path: Path) -> None:
    """A red ball (sub-pixel centres, antialiased) crossing a static textured scene, plus a static bar."""
    rng = np.random.default_rng(0)
    bg = np.clip(rng.normal(90, 6, (H, W, 3)), 0, 255).astype(np.uint8)
    bg = cv2.GaussianBlur(bg, (0, 0), 1.0)
    cv2.rectangle(bg, (200, 40), (279, 59), (230, 230, 230), -1)          # bar: x 200..280, y 40..60
    vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W, H))
    for f in range(N):
        img = bg.copy()
        c = (int(round((ball_x(f) - 0.5) * 16)), int(round((Y - 0.5) * 16)))   # continuous -> cv2 pixel centres
        cv2.circle(img, c, int(DIAM / 2 * 16), (40, 40, 220), -1, cv2.LINE_AA, 4)
        vw.write(img)
    vw.release()


def questions(video: Path) -> pd.DataFrame:
    rows = [(101, "What is the diameter of the ball in cm?", "speed of the ball = 0.9 m/s", "cm", 20.0, "DS"),
            (102, "What is the speed of the ball in m/s?", "diameter of the ball = 0.2 m", "m/s", 0.9, "SD")]
    return pd.DataFrame([{"qid": q, "video_id": "vid_a", "video_path": str(video), "video_type": "V2SC", "fps": FPS,
                          "inference_type": it, "question": qu, "prior": pr, "depth_info": "",
                          "video_source": "simulation", "category": it[0] + "2", "target_unit": u, "answer": a}
                         for q, qu, pr, u, a, it in rows])


@pytest.fixture
def ws(tmp_path, monkeypatch):
    video = tmp_path / "vid_a.mp4"
    make_video(video)
    monkeypatch.setenv("QP_LEDGER", str(tmp_path / "ledger.jsonl"))
    monkeypatch.setenv("QP_BUDGET_USD", "50")
    return SimpleNamespace(root=tmp_path, video=video, df=questions(video))


def _session(ws, **kw) -> ag.AgentSession:
    return ag.AgentSession(ws.df, **kw)


def _decode(block) -> np.ndarray:
    return cv2.imdecode(np.frombuffer(base64.b64decode(block["source"]["data"]), np.uint8), cv2.IMREAD_COLOR)


def _mapping(text: str):
    m = re.search(r"x = (-?\d+) \+ \(u - (\d+)\) / ([\d.]+), y = (-?\d+) \+ \(v - (\d+)\) / ([\d.]+)", text)
    x0, ml, z, y0, mt, z2 = (float(g) for g in m.groups())
    assert z == z2
    return lambda u, v: (x0 + (u - ml) / z, y0 + (v - mt) / z)


# --------------------------------------------------------------------------- rendering


def test_view_geometry_zoom_snapping_and_clipping():
    assert ag.view_geometry(854, 480) == (0, 0, 854, 480, 1.0)                  # full frames never upscaled
    x0, y0, x1, y1, z = ag.view_geometry(3840, 2160)
    assert (x0, y0, x1, y1) == (0, 0, 3840, 2160) and round(3840 * z) == 1024 and round(2160 * z) == 576
    x0, y0, x1, y1, z = ag.view_geometry(854, 480, [100, 100, 211, 160], 2.7)   # 111 px wide, zoom -> 2.5
    assert z == 2.5 and (x1 - x0) % 2 == 0 and (y1 - y0) % 2 == 0 and x1 - x0 >= 111
    assert ag.view_geometry(854, 480, [10, 10, 30, 20])[4] == 8.0               # auto: MAX_ZOOM
    assert ag.view_geometry(854, 480, [-50, -20, 900, 500], 1)[:4] == (0, 0, 854, 480)
    x0, _, x1, _, z = ag.view_geometry(854, 480, [0, 0, 600, 100], 5)           # capped to fit 1024 px
    assert (x1 - x0) * z <= 1024
    with pytest.raises(ag.ToolError):
        ag.view_geometry(854, 480, [900, 500, 950, 560])


@pytest.mark.parametrize("region,zoom", [(None, None), ([90, 40, 131, 75], None), ([95, 45, 140, 75], 2.5),
                                         ([60, 30, 300, 200], 3)])
def test_crop_pixels_and_mapping_text_map_back_to_original(region, zoom):
    img = np.zeros((H, W, 3), np.uint8)
    img[57, 101] = 255                  # pixel column 101, row 57: continuous centre (101.5, 57.5)
    v = ag.render_view(img, 0, region, zoom, grid=False)
    tmap = _mapping(v.mapping())
    out = v.img.astype(float).sum(axis=2)
    out[:ag.MT + 1] = 0
    out[:, :ag.ML + 1] = 0              # tick labels live in the margins (tick ends touch the first body px)
    ys, xs = np.nonzero(out > 0.5 * out.max())
    w = out[ys, xs]
    u, vv = (xs * w).sum() / w.sum() + 0.5, (ys * w).sum() / w.sum() + 0.5   # continuous image coords
    x, y = tmap(u, vv)
    assert x == pytest.approx(101.5, abs=0.5 / v.zoom + 0.15) and y == pytest.approx(57.5, abs=0.5 / v.zoom + 0.15)


def test_tick_labels_sit_at_their_original_coordinate():
    img = np.full((H, W, 3), 60, np.uint8)
    v = ag.render_view(img, 0, [100, 50, 160, 90], 8, grid=False)
    tmap = _mapping(v.mapping())
    # major ticks (every 5 original px at zoom 8): bright marks in the top margin, 2 px wide (antialiased)
    row = v.img[ag.MT - 4, :, 0].astype(int)
    px = [u for u in range(ag.ML + 1, v.img.shape[1]) if row[u] > 150]
    groups, cur = [], [px[0]]
    for u in px[1:]:
        if u == cur[-1] + 1:
            cur.append(u)
        else:
            groups.append(cur)
            cur = [u]
    groups.append(cur)
    xs = [tmap(np.mean(g) + 0.5, 0)[0] for g in groups]
    assert len(xs) >= 10 and all(abs(x - 5 * round(x / 5)) < 0.1 for x in xs)
    assert [5 * round(x / 5) for x in xs[:3]] == [105, 110, 115]


def test_marks_and_shown_measurements_are_drawn_at_their_coordinates(ws):
    s = _session(ws)
    out = s.execute("get_frames", {"frames": [10], "region": [40, 80, 140, 160], "zoom": 4,
                                   "marks": [{"kind": "point", "coords": [ball_x(10), Y], "label": ""}]})
    assert not out.is_error
    img = _decode(out.content[1])
    tmap = _mapping(out.content[0]["text"])
    red = (img[:, :, 2] > 200) & (img[:, :, 1] < 80) & (img[:, :, 0] < 80)    # mark colour 0 = red (BGR)
    red[:ag.MT] = False
    red[:, :ag.ML] = False
    ys, xs = np.nonzero(red)
    x, y = tmap(xs.mean() + 0.5, ys.mean() + 0.5)
    assert x == pytest.approx(ball_x(10), abs=0.3) and y == pytest.approx(Y, abs=0.3)
    bad = s.execute("get_frames", {"frames": [10], "show": ["T9"]})
    assert bad.is_error and "unknown measurement" in bad.content[0]["text"]
    assert s.execute("get_frames", {"frames": [N + 5]}).is_error
    assert s.execute("get_frames", {"times": [0.5], "marks": [{"kind": "box", "coords": [1, 2], "label": ""}]}).is_error


def test_initial_content_overview_and_questions(ws):
    s = _session(ws)
    content = s.initial_content()
    imgs = [b for b in content if b["type"] == "image"]
    assert len(imgs) == ag.OVERVIEW_FRAMES
    assert _decode(imgs[0]).shape[:2] == (H + ag.MT + cvf_margin_b(), W + ag.ML + cvf_margin_r())   # native size
    text = "\n".join(b["text"] for b in content if b["type"] == "text")
    assert "320x240 px" in text and "qid=101" in text and "qid=102" in text and "Asked unit: cm" in text


def cvf_margin_b():
    from qp import claude_verify as cvf
    return cvf.MARGIN_B


def cvf_margin_r():
    from qp import claude_verify as cvf
    return cvf.MARGIN_R


# --------------------------------------------------------------------------- measurement tools


@pytest.mark.parametrize("use_dense", [True, False])
def test_track_follows_the_ball_to_subpixel(ws, use_dense):
    s = _session(ws, use_dense=use_dense)
    out = s.execute("track", {"object": "ball", "anchors": [{"frame": 10, "box": ball_box(10)}]})
    assert not out.is_error, out.content[0]["text"]
    m = s.meas["T1"]
    assert m.kind == "track" and len(m.obs) == N
    err = [math.hypot(o["point"][0] - ball_x(o["frame"]), o["point"][1] - Y) for o in m.obs]
    assert max(err) < 0.6, max(err)
    text = out.content[0]["text"]
    assert "T1" in text and "tracked 30 of 30 frames" in text
    assert m.info["tracker"] == ("dense_track.track_pass" if use_dense else "ncc_fallback")
    assert any(b["type"] == "image" for b in out.content)
    # two anchors, limited range
    out = s.execute("track", {"object": "ball", "from_t": 5 / FPS, "to_t": 25 / FPS, "overlay": False,
                              "anchors": [{"frame": 8, "box": ball_box(8)}, {"frame": 20, "box": ball_box(20)}]})
    m2 = s.meas["T2"]
    assert [o["frame"] for o in m2.obs] == list(range(5, 26)) and not any(b["type"] == "image" for b in out.content)
    # between two anchors the track is qp.dense_track.dense_motion's (the fallback: chained passes)
    assert m2.info["between_anchors"] == ("dense_motion" if use_dense else "chained_passes"), m2.info
    assert max(math.hypot(o["point"][0] - ball_x(o["frame"]), o["point"][1] - Y) for o in m2.obs) < 0.6


def test_track_is_continuous_across_inconsistent_anchors(ws):
    s = _session(ws)
    off = [b + d for b, d in zip(ball_box(20), (3.0, -2.0, 3.0, -2.0))]     # second anchor 3 / 2 px off
    s.execute("track", {"object": "ball", "overlay": False,
                        "anchors": [{"frame": 8, "box": ball_box(8)}, {"frame": 20, "box": off}]})
    pts = {o["frame"]: np.array(o["point"]) for o in s.meas["T1"].obs}
    assert sorted(pts) == list(range(N))
    steps = [np.linalg.norm(pts[f + 1] - pts[f]) for f in range(N - 1)]
    assert max(abs(st - VX) for st in steps) < 0.8, steps      # tracker noise ~0.6; the anchor offset would add ~1.5


def test_track_rejects_bad_anchors(ws):
    s = _session(ws)
    assert s.execute("track", {"object": "ball", "anchors": []}).is_error
    assert s.execute("track", {"object": "ball", "anchors": [{"frame": 99, "box": ball_box(1)}]}).is_error
    assert s.execute("track", {"object": "ball", "anchors": [{"frame": 1, "box": [5, 5, 6, 6]}]}).is_error
    assert not s.meas


def test_segment_measures_ball_and_bar(ws):
    s = _session(ws)
    pad = [ball_box(10)[0] - 2, ball_box(10)[1] - 2, ball_box(10)[2] + 2, ball_box(10)[3] + 2]
    out = s.execute("segment", {"object": "ball", "frame": 10, "box": pad, "measure": "diameter"})
    assert not out.is_error, out.content[0]["text"]
    e = s.meas["S1"].obs[0]["extent"]
    assert math.hypot(e[1][0] - e[0][0], e[1][1] - e[0][1]) == pytest.approx(DIAM, abs=1.0)
    assert "other axes" in out.content[0]["text"].lower() and out.content[-1]["type"] == "image"
    out = s.execute("segment", {"object": "bar", "frame": 3, "box": [197, 37, 283, 63], "measure": "long"})
    e = s.meas["S2"].obs[0]["extent"]
    assert math.hypot(e[1][0] - e[0][0], e[1][1] - e[0][1]) == pytest.approx(80.0, abs=1.0)
    s.execute("segment", {"object": "bar", "frame": 3, "box": [197, 37, 283, 63], "measure": "short"})
    e = s.meas["S3"].obs[0]["extent"]
    assert math.hypot(e[1][0] - e[0][0], e[1][1] - e[0][1]) == pytest.approx(20.0, abs=1.0)
    # edges: rough endpoints snap onto the bar's ends
    out = s.execute("segment", {"object": "bar", "frame": 3, "measure": "long", "method": "edges",
                                "extent": [[202.5, 50], [277.0, 50]]})
    assert not out.is_error, out.content[0]["text"]
    e = s.meas["S4"].obs[0]["extent"]
    assert e[0][0] == pytest.approx(200, abs=0.75) and e[1][0] == pytest.approx(280, abs=0.75)
    assert s.execute("segment", {"object": "bar", "frame": 3, "measure": "long", "method": "edges"}).is_error


Q_SIZE = {"kind": "size", "objects": ["ball"], "dimension": "diameter", "time": None, "window": None, "axis": "any",
          "value_si": None, "unit": "cm"}
Q_SPEED = {"kind": "speed", "objects": ["ball"], "dimension": "", "time": None, "window": None, "axis": "any",
           "value_si": None, "unit": "m/s"}


def _spec(target, prior, value):
    return {"target": target, "prior": {**prior, "value_si": value, "unit": ""}, "notes": ""}


def _tr(role, refs=(), obs=()):
    return {"role": role, "object": "ball", "depth_name": "", "range_m": None, "refs": list(refs), "obs": list(obs)}


def _measure_all(s):
    s.execute("track", {"object": "ball", "anchors": [{"frame": 10, "box": ball_box(10)}], "overlay": False})
    pad = [ball_box(10)[0] - 2, ball_box(10)[1] - 2, ball_box(10)[2] + 2, ball_box(10)[3] + 2]
    s.execute("segment", {"object": "ball", "frame": 10, "box": pad, "measure": "diameter"})


def test_solve_and_submit(ws):
    s = _session(ws)
    _measure_all(s)
    out = s.execute("solve", {"qid": 101, "spec": _spec(Q_SIZE, Q_SPEED, 0.9),
                              "tracks": [_tr("prior", ["T1"]), _tr("target", ["S1"])]})
    assert not out.is_error, out.content[0]["text"]
    assert re.search(r"geometry answer ([\d.]+) cm", out.content[0]["text"])
    assert float(re.search(r"geometry answer ([\d.]+) cm", out.content[0]["text"]).group(1)) == pytest.approx(20, rel=0.05)
    assert "scale_m_per_px" in out.content[0]["text"]
    # manual obs combine with refs; unknown refs are errors
    assert s.execute("solve", {"qid": 102, "spec": _spec(Q_SPEED, Q_SIZE, 0.2),
                               "tracks": [_tr("prior", ["S7"]), _tr("target", ["T1"])]}).is_error
    out = s.execute("solve", {"qid": 102, "spec": _spec(Q_SPEED, {**Q_SIZE, "unit": ""}, 0.2),
                              "tracks": [_tr("prior", obs=[{"frame": 4, "point": None, "box": None,
                                                            "extent": [[ball_x(4) - 10, Y], [ball_x(4) + 10, Y]]}]),
                                         _tr("target", ["T1"])]})
    assert float(re.search(r"geometry answer ([\d.]+) m/s", out.content[0]["text"]).group(1)) == pytest.approx(0.9, rel=0.05)
    assert s.execute("solve", {"qid": 999, "spec": _spec(Q_SIZE, Q_SPEED, 0.9), "tracks": []}).is_error
    # submit: one answer from its last solve, one missing -> not done; then the other
    out = s.execute("submit", {"answers": [{"qid": 101, "use_last_solve": True, "direct_answer": 19.5,
                                            "confidence": 0.8, "derivation": "20 px"}]})
    assert not out.is_error and not s.done and "Still missing: [102]" in out.content[0]["text"]
    out = s.execute("submit", {"answers": [{"qid": 102, "use_last_solve": True, "direct_answer": 0.88,
                                            "confidence": 0.8, "derivation": "90 px/s"}]})
    assert s.done and "complete" in out.content[0]["text"]
    parsed, fallback, missing = s.final_parsed()
    assert [q["qid"] for q in parsed["questions"]] == [101, 102] and not fallback and not missing
    assert parsed["questions"][0]["direct_answer"] == 19.5 and parsed["questions"][0]["tracks"][0]["obs"]
    # the record contract: qp.claude_annotate reads it back unchanged
    from qp import claude_annotate as ca
    anns = ca.to_annotations(parsed, s.meta())
    assert set(anns) == {101, 102} and len(anns[101].tracks[0].obs) == N


# --------------------------------------------------------------------------- loop with a fake client


def _usage(i=5000, o=3000, cw=0, cr=0):
    return SimpleNamespace(input_tokens=i, output_tokens=o, cache_creation_input_tokens=cw, cache_read_input_tokens=cr,
                           cache_creation=None)


def _msg(n, blocks, stop="tool_use", usage=None):
    return SimpleNamespace(id=f"msg_{n}", stop_reason=stop, stop_details=None, content=blocks,
                           usage=usage or _usage(cr=1000 * n))


def _use(n, k, name, inp):
    return SimpleNamespace(type="tool_use", id=f"toolu_{n}_{k}", name=name, input=inp)


def _think(n):
    return SimpleNamespace(type="thinking", thinking=f"plan {n}", signature=f"sig{n}")


def happy_script(n, params):
    """Turn 1: look + track + segment; turn 2: solve both; turn 3: submit."""
    if n == 1:
        pad = [ball_box(10)[0] - 2, ball_box(10)[1] - 2, ball_box(10)[2] + 2, ball_box(10)[3] + 2]
        return _msg(n, [_think(n), _use(n, 0, "get_frames", {"frames": [0, 29], "region": [40, 90, 160, 150]}),
                        _use(n, 1, "track", {"object": "ball", "anchors": [{"frame": 10, "box": ball_box(10)}]}),
                        _use(n, 2, "segment", {"object": "ball", "frame": 10, "box": pad, "measure": "diameter"})])
    if n == 2:
        return _msg(n, [_think(n), SimpleNamespace(type="text", text="solving"),
                        _use(n, 0, "solve", {"qid": 101, "spec": _spec(Q_SIZE, Q_SPEED, 0.9),
                                             "tracks": [_tr("prior", ["T1"]), _tr("target", ["S1"])]}),
                        _use(n, 1, "solve", {"qid": 102, "spec": _spec(Q_SPEED, {**Q_SIZE, "unit": ""}, 0.2),
                                             "tracks": [_tr("prior", ["S1"]), _tr("target", ["T1"])]})])
    return _msg(n, [_think(n), _use(n, 0, "submit", {"answers": [
        {"qid": 101, "use_last_solve": True, "direct_answer": 20.5, "confidence": 0.9, "derivation": "d"},
        {"qid": 102, "use_last_solve": True, "direct_answer": 0.91, "confidence": 0.9, "derivation": "d"}]})])


class FakeStream:
    def __init__(self, msg):
        self.msg, self.request_id = msg, f"req_{msg.id}"

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get_final_message(self):
        return self.msg


class FakeClient:
    def __init__(self, script=happy_script):
        self.script, self.requests = script, []
        self.messages = SimpleNamespace(stream=self._stream)

    def _stream(self, **params):
        self.requests.append(copy.deepcopy(params))
        return FakeStream(self.script(len(self.requests), params))


def _cfg(**kw):
    return ag.AgentConfig(**{"run": "t", "split": "val", **kw})


def test_loop_append_only_pairing_and_params(ws):
    client = FakeClient()
    s = _session(ws)
    rec = ag.run_video(client, s, _cfg(effort="medium"), log=lambda *a: None)
    reqs = client.requests
    assert len(reqs) == 3 and rec["status"] == "ok" and rec["stop"] == "submitted" and rec["turns"] == 3
    tools = ag.tool_definitions(True)
    assert [t["name"] for t in tools] == sorted(t["name"] for t in tools)
    assert {t["name"] for t in tools if t.get("strict")} == set(ag.STRICT_TOOLS)
    for r in reqs:
        assert r["model"] == "claude-opus-5-5" and r["tools"] == tools and r["system"] == reqs[0]["system"]
        assert r["system"][-1]["cache_control"] == {"type": "ephemeral"} and r["cache_control"] == {"type": "ephemeral"}
        assert r["output_config"] == {"effort": "medium"} and r["thinking"]["type"] == "adaptive"
        assert "tool_choice" not in r and r["max_tokens"] <= ag.TURN_MAX_TOKENS
    # append-only: each request's messages are a prefix of the next one's, followed by the assistant
    # content returned unchanged (thinking blocks with signatures) and then the tool results
    for k in range(len(reqs) - 1):
        a, b = ag._plain(reqs[k]["messages"]), ag._plain(reqs[k + 1]["messages"])
        assert b[:len(a)] == a and len(b) == len(a) + 2
        assistant = b[len(a)]
        assert assistant["role"] == "assistant" and assistant["content"] == ag._plain(happy_script(k + 1, None).content)
        user = b[len(a) + 1]
        ids = [blk["id"] for blk in assistant["content"] if blk["type"] == "tool_use"]
        results = [blk for blk in user["content"] if blk["type"] == "tool_result"]
        assert [r["tool_use_id"] for r in results] == ids                         # paired, in order
        assert user["content"] == results           # results only: no status line while no limit is near
        assert not any(r.get("is_error") for r in results)
    first = reqs[0]["messages"]
    assert len(first) == 1 and sum(b["type"] == "image" for b in first[0]["content"]) == ag.OVERVIEW_FRAMES
    turn1 = reqs[1]["messages"][2]["content"]
    assert any(c["type"] == "image" for r in turn1 if r["type"] == "tool_result" for c in r["content"])
    # answers, ledger, record shape
    assert rec["final_geometry"][101]["geo"] == pytest.approx(20, rel=0.05)
    assert rec["final_geometry"][102]["geo"] == pytest.approx(0.9, rel=0.05)
    led = budget.entries()
    assert [e["turn"] for e in led] == [1, 2, 3] and all(e["run"] == "t" and e["video_id"] == "vid_a" for e in led)
    assert rec["usd"] == pytest.approx(sum(e["usd"] for e in led))
    assert rec["usage"]["cache_read_input_tokens"] == 6000 and rec["tool_counts"] == {
        "get_frames": 1, "track": 1, "segment": 1, "solve": 2, "submit": 1}
    dumped = json.dumps(rec, default=str)
    assert '"data"' not in dumped and "signature" not in dumped and '"omitted": true' in dumped


def test_turn_cap_falls_back_to_last_solve(ws):
    def script(n, params):
        if n == 1:
            return happy_script(1, params)
        return _msg(n, [_use(n, 0, "solve", {"qid": 101, "spec": _spec(Q_SIZE, Q_SPEED, 0.9),
                                             "tracks": [_tr("prior", ["T1"]), _tr("target", ["S1"])]})])
    client = FakeClient(script)
    rec = ag.run_video(client, _session(ws), _cfg(max_turns=3), log=lambda *a: None)
    assert len(client.requests) == 3 and rec["stop"] == "max_turns" and rec["status"] == "partial"
    assert rec["fallback_qids"] == [101] and rec["missing_qids"] == [102]
    q = rec["parsed"]["questions"]
    assert [x["qid"] for x in q] == [101] and q[0]["direct_answer"] is None
    last_status = client.requests[2]["messages"][-1]["content"][-1]["text"]
    assert "last response" in last_status and "submit" in last_status
    wrap = client.requests[1]["messages"][-1]["content"][-1]["text"]
    assert "Wrap up now" in wrap                                          # 2 turns left


def test_per_video_budget_shrinks_max_tokens_and_stops(ws):
    client = FakeClient(lambda n, p: happy_script(1, p) if n == 1 else _msg(n, [_use(n, 0, "get_frames", {"frames": [n]})]))
    cfg = _cfg(max_usd=0.4)
    rec = ag.run_video(client, _session(ws), cfg, log=lambda *a: None)
    assert rec["stop"] == "budget_video" and rec["usd"] <= cfg.max_usd
    mts = [r["max_tokens"] for r in client.requests]
    assert mts[0] < ag.TURN_MAX_TOKENS and all(a >= b for a, b in zip(mts, mts[1:])) and mts[-1] >= ag.MIN_TURN_TOKENS
    assert rec["status"] == "failed" and rec["parsed"] == {"questions": []}
    # output-token cap
    client = FakeClient(lambda n, p: _msg(n, [_use(n, 0, "get_frames", {"frames": [0]})], usage=_usage(o=9000)))
    rec = ag.run_video(client, _session(ws), _cfg(max_output_tokens=30000), log=lambda *a: None)
    assert rec["stop"] == "budget_video" and rec["usage"]["output_tokens"] <= 30000


def test_global_budget_stops_before_the_request(ws, monkeypatch):
    monkeypatch.setenv("QP_BUDGET_USD", "0.05")
    client = FakeClient()
    rec = ag.run_video(client, _session(ws), _cfg(), log=lambda *a: None)
    assert not client.requests and rec["stop"] == "budget_global" and not budget.entries()


def test_text_only_reply_is_nudged_and_tool_errors_return_is_error(ws):
    def script(n, params):
        if n == 1:
            return _msg(n, [SimpleNamespace(type="text", text="I think the answer is 20.")], stop="end_turn")
        if n == 2:
            return _msg(n, [_use(n, 0, "get_frames", {"frames": [500]}), _use(n, 1, "nope", {})])
        if n == 3:
            return happy_script(1, params)
        return happy_script(n - 2, params)
    client = FakeClient(script)
    rec = ag.run_video(client, _session(ws), _cfg(), log=lambda *a: None)
    assert rec["status"] == "ok" and len(client.requests) == 5
    nudge = client.requests[1]["messages"][-1]
    assert nudge["role"] == "user" and "did not call a tool" in nudge["content"][0]["text"]
    res = [b for b in client.requests[2]["messages"][-1]["content"] if b["type"] == "tool_result"]
    assert [r.get("is_error") for r in res] == [True, True]
    assert sum(c["is_error"] for c in rec["tool_calls"]) == 2


def test_max_tokens_cut_tool_use_is_not_executed(ws):
    def script(n, params):
        if n == 1:
            return _msg(n, [_use(n, 0, "track", {"object": "ball", "anchors": []})], stop="max_tokens")
        return happy_script(n - 1, params)
    client = FakeClient(script)
    s = _session(ws)
    rec = ag.run_video(client, s, _cfg(), log=lambda *a: None)
    first = [b for b in client.requests[1]["messages"][-1]["content"] if b["type"] == "tool_result"]
    assert first[0]["is_error"] and "max_tokens" in first[0]["content"][0]["text"]
    assert rec["status"] == "ok"


def _unions(schema) -> int:
    """Parameters with a union type (anyOf / type arrays) in a JSON schema, as the strict-grammar limit counts."""
    if isinstance(schema, dict):
        own = int("anyOf" in schema or isinstance(schema.get("type"), list))
        return own + sum(_unions(v) for k, v in schema.items() if k != "anyOf") + \
            sum(_unions(v) for v in schema.get("anyOf", []))
    if isinstance(schema, list):
        return sum(_unions(v) for v in schema)
    return 0


def test_strict_tools_stay_within_grammar_limits():
    strict = [t for t in ag.tool_definitions(True) if t.get("strict")]
    assert sum(_unions(t["input_schema"]) for t in strict) <= 16
    for t in strict:   # strict schemas: every object closed
        stack = [t["input_schema"]]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                if x.get("type") == "object":
                    assert x.get("additionalProperties") is False
                stack += list(x.values())
            elif isinstance(x, list):
                stack += x


def test_estimate_video_usd_scales_with_effort():
    lo = ag.estimate_video_usd(5000, 4, "low")
    hi = ag.estimate_video_usd(5000, 4, "high")
    assert 0 < lo < hi < 5


# --------------------------------------------------------------------------- script


def _load_script():
    spec = importlib.util.spec_from_file_location("run_claude_agent", ROOT / "scripts" / "run_claude_agent.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def rca(ws, monkeypatch):
    mod = _load_script()
    monkeypatch.setattr(mod, "load_split", lambda split: ws.df.copy())
    monkeypatch.setattr(mod.rc, "ROOT", ws.root)       # no .env from the repo
    return mod


def _argv(ws, *extra):
    return ["--split", "val", "--name", "ag", "--out-root", str(ws.root / "runs"), "--workers", "1", *extra]


def test_script_records_csv_ledger_and_resume(ws, rca):
    client = FakeClient()
    res = rca.main(_argv(ws, "--effort", "medium"), client=client)
    assert len(client.requests) == 3
    rec_path = ws.root / "runs" / "ag" / "val" / "records" / "vid_a.json"
    rec = json.loads(rec_path.read_text())
    assert rec["status"] == "ok" and rec["meta"]["image_size"] == [W, H] and rec["config"]["agent_version"] == ag.AGENT_VERSION
    assert list(res.columns) == ["id", "parsed_value", "geo_value", "direct_value", "method", "flags", "geo_method"]
    r = res.set_index("id")
    assert r.geo_value[101] == pytest.approx(20, rel=0.05) and r.geo_value[102] == pytest.approx(0.9, rel=0.05)
    assert r.direct_value[101] == 20.5 and r.parsed_value[101] == pytest.approx(r.geo_value[101])
    assert (ws.root / "runs" / "ag" / "val.csv").exists()
    assert list((ws.root / "runs" / "ag" / "val" / "images" / "vid_a").glob("*.jpg"))
    assert len(budget.entries()) == 3
    # rerun: cached, nothing sent, same answers
    client2 = FakeClient()
    res2 = rca.main(_argv(ws, "--effort", "medium"), client=client2)
    assert not client2.requests and len(budget.entries()) == 3
    assert res2.set_index("id").parsed_value.to_dict() == pytest.approx(r.parsed_value.to_dict())
    # other settings: a fully cached run re-scores (nothing sent); a run with videos to send refuses to mix
    client3 = FakeClient()
    rca.main(_argv(ws, "--effort", "high"), client=client3)
    assert not client3.requests
    two = pd.concat([ws.df, ws.df.assign(video_id="vid_b", qid=[201, 202])], ignore_index=True)
    rca.load_split = lambda split: two.copy()
    with pytest.raises(SystemExit, match="other settings"):
        rca.main(_argv(ws, "--effort", "high"), client=FakeClient())


def test_script_dry_run_and_budget_refusal(ws, rca, monkeypatch):
    client = FakeClient()
    assert rca.main(_argv(ws, "--dry-run"), client=client) is None and not client.requests
    monkeypatch.setenv("QP_BUDGET_USD", "0.01")
    res = rca.main(_argv(ws), client=client)
    assert not client.requests and res.parsed_value.isna().all()
    monkeypatch.setenv("QP_BUDGET_USD", "50")
    rca.main(_argv(ws, "--max-usd", "0.01"), client=client)
    assert not client.requests


# --------------------------------------------------------------------------- regression tests (review findings)


def _still_video(path: Path, draw, n: int = 4, bg=(50, 50, 50), noise: float = 3.0, seed: int = 2) -> Path:
    """A static mp4v clip: noisy background + draw(img) (antialiased shapes in continuous coords)."""
    rng = np.random.default_rng(seed)
    base = np.clip(rng.normal(0, noise, (H, W, 3)) + np.array(bg, float), 0, 255).astype(np.uint8)
    draw(base)
    vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W, H))
    for _ in range(n):
        vw.write(base)
    vw.release()
    return path


def _one_q(video: Path, vid: str = "v") -> pd.DataFrame:
    return pd.DataFrame([{"qid": 1, "video_id": vid, "video_path": str(video), "video_type": "V2SC", "fps": FPS,
                          "inference_type": "SS", "question": "q", "prior": "p = 1 m", "depth_info": "",
                          "video_source": "simulation", "category": "S2", "target_unit": "m", "answer": 1.0}])


def _poly(img, pts, col):
    cv2.fillPoly(img, [np.round((np.asarray(pts, np.float32) - 0.5) * 16).astype(np.int32)], col, cv2.LINE_AA, 4)


TRAPEZOID = np.array([[137, 80], [182, 80], [189, 129], [130, 129]], np.int32)   # pixels: 60 wide at the bottom


def test_segment_refines_where_the_extent_is_reached_not_on_the_centroid_line(tmp_path):
    """A trapezoid 60 px wide at the bottom, 46 px at the top: its horizontal / long extent is reached at the
    bottom corners, not on the centroid's row (a ~53.5 px chord there). The old refinement snapped along the
    centroid row to the search window's edge (57.9 px for the reviewer's version of this shape)."""
    v = _still_video(tmp_path / "trap.mp4", lambda im: cv2.fillPoly(im, [TRAPEZOID], (230, 230, 230), cv2.LINE_8))
    s = ag.AgentSession(_one_q(v))
    for meas, true in (("horizontal", 60.0), ("long", 60.0), ("vertical", 50.0)):
        out = s.execute("segment", {"object": "block", "frame": 1, "box": [127, 77, 193, 133], "measure": meas})
        assert not out.is_error, out.content[0]["text"]
        e = s.meas[f"S{len(s.meas)}"].obs[0]["extent"]
        assert ag._len(e) == pytest.approx(true, abs=0.4), out.content[0]["text"]
        assert "edge-refined" in out.content[0]["text"] and "kept at the mask" not in out.content[0]["text"]


def test_snap_never_lands_on_the_window_boundary(tmp_path):
    """An edge farther than the search window is not snapped to the window's boundary: the end stays."""
    v = _still_video(tmp_path / "sq.mp4", lambda im: cv2.rectangle(im, (100, 100), (139, 139), (230, 230, 230), -1))
    img = ag.AgentSession(_one_q(v)).store.get([1])[1]                  # edges at x = 100 and 140
    ext, info = ag.snap_ends(img, [[96.5, 120.0], [143.5, 120.0]], 2.5)     # edges 3.5 px away: beyond the window
    assert info["end0"] == "window" and info["end1"] == "window" and ext == [[96.5, 120.0], [143.5, 120.0]]
    ext, info = ag.snap_ends(img, [[98.5, 120.0], [143.5, 120.0]], 2.5)     # one end in reach: applied alone
    assert ext[0][0] == pytest.approx(100.0, abs=0.3) and info["end1"] == "window" and ext[1][0] == 143.5
    ext, info = ag.snap_ends(img, [[60.0, 30.0], [80.0, 30.0]], 3.0)        # flat background: no edge
    assert info["end0"] == info["end1"] == "weak"


@pytest.mark.parametrize("side,col,bg", [(12, (235, 235, 235), (40, 40, 40)), (12, (40, 40, 220), (90, 90, 90)),
                                         (20, (40, 40, 220), (90, 90, 90))])
def test_segment_refines_small_objects(tmp_path, side, col, bg):
    """A 12 px square: the mask bleeds ~1.2 px per side (14.5 px); the old relative guard (15%) threw the
    correct refinement away and returned +21%."""
    def draw(im):
        cv2.rectangle(im, (200, 100), (200 + side - 1, 100 + side - 1), col, -1)
    v = _still_video(tmp_path / "small.mp4", draw, bg=bg, noise=4.0, seed=1)
    s = ag.AgentSession(_one_q(v))
    for meas in ("horizontal", "vertical"):
        out = s.execute("segment", {"object": "square", "frame": 2, "box": [197, 97, 203 + side, 103 + side],
                                    "measure": meas})
        L = ag._len(s.meas[f"S{len(s.meas)}"].obs[0]["extent"])
        assert L == pytest.approx(side, abs=0.4), out.content[0]["text"]


def test_segment_edges_method_keeps_an_end_without_edge(ws):
    s = _session(ws)
    out = s.execute("segment", {"object": "bar", "frame": 3, "measure": "long", "method": "edges",
                                "extent": [[201.5, 50], [290.0, 50]]})     # end 2 is 10 px past the bar's end
    e = s.meas["S1"].obs[0]["extent"]
    assert e[0][0] == pytest.approx(200, abs=0.5) and e[1][0] == 290.0
    assert "end 2 kept where you put it" in out.content[0]["text"]


def _stub_pass(truth, k_drift: int, jump=(40.0, 0.0)):
    """A fake track_pass: follows truth(f); a forward pass from the truth branch jumps onto truth + jump after
    frame k_drift; a pass started on the jumped branch stays on it (like a template locked on the wrong thing)."""
    jump = np.asarray(jump, float)

    def passer(imgs, f_a, f_b, c_a, tsize, guide=None):
        c_a = np.asarray(c_a, float) + 0.5               # work == original px here (S = 1)
        drifted = np.linalg.norm(c_a - truth(f_a)) > 0.5 * np.linalg.norm(jump)
        step = 1 if f_b >= f_a else -1
        out = {}
        for f in range(f_a, f_b + step, step):
            on_jump = drifted or (step > 0 and f > k_drift)
            out[f] = (truth(f) + (jump if on_jump else 0) - 0.5, 0.9, 1.0)
        return out
    return passer


def test_track_drops_frames_where_the_tracker_drifted(monkeypatch):
    truth = lambda f: np.array([50.0 + 2 * f, 100.0])                     # noqa: E731
    monkeypatch.setattr(ag, "ncc_pass", _stub_pass(truth, k_drift=17))
    frames = {f: np.zeros((H, W, 3), np.uint8) for f in range(40)}
    box = lambda f: [*(truth(f) - 10), *(truth(f) + 10)]                  # noqa: E731
    path, info = ag.track_object(frames, 1.0, (W, H), [(5, box(5))], 0, 39, FPS, use_dense=False)
    assert sorted(path) == list(range(0, 18))                            # up to the last frame before the jump
    assert info["dropped"] == {f: "drift" for f in range(18, 40)} and not info["lost"]
    assert all(np.allclose(path[f]["point"], truth(f)) for f in path)
    assert info["fb_max_px"] is not None and info["fb_max_px"] <= info["tolerance_px"]


def test_track_session_reports_dropped_frames_and_solve_warns(ws, monkeypatch):
    truth = lambda f: np.array([ball_x(f), Y])                            # noqa: E731
    monkeypatch.setattr(ag, "ncc_pass", _stub_pass(truth, k_drift=20))
    s = _session(ws, use_dense=False)
    out = s.execute("track", {"object": "ball", "anchors": [{"frame": 10, "box": ball_box(10)}], "overlay": False})
    text = out.content[0]["text"]
    assert "DROPPED 9 frames" in text and "21..29" in text and "drifted" in text
    assert [o["frame"] for o in s.meas["T1"].obs] == list(range(0, 21))
    s.execute("segment", {"object": "ball", "frame": 10, "box": [b + d for b, d in zip(ball_box(10), (-2, -2, 2, 2))],
                          "measure": "diameter"})
    out = s.execute("solve", {"qid": 102, "spec": _spec(Q_SPEED, {**Q_SIZE, "unit": ""}, 0.2),
                              "tracks": [_tr("prior", ["S1"]), _tr("target", ["T1"])]})
    assert "warning: T1 (ball) has no frames 21..29" in out.content[0]["text"]


@pytest.mark.parametrize("use_dense", [False, True])
def test_chained_passes_have_no_step_at_inconsistent_anchors(ws, monkeypatch, use_dense):
    """Without dense_motion (fallback tracker, or dense_motion failing), each pass's mismatch at the next
    anchor is spread over its frames: no step at the anchor. The old code put the next anchor's raw centre
    there (a 6.2 px step for a 3 px inconsistency)."""
    dt = ag._dense_track()
    if use_dense:
        if dt is None:
            pytest.skip("qp.dense_track unavailable")
        monkeypatch.setattr(dt, "dense_motion", lambda *a, **k: (None, {"why": "cover"}))
    s = _session(ws, use_dense=use_dense)
    off = [b + d for b, d in zip(ball_box(20), (3.0, 0.0, 3.0, 0.0))]
    s.execute("track", {"object": "ball", "overlay": False,
                        "anchors": [{"frame": 8, "box": ball_box(8)}, {"frame": 20, "box": off}]})
    m = s.meas["T1"]
    assert m.info["between_anchors"] == "chained_passes" and m.info["segments"] == ["forward"]
    pts = {o["frame"]: np.array(o["point"]) for o in m.obs}
    assert sorted(pts) == list(range(N))
    steps = [pts[f + 1][0] - pts[f][0] for f in range(N - 1)]
    assert max(abs(st - VX) for st in steps) < 0.8, steps                 # 3 px over 12 frames: +0.25 / frame
    assert np.allclose(pts[20], ag._box_c(off), atol=0.01)               # continuous at the anchor ...
    assert pts[21][0] - pts[20][0] == pytest.approx(VX, abs=0.8)          # ... and after it


def test_chained_passes_drop_frames_between_anchors_that_do_not_connect(ws):
    s = _session(ws, use_dense=False)
    off = [b + d for b, d in zip(ball_box(20), (12.0, 0.0, 12.0, 0.0))]  # 12 px: beyond the 5 px tolerance
    out = s.execute("track", {"object": "ball", "overlay": False,
                              "anchors": [{"frame": 8, "box": ball_box(8)}, {"frame": 20, "box": off}]})
    m = s.meas["T1"]
    assert m.info["segments"] == ["dropped"] and set(m.info["dropped"]) == set(range(9, 20))
    assert "neither a forward nor a backward pass connects" in out.content[0]["text"]
    pts = {o["frame"]: np.array(o["point"]) for o in m.obs}
    assert 8 in pts and 20 in pts and not set(range(9, 20)) & set(pts)
    steps = [pts[f + 1][0] - pts[f][0] for f in sorted(pts) if f + 1 in pts]
    assert max(abs(st - VX) for st in steps) < 0.8                       # no jump anywhere


def make_frozen_video(path: Path) -> Path:
    """The test ball video with frame 0 a copy of frame 1 (a renderer artifact of some simulations); a flat
    background, so the codec reproduces the repeated frame exactly."""
    bg = np.full((H, W, 3), 90, np.uint8)
    vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W, H))
    for f in [1] + list(range(1, N)):
        img = bg.copy()
        c = (int(round((ball_x(f) - 0.5) * 16)), int(round((Y - 0.5) * 16)))
        cv2.circle(img, c, int(DIAM / 2 * 16), (40, 40, 220), -1, cv2.LINE_AA, 4)
        cv2.rectangle(img, (10 + 4 * f, 160), (110 + 4 * f, 230), (250, 250, 250), -1)   # big mover: "moving"
        vw.write(img)
    vw.release()
    return path


def test_frozen_first_frame(tmp_path):
    video = make_frozen_video(tmp_path / "frozen.mp4")
    s = ag.AgentSession(questions(video))
    assert s.frozen0 and s.first == 1
    meta = s.meta()
    assert meta["frozen_first_frame"] and meta["frames"][0] == 1
    text = "\n".join(b["text"] for b in s.initial_content() if b["type"] == "text")
    assert "Frame 0 repeats frame 1" in text and "Frame 0 (" not in text
    s.execute("track", {"object": "ball", "anchors": [{"frame": 0, "box": ball_box(1)}], "overlay": False})
    fr = [o["frame"] for o in s.meas["T1"].obs]
    assert fr == list(range(1, N))                                       # default range starts at frame 1
    obs0 = {"frame": 0, "point": [ball_x(1), Y], "extent": None, "box": None}
    tr = s.resolve_tracks([_tr("target", obs=[obs0])])
    assert [o["frame"] for o in tr[0]["obs"]] == [1]                     # frame 0 counts as frame 1 ...
    tr = s.resolve_tracks([_tr("target", ["T1"], obs=[obs0])])
    assert [o["frame"] for o in tr[0]["obs"]] == fr                      # ... unless frame 1 is there already
    assert not ag.AgentSession(questions(make_video_path(tmp_path))).frozen0


def make_video_path(tmp_path: Path) -> Path:
    p = tmp_path / "moving.mp4"
    make_video(p)
    return p


def test_one_malformed_answer_does_not_void_the_others(ws):
    s = _session(ws)
    _measure_all(s)
    good = {"qid": 101, "use_last_solve": False, "spec": _spec(Q_SIZE, Q_SPEED, 0.9),
            "tracks": [_tr("prior", ["T1"]), _tr("target", ["S1"])], "direct_answer": 20, "confidence": 0.5,
            "derivation": ""}
    bad = {"qid": 102, "use_last_solve": False, "spec": {"target": "speed of ball", "prior": "diameter", "notes": ""},
           "tracks": [_tr("prior", ["S1"])], "direct_answer": 0.9, "confidence": 0.5, "derivation": ""}
    out = s.execute("submit", {"answers": [good, bad]})
    assert out.is_error and sorted(s.submitted) == [101] and not s.done
    assert "spec.target must be an object" in out.content[0]["text"]
    for spec, msg in [({"target": "speed", "prior": {}, "notes": ""}, "spec.target must be an object"),
                      (_spec({**Q_SPEED, "objects": "ball"}, Q_SIZE, 0.2), "objects must be a list"),
                      (_spec({**Q_SPEED, "window": [1]}, Q_SIZE, 0.2), "window must be"),
                      (_spec({**Q_SPEED, "time": "end"}, Q_SIZE, 0.2), "time has the wrong type")]:
        out = s.execute("solve", {"qid": 102, "spec": spec, "tracks": []})
        assert out.is_error and msg in out.content[0]["text"] and "Internal error" not in out.content[0]["text"]
    for obs, msg in [({"frame": 3, "point": [1, 2, 3], "extent": None, "box": None}, "point must be"),
                     ({"frame": 3, "point": None, "extent": [[1, 2]], "box": None}, "extent must be"),
                     ({"frame": 3, "point": None, "extent": None, "box": "x"}, "box must be"),
                     ({"frame": 3, "point": None, "extent": None, "box": None}, "no point, extent or box")]:
        out = s.execute("solve", {"qid": 102, "spec": _spec(Q_SPEED, Q_SIZE, 0.2), "tracks": [_tr("target", obs=[obs])]})
        assert out.is_error and msg in out.content[0]["text"], out.content[0]["text"]


def test_per_video_cap_holds_when_every_turn_misses_the_cache(ws):
    def script(n, params):   # growing context, every turn a cache miss (TTL expired / lookback miss)
        return _msg(n, [_use(n, 0, "get_frames", {"frames": [0]})],
                    usage=_usage(i=0, o=min(2000, params["max_tokens"]), cw=12000 + 30000 * (n - 1), cr=0))
    rec = ag.run_video(FakeClient(script), _session(ws), _cfg(max_usd=1.0), log=lambda *a: None)
    assert rec["stop"] == "budget_video" and rec["usd"] <= 1.0


class FailingStream(FakeStream):
    """Fails in get_final_message: after message_start (a snapshot with usage) or before it."""

    def __init__(self, msg, started: bool, exc):
        super().__init__(msg)
        self.started, self.exc = started, exc

    @property
    def current_message_snapshot(self):
        if not self.started:
            raise AssertionError("no message_start yet")
        return SimpleNamespace(usage=_usage(i=7000, o=1, cw=0, cr=0))

    def get_final_message(self):
        raise self.exc


class APIConnectionError(Exception):
    pass


def test_mid_stream_failure_is_billed_then_retried(ws, monkeypatch):
    monkeypatch.setattr(ag, "RETRY_WAIT", 0.0)
    calls = []

    class Client(FakeClient):
        def _stream(self, **params):
            calls.append(1)
            if len(calls) == 2:      # turn 2, attempt 1: dies mid-stream (billed)
                return FailingStream(_msg(99, []), True, APIConnectionError("connection reset"))
            if len(calls) == 3:      # turn 2, attempt 2: dies before the response (not billed)
                return FailingStream(_msg(98, []), False, APIConnectionError("refused"))
            self.requests.append(copy.deepcopy(params))
            return FakeStream(happy_script(len(self.requests), params))
    client = Client()
    rec = ag.run_video(client, _session(ws), _cfg(), log=lambda *a: None)
    assert rec["status"] == "ok" and rec["turns"] == 3 and len(calls) == 5
    led = budget.entries()
    partial = [e for e in led if e.get("partial")]
    assert len(led) == 4 and len(partial) == 1 and partial[0]["turn"] == 2
    assert partial[0]["output_tokens"] == rec["requests"][1]["max_tokens"]          # worst case: output unknown
    assert rec["usd"] == pytest.approx(sum(e["usd"] for e in led))
    assert [r.get("partial", False) for r in rec["requests"]] == [False, True, False, False]
    # a non-transient failure is not retried
    calls.clear()

    class Bad(FakeClient):
        def _stream(self, **params):
            calls.append(1)
            return FailingStream(_msg(97, []), True, ValueError("bad request"))
    rec = ag.run_video(Bad(), _session(ws), _cfg(), log=lambda *a: None)
    assert rec["stop"] == "api_error" and len(calls) == 1 and rec["usd"] > 0


def test_stop_event_and_checkpoints(ws):
    import threading
    stop = threading.Event()
    seen = []

    class Client(FakeClient):
        def _stream(self, **params):
            if len(self.requests) == 1:
                stop.set()           # Ctrl-C while the second request is in flight
            return super()._stream(**params)
    client = Client()
    rec = ag.run_video(client, _session(ws), _cfg(), log=lambda *a: None, stop_event=stop,
                       checkpoint=lambda r: seen.append((r["stop"], r["turns"])))
    assert len(client.requests) == 2 and rec["stop"] == "interrupted" and rec["turns"] == 2
    assert rec["status"] == "partial" and rec["fallback_qids"] == [101, 102]   # scored from the last solves
    assert seen == [("in_progress", 1), ("in_progress", 2)]
    stop.set()
    client = FakeClient()
    rec = ag.run_video(client, _session(ws), _cfg(), log=lambda *a: None, stop_event=stop)
    assert not client.requests and rec["stop"] == "interrupted" and rec["status"] == "failed"


def test_status_line_only_late_unless_always(ws):
    def script(n, params):
        return _msg(n, [_use(n, 0, "get_frames", {"frames": [n % N]})])
    client = FakeClient(script)
    ag.run_video(client, _session(ws), _cfg(max_turns=10), log=lambda *a: None)
    status = ["[status]" in json.dumps(ag._plain(r["messages"][-1]["content"])) for r in client.requests[1:]]
    assert status == [False] * 5 + [True] * 4                            # from 60% of the turns on
    first = json.dumps(ag._plain(client.requests[0]["messages"][0]["content"]))
    assert "Limits for this video" not in first
    client = FakeClient(script)
    ag.run_video(client, _session(ws), _cfg(max_turns=10, status="always"), log=lambda *a: None)
    assert all("[status]" in json.dumps(ag._plain(r["messages"][-1]["content"])) for r in client.requests[1:])
    assert "Limits for this video" in json.dumps(ag._plain(client.requests[0]["messages"][0]["content"]))


def test_task_budget_minimum_and_constant_total(ws, rca):
    with pytest.raises(SystemExit):
        rca.parse_args(_argv(ws, "--task-budget", "5000"))
    assert rca.parse_args(_argv(ws, "--task-budget", "20000")).task_budget == 20000
    with pytest.raises(ValueError, match="at least"):
        ag.run_video(FakeClient(), _session(ws), _cfg(task_budget=5000), log=lambda *a: None)
    client = FakeClient()
    client.beta = SimpleNamespace(messages=SimpleNamespace(stream=client._stream))
    ag.run_video(client, _session(ws), _cfg(task_budget=64000), log=lambda *a: None)
    assert len(client.requests) == 3
    for r in client.requests:
        assert r["betas"] == ["task-budgets-2026-03-13"]
        assert r["output_config"]["task_budget"] == {"type": "tokens", "total": 64000}


def test_todo_videos_retry_flags(rca):
    groups = {v: None for v in ("new", "ok", "partial", "failed", "refusal", "intr_failed", "intr_partial", "killed")}
    records = {"ok": {"status": "ok", "stop": "submitted"}, "partial": {"status": "partial", "stop": "max_turns"},
               "failed": {"status": "failed", "stop": "api_error"}, "refusal": {"status": "refusal", "stop": "refusal"},
               "intr_failed": {"status": "failed", "stop": "interrupted"},
               "intr_partial": {"status": "partial", "stop": "interrupted"},
               "killed": {"status": "failed", "stop": "in_progress"}}
    assert rca.todo_videos(groups, records) == ["new", "intr_failed", "killed"]
    assert rca.todo_videos(groups, records, retry_failed=True) == ["new", "failed", "refusal", "intr_failed", "killed"]
    assert rca.todo_videos(groups, records, retry_partial=True) == ["new", "partial", "intr_failed", "intr_partial",
                                                                    "killed"]
    assert "1 ok, 2 partial" in rca.record_counts(groups, records)


def _multi(ws, k: int) -> pd.DataFrame:
    return pd.concat([ws.df.assign(video_id=f"vid_{i}", qid=[1000 + 10 * i, 1001 + 10 * i]) for i in range(k)],
                     ignore_index=True)


def test_script_ctrl_c_cancels_queued_videos_and_saves_in_flight(ws, rca, monkeypatch):
    df = _multi(ws, 4)
    rca.load_split = lambda split: df.copy()

    def interrupted(fs):     # Ctrl-C reaches the main thread while the first video is running
        raise KeyboardInterrupt
        yield  # makes this a generator

    monkeypatch.setattr(rca, "as_completed", interrupted)

    class Slow(FakeClient):
        def _stream(self, **params):
            import time
            time.sleep(0.2)
            n = len(params["messages"]) // 2 + 1
            self.requests.append(1)
            return FakeStream(happy_script(n, params))
    client = Slow()
    with pytest.raises(SystemExit) as e:
        rca.main(_argv(ws), client=client)
    assert e.value.code == 130
    assert len(client.requests) <= 2 and len(budget.entries()) == len(client.requests)
    recs = sorted(p.name for p in (ws.root / "runs" / "ag" / "val" / "records").glob("*.json"))
    assert recs == ["vid_0.json"]                                        # queued videos never started
    rec = json.loads((ws.root / "runs" / "ag" / "val" / "records" / "vid_0.json").read_text())
    assert rec["stop"] == "interrupted"


def test_script_max_usd_holds_with_parallel_workers(ws, rca):
    df = _multi(ws, 2)
    rca.load_split = lambda split: df.copy()
    import threading
    lock = threading.Lock()

    class Pricey(FakeClient):   # ~$0.30 per request, never submits
        def _stream(self, **params):
            with lock:
                self.requests.append(1)
                n = len(self.requests)
            return FakeStream(_msg(n, [_use(n, 0, "get_frames", {"frames": [0]})],
                                   usage=_usage(i=10, o=min(15000, params["max_tokens"]))))
    client = Pricey()
    rca.main(_argv(ws, "--workers", "2", "--max-usd", "3", "--max-usd-video", "2"), client=client)
    assert budget.spent() <= 3.0 and len(client.requests) > 4
