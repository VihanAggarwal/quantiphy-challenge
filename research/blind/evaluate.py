"""Score the blind agentic-measurement pilot (/tmp/blind/<video>/answers.json).

Validation clips: agent vs label, next to combo3 (matched test rows) and Claude's pipeline / direct runs.
Fact clips (test, answers stated as priors in sibling clips the agent never saw): agent vs the stated fact, next to our raw
routed answer before the facts rule (3D sim: the 3-run direct median).
Also a leakage audit: every agent transcript is scanned for paths under the repo's data/ or runs/ folders, the validation set,
or other clips' folders.

    .venv/bin/python research/blind/evaluate.py [/tmp/blind] [transcript dirs ...]
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
sys.path.insert(0, str(ROOT / "research/newmodels"))
import evaluate as E  # noqa: E402
from qp import postprocess as pp  # noqa: E402
from qp.data import load_split  # noqa: E402

B = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("/root") else Path("/tmp/blind")
TDIRS = [Path(p) for p in sys.argv[1:] if p.startswith("/root")]


def agent_answers():
    out = {}
    for d in sorted(B.iterdir()):
        f = d / "answers.json"
        if d.is_dir() and f.exists():
            try:
                for k, v in json.loads(f.read_text()).items():
                    try:
                        out[int(k)] = float(v)
                    except (TypeError, ValueError):
                        pass
            except json.JSONDecodeError:
                print("bad json", f)
    return pd.Series(out, dtype=float)


def main():
    man = pd.DataFrame(json.loads((B / "manifest.json").read_text()))
    ag = agent_answers()
    done = [v for v in man.video_id if (B / v / "answers.json").exists()]
    print(f"clips answered: {len(done)}/{len(man)}")
    t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
    # ---- validation clips
    v = load_split("val_hires").set_index("qid")
    v = v[v.video_id.isin([x for x in man[man.set == "val"].video_id if x in done])]
    key = {(a, pp.norm_question(b)): i for i, a, b in zip(t.index, t.video_id, t.question)}
    v["tq"] = [key.get((a, pp.norm_question(b))) for a, b in zip(v.video_id, v.question)]
    gt = v.answer.astype(float)
    clip = v.video_id
    A = ag.reindex(v.index)
    c3 = pd.Series([t.combo3.get(i) if i is not None else np.nan for i in v.tq], index=v.index, dtype=float)
    pipe = E.col(ROOT / "runs/val_hr_v1_high/val_hires.csv", "parsed_value").reindex(v.index)
    L = np.log(pd.concat([E.col(ROOT / p).reindex(v.index) for p in
                          ("runs/val_hr_v1_high/val_hires.csv", "runs/val_hr_v2_high/val_hires.csv", "runs/val_opus_high/val.csv")], axis=1))
    dmed = np.exp(L.median(axis=1))
    if len(v):
        m = c3.notna()
        S = pd.DataFrame({"agent": E.sc(A, gt), "combo3": E.sc(c3, gt), "claude_pipeline": E.sc(pipe, gt), "claude_dmed": E.sc(dmed, gt),
                          "gm_agent_combo3": E.sc(np.exp((np.log(A.fillna(c3)) + np.log(c3)) / 2), gt)})
        S["src"] = v.video_source
        print(f"\nVALIDATION ({len(v)} q, {clip.nunique()} clips; agent answered {int(A.notna().sum())}); matched to combo3: {int(m.sum())}")
        print(S[m].groupby("src").mean(numeric_only=True).round(3).to_string())
        print("all matched:", S[m].mean(numeric_only=True).round(4).to_dict())
        d = (S.agent - S.combo3)[m]
        lo, hi = E.boot(d, clip[m])
        print(f"agent - combo3: {d.mean():+.4f} [{lo:+.4f}, {hi:+.4f}]; per clip: {d.groupby(clip[m]).mean().round(3).to_dict()}")
        rows = pd.DataFrame({"video": clip, "q": v.question.str[:70], "gt": gt, "agent": A, "combo3": c3})
        rows["r_agent"] = rows.agent / rows.gt
        rows["r_combo3"] = rows.combo3 / rows.gt
        rows.round(3).to_csv(ROOT / "research/blind/val_rows.csv")
    # ---- fact clips
    fv = [x for x in man[man.set == "fact"].video_id if x in done]
    f = t[t.video_id.isin(fv) & t.fact.notna()].copy()
    if len(f):
        raw = f.r_parsed_value.where(~(f.category.isin(["S3", "D3"]) & f.srcg.eq("sim")), f.dmed)
        Af = ag.reindex(f.index)
        Sf = pd.DataFrame({"agent": E.sc(Af, f.fact), "raw_ours": E.sc(raw, f.fact),
                           "gm": E.sc(np.exp((np.log(Af.fillna(raw)) + np.log(raw)) / 2), f.fact)})
        d = Sf.agent - Sf.raw_ours
        lo, hi = E.boot(d, f.video_id)
        print(f"\nFACTS ({len(f)} rows, {f.video_id.nunique()} clips; agent answered {int(Af.notna().sum())}):",
              Sf.mean().round(4).to_dict(), f"agent - raw {d.mean():+.4f} [{lo:+.4f}, {hi:+.4f}]")
        print(pd.DataFrame({"video": f.video_id, "q": f.question.str[:60], "fact": f.fact, "agent": Af, "raw": raw}).round(3).to_string())
    # ---- leakage audit
    bad = re.compile(r"quantiphy-challenge/(data|runs|research|submissions|budget)|QuantiPhy-validation|val_hires|answer\"\s*:")
    hits = []
    for td in TDIRS:
        for p in td.glob("agent-*.jsonl"):
            for line in p.read_text(errors="ignore").splitlines():
                if '"tool_use"' in line and bad.search(line):
                    hits.append((p.name, bad.search(line).group(0)))
    print(f"\nleakage audit: {len(hits)} suspicious tool calls", hits[:20])


if __name__ == "__main__":
    main()
