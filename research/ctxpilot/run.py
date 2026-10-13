"""Pilot: does MORE context (sibling camera clips of the same Blender scene) improve Claude's direct answers on
3D simulation validation questions? Two arms with the identical direct-answer prompt and settings:
  single: the target clip only (its frames, prior, depth info) + its validation questions
  family: the same + up to 3 sibling clips of the scene family (8 frames each, their stated prior and depth info)
Scored only on the target clip's validation questions. Paid (sync, budget-held), ~12 requests.

Kill test (fixed before running): family beats single by >= +0.015 MRA and wins on most clips.

    .venv/bin/python research/ctxpilot/run.py            # runs missing requests, then scores
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from qp import budget  # noqa: E402
from qp import claude_annotate as ca  # noqa: E402
from qp import postprocess as pp  # noqa: E402
from qp.data import load_split, load_test  # noqa: E402
from qp.mra import item_scores  # noqa: E402

OUT = Path(__file__).parent / "out"
MODEL, EFFORT, MAX_SIDE, N_TARGET, MAX_TARGET, N_SIB, MAX_SIBS = ca.MODEL, "high", 1280, 16, 32, 8, 3
SYSTEM = (
    "You are an expert in quantitative physical reasoning from video. Each clip comes with one exactly-true "
    "quantity (its prior) and, for 3D clips, camera-to-object distances. Use the frames, the priors and the "
    "distances of ALL clips shown (they are different camera views of the same simulated scene, rendered in "
    "Blender; the same objects have the same physical sizes and the same event happens at the same times) to "
    "answer each question about the TARGET clip numerically in the unit asked. Think carefully, measure in the "
    "frames, and cross-check against the other views. Return JSON only.")
SCHEMA = {"type": "object", "properties": {"answers": {"type": "array", "items": {
    "type": "object", "properties": {"qid": {"type": "integer"}, "value": {"type": "number"}},
    "required": ["qid", "value"], "additionalProperties": False}}}, "required": ["answers"],
    "additionalProperties": False}


def clip_blocks(row, n_uniform, max_frames, label, rows_for_times):
    path = str(row.video_path)
    fps, _ = ca.video_fps(row.fps, path)
    n_total = ca.video_info(path)[0]
    idxs, _ = ca.frame_plan(rows_for_times, n_total, fps, n_uniform, max_frames, "v1")
    frames, _ = ca.read_frames(path, idxs, fps, 90, MAX_SIDE)
    head = (f"{label} clip {row.video_id}: {frames[0].width}x{frames[0].height} px, {fps:g} fps, {n_total} frames "
            f"(~{n_total / fps:.2f} s). Prior: {row.prior}. Distances: {str(row.depth_info or '').strip() or 'none'}. "
            f"{len(frames)} frames follow.")
    content = [{"type": "text", "text": head}]
    for f in frames:
        content.append({"type": "text", "text": f"[{row.video_id}] " + ca.frame_label(f)})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": f.jpeg_b64}})
    return content


def build(target_rows, siblings):
    t0 = target_rows.iloc[0]
    content = []
    for s in siblings:
        content += clip_blocks(s, N_SIB, N_SIB, "Sibling view", pd.DataFrame([s]))
    content += clip_blocks(t0, N_TARGET, MAX_TARGET, "TARGET", target_rows)
    qs = "\n".join(f"- qid {int(r.qid)}: {r.question}" for r in target_rows.itertuples())
    content.append({"type": "text", "text": f"Questions about the TARGET clip {t0.video_id}:\n{qs}"})
    return {"model": MODEL, "max_tokens": 32000,
            "system": [{"type": "text", "text": SYSTEM}],
            "messages": [{"role": "user", "content": content}],
            "output_config": {"effort": EFFORT, "format": {"type": "json_schema", "schema": SCHEMA}}}


def main():
    import run_claude as rc
    rc.load_env()
    import anthropic
    client = anthropic.Anthropic(max_retries=5)
    OUT.mkdir(parents=True, exist_ok=True)
    v = load_split("val_hires")
    v = v[(v.video_type.str[1] == "3") & (v.video_source != "lab")]
    t = load_test()
    df = pp._questions(t)
    fam = pp.scene_families(df, pp.scene_links(df, pp._parse_facts(df), pp.FrameCache()))
    tclips = t.drop_duplicates("video_id").set_index("video_id")
    num = lambda s: int(re.search(r"(\d+)", s).group(1))  # noqa: E731
    for vid, rows in v.groupby("video_id"):
        members = sorted({m for m in t.video_id if fam.get(m) == fam.get(vid)})
        base = pp.base_id(vid)
        sibs = [m for m in members if not m.endswith("_segmented") and pp.base_id(m) != base]
        sibs = sorted(sibs, key=lambda m: abs(num(m) - num(vid)))[:MAX_SIBS]
        for arm, sl in (("single", []), ("family", sibs)):
            f = OUT / f"{vid}__{arm}.json"
            if f.exists():
                continue
            if arm == "family" and not sl:
                print(f"{vid}: no sibling views; family arm = single"); continue
            params = build(rows, [pd.Series({**tclips.loc[s].to_dict(), "video_id": s}) for s in sl])
            try:
                n_in = client.messages.count_tokens(model=MODEL, system=params["system"],
                                                     messages=params["messages"]).input_tokens
            except Exception:  # noqa: BLE001
                n_in = 25000 + 12000 * len(sl)
            worst = budget.estimate_usd(n_in, params["max_tokens"], MODEL)
            with budget.reserve(worst):
                with client.messages.stream(**params) as st:
                    r = st.get_final_message()
                usd = budget.price(r.usage, MODEL)
                budget.record("ctxpilot", MODEL, "sync", r.id, r.usage, usd=usd)
            text = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
            f.write_text(json.dumps({"video": vid, "arm": arm, "siblings": sl, "usd": usd, "text": text,
                                     "input_tokens": r.usage.input_tokens}))
            print(f"{vid} {arm}: {len(sl)} siblings, {r.usage.input_tokens} in, ${usd:.3f}", flush=True)
    score(v)


def score(v):
    ans = {}
    for f in OUT.glob("*.json"):
        d = json.loads(f.read_text())
        try:
            a = {int(x["qid"]): float(x["value"]) for x in json.loads(d["text"])["answers"]}
        except Exception as e:  # noqa: BLE001
            print("parse failed", f.name, e); continue
        ans.setdefault(d["arm"], {}).update(a)
    gt = v.set_index("qid").answer.astype(float)
    vid = v.set_index("qid").video_id
    single = pd.Series(ans.get("single", {})).reindex(gt.index)
    family = pd.Series(ans.get("family", {})).reindex(gt.index).fillna(single)   # no-sibling clips: = single
    S = pd.DataFrame({k: np.nan_to_num(item_scores(s.to_numpy(), gt.to_numpy()), nan=0.0)
                      for k, s in (("single", single), ("family", family))}, index=gt.index)
    d = (S.family - S.single)
    byclip = d.groupby(vid).mean()
    print(S.mean().round(4).to_dict(), "| per clip:", byclip.round(3).to_dict())
    ok = d.mean() >= 0.015 and (byclip > 0).sum() > (byclip != 0).sum() / 2
    print(f"delta {d.mean():+.4f}; KILL TEST:", "PASS" if ok else "FAIL")
    pd.DataFrame({"gt": gt, "single": single, "family": family}).to_csv(OUT / "answers.csv")


if __name__ == "__main__":
    main()
