"""Score new frontier models (Gemini 4 Argon, GPT-6.1 Sol, ...) as direct answerers on the 159 validation questions,
next to Claude and our current submission (combo3, matched to the identical test questions), and as ensemble members.
Validation labels are read only for scoring; nothing here writes a test answer.

    .venv/bin/python research/newmodels/evaluate.py runs/val_argon_frames/val_hires.csv [runs/val_sol_high/val_hires.csv ...]

Reports, per model: alone; per category and per source; blends with combo3 decided a priori:
  gm      geometric mean of combo3 and the model on every matched row
  med4    on rows where combo3 holds Claude's 3-run direct median (3D non-lab without a family rule):
          median of the 3 Claude runs + the model; elsewhere combo3
  gmdir   geometric mean of Claude's v1 direct answer and the model (pure direct-answer ensemble, all rows)
with clip-bootstrap 90% intervals of the delta vs combo3 (or vs Claude v1 direct for gmdir).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp import postprocess as pp  # noqa: E402
from qp.data import load_split  # noqa: E402
from qp.mra import item_scores  # noqa: E402

CATS = ["S2", "D2", "S3", "D3"]


def col(path, name="direct_value"):
    d = pd.read_csv(path)
    d = d.rename(columns={d.columns[0]: "id"}).set_index("id")
    c = name if name in d.columns else "parsed_value"
    s = pd.to_numeric(d[c], errors="coerce")
    return s.where(s > 0)


def sc(pred, gt):
    return pd.Series(np.nan_to_num(item_scores(pred.to_numpy(float), gt.to_numpy(float)), nan=0.0), index=gt.index)


def boot(delta, clips, n=4000, seed=0):
    rng = np.random.default_rng(seed)
    g = {c: delta[clips == c].to_numpy() for c in clips.unique()}
    keys = list(g)
    bs = [np.mean(np.concatenate([g[k] for k in rng.choice(keys, len(keys))])) for _ in range(n)]
    return np.percentile(bs, 5), np.percentile(bs, 95)


def main(paths):
    v = load_split("val_hires").set_index("qid")
    t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
    key_t = {(vid, pp.norm_question(q)): i for i, vid, q in zip(t.index, t.video_id, t.question)}
    v["tq"] = [key_t.get((vid, pp.norm_question(q))) for vid, q in zip(v.video_id, v.question)]
    v["cat"] = [t.category.get(i) if i is not None else None for i in v.tq]
    v["src"] = [t.srcg.get(i) if i is not None else None for i in v.tq]
    v["prov"] = [t.prov.get(i) if i is not None else None for i in v.tq]
    gt = v.answer.astype(float)
    clip = v.video_id.str.replace("_segmented", "", regex=False)
    R = {
        "claude_v1_direct": col(ROOT / "runs/val_hr_v1_high/val_hires.csv").reindex(v.index),
        "claude_v2_direct": col(ROOT / "runs/val_hr_v2_high/val_hires.csv").reindex(v.index),
        "claude_opus_direct": col(ROOT / "runs/val_opus_high/val.csv").reindex(v.index),
        "claude_v1_pipeline": col(ROOT / "runs/val_hr_v1_high/val_hires.csv", "parsed_value").reindex(v.index),
    }
    L = np.log(pd.concat([R["claude_v1_direct"], R["claude_v2_direct"], R["claude_opus_direct"]], axis=1))
    R["claude_3run_median"] = np.exp(L.median(axis=1))
    m = v.tq.notna()
    R["combo3"] = pd.Series([t.combo3.get(i) for i in v.tq], index=v.index, dtype=float)
    print(f"validation: {len(v)} questions, {clip.nunique()} clips; {int(m.sum())} matched to test rows (combo3)")
    rows = []
    for name, s in R.items():
        rows.append((name, s))
    new = {Path(p).parent.name: col(p).reindex(v.index) for p in paths}
    for name, s in new.items():
        rows.append((name, s))
    tab = []
    for name, s in rows:
        S = sc(s, gt)
        r = {"run": name, "answered": int(s.notna().sum()), "all159": S.mean(), "matched": S[m].mean()}
        for c in CATS:
            r[c] = S[v.cat == c].mean()
        for src in ("sim", "lab", "internet"):
            r[src] = S[v.src == src].mean()
        tab.append(r)
    print(pd.DataFrame(tab).set_index("run").round(3).to_string())
    base = sc(R["combo3"], gt)[m]
    for name, s in new.items():
        print(f"\n=== {name}: blends (matched rows, n={int(m.sum())}; combo3 = {base.mean():.4f}) ===")
        lr = np.log(s / R["claude_3run_median"]).abs()
        print(f"median |log(model / Claude 3-run median)| = {lr.median():.3f}")
        gm = np.exp((np.log(R["combo3"]) + np.log(s.fillna(R["combo3"]))) / 2)
        dmedrows = v.prov.isin(["dmed", "raw:direct"])
        L4 = np.log(pd.concat([R["claude_v1_direct"], R["claude_v2_direct"], R["claude_opus_direct"], s], axis=1))
        med4 = R["combo3"].where(~dmedrows, np.exp(L4.median(axis=1)))
        for bn, b in (("gm", gm), ("med4", med4)):
            S = sc(b, gt)[m]
            d = S - base
            lo, hi = boot(d, clip[m])
            per = {c: round((S - base)[v.cat[m] == c].mean(), 4) for c in CATS}
            print(f"{bn:5s} {S.mean():.4f}  delta {d.mean():+.4f} [{lo:+.4f}, {hi:+.4f}]  per cat {per}  "
                  f"rows changed {int((~np.isclose(b[m], R['combo3'][m])).sum())}")
        gmd = np.exp((np.log(R["claude_v1_direct"]) + np.log(s.fillna(R["claude_v1_direct"]))) / 2)
        S0, S1 = sc(R["claude_v1_direct"], gt), sc(gmd, gt)
        lo, hi = boot(S1 - S0, clip)
        print(f"gmdir {S1.mean():.4f} vs claude v1 direct {S0.mean():.4f}: delta {(S1 - S0).mean():+.4f} [{lo:+.4f}, {hi:+.4f}]")
        bycl = (sc(s, gt) - sc(R["claude_3run_median"], gt)).groupby(clip).mean()
        print(f"clips where {name} beats Claude 3-run median: {int((bycl > 0).sum())}/{int((bycl != 0).sum())}")


if __name__ == "__main__":
    main(sys.argv[1:])
