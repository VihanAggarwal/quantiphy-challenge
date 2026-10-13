"""Pilot 2: the FULL pipeline prompt (v1: specs, tracks, direct answers; same settings as val_hr_v1_high:
high effort, 16 uniform + asked-time frames up to 32, max side 2576) with up to 3 sibling camera clips of the same
scene family prepended as context (8 frames each, their prior and distances; marked as context, not to be annotated).
Only the direct answers are used (3D non-lab rows are answered by Claude's direct answer in the pipeline).

Kill test (fixed before running): direct-answer MRA beats the matched single batched run val_hr_v1_high by
>= +0.015 on the 52 questions and wins on most clips whose score changes.

    .venv/bin/python research/ctxpilot/run_pipeline.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).parent))
from qp import budget  # noqa: E402
from qp import claude_annotate as ca  # noqa: E402
from qp import postprocess as pp  # noqa: E402
from qp.data import load_split, load_test  # noqa: E402
from qp.mra import item_scores  # noqa: E402
import run as pilot1  # noqa: E402

OUT = Path(__file__).parent / "out_pipeline"
NOTE = ("CONTEXT ONLY: the next clips are other camera views of the same Blender scene (same objects, same sizes, "
        "same event timing). Use them, their priors and their distances to cross-check scale and motion. Do NOT "
        "annotate them: all tracks/frame references in your answer must refer to the TARGET video that follows.")


def main():
    import run_claude as rc
    rc.load_env()
    import anthropic
    client = anthropic.Anthropic(max_retries=5)
    OUT.mkdir(parents=True, exist_ok=True)
    v = load_split("val_hires")
    v = v[(v.video_type.str[1] == "3") & (v.video_source != "lab")]
    t = load_test()
    tclips = t.drop_duplicates("video_id").set_index("video_id")
    sib_used = {json.loads(f.read_text())["video"]: json.loads(f.read_text())["siblings"]
                for f in (Path(__file__).parent / "out").glob("*__family.json")}
    for vid, rows in v.groupby("video_id"):
        f = OUT / f"{vid}.json"
        sl = sib_used.get(vid, [])
        if f.exists() or not sl:
            continue
        params, meta = ca.build_request(rows, n_uniform=16, max_frames=32, effort="high", prompt_version="v1",
                                        max_side=2576)
        ctx = [{"type": "text", "text": NOTE}]
        for s in sl:
            ctx += pilot1.clip_blocks(pd.Series({**tclips.loc[s].to_dict(), "video_id": s}), 8, 8, "Context view",
                                      pd.DataFrame([{**tclips.loc[s].to_dict(), "video_id": s}]))
        ctx.append({"type": "text", "text": "TARGET video (annotate this one):"})
        params["messages"][0]["content"] = ctx + params["messages"][0]["content"]
        worst = budget.estimate_usd(30000 + 12000 * len(sl), params["max_tokens"], ca.MODEL)
        with budget.reserve(worst):
            with client.messages.stream(**params) as st:
                r = st.get_final_message()
            usd = budget.price(r.usage, ca.MODEL)
            budget.record("ctxpilot_pipe", ca.MODEL, "sync", r.id, r.usage, usd=usd)
        text = ca.response_text(r)
        anns = ca.to_annotations(ca.parse_json(text) or {}, meta)
        direct = {int(q): a.direct_answer for q, a in anns.items()}
        f.write_text(json.dumps({"video": vid, "siblings": sl, "usd": usd, "direct": direct, "text": text}))
        print(f"{vid}: {len(sl)} context views, {r.usage.input_tokens} in, ${usd:.3f}, {len(direct)} answers", flush=True)
    score(v)


def score(v):
    gt = v.set_index("qid").answer.astype(float)
    vid = v.set_index("qid").video_id
    d = lambda p: pd.to_numeric(pd.read_csv(p).set_index("id").direct_value, errors="coerce").reindex(gt.index)  # noqa: E731
    base = d(ROOT / "runs/val_hr_v1_high/val_hires.csv")
    new = {}
    for f in OUT.glob("*.json"):
        new.update({int(k): v_ for k, v_ in json.loads(f.read_text())["direct"].items() if v_ is not None})
    ctx = pd.Series(new, dtype=float).reindex(gt.index).fillna(base)          # clips without siblings: = base
    r2, r3 = d(ROOT / "runs/val_hr_v2_high/val_hires.csv"), d(ROOT / "runs/val_opus_high/val.csv")
    med = lambda *s: np.exp(np.log(pd.concat(s, axis=1)).median(axis=1))  # noqa: E731
    sc = lambda s: pd.Series(np.nan_to_num(item_scores(s.to_numpy(), gt.to_numpy()), nan=0.0), index=gt.index)  # noqa: E731
    S = {"base_hr_v1": sc(base), "ctx_pipeline": sc(ctx), "3run": sc(med(base, r2, r3)),
         "3run_ctx_replaces_v1": sc(med(ctx, r2, r3)), "4run_with_ctx": sc(med(base, r2, r3, ctx))}
    for k, s in S.items():
        print(f"{k:22s} {s.mean():.4f}")
    dd = S["ctx_pipeline"] - S["base_hr_v1"]
    byclip = dd.groupby(vid).mean()
    print("per clip:", byclip.round(3).to_dict())
    ok = dd.mean() >= 0.015 and (byclip > 0).sum() > (byclip != 0).sum() / 2
    print(f"delta {dd.mean():+.4f}; KILL TEST:", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    main()
