"""Second independent agent pass on validation clips (/tmp/blind_r2) vs the first (/tmp/blind): which combination wins?

Rows: validation questions of clips answered in both passes, matched to a test row (combo3 = our base there).
Combinations (logs): a1, a2, base, gm(a1, base) [current 2D-sim routing], gm(a1, a2), med(a1, a2, base), gm(a1, a2, base).
Item means by clip type, with per-clip bootstrap CIs for the main contrasts.

    .venv/bin/python research/blind/eval_r2.py
"""
from __future__ import annotations

import json
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


def answers(root, videos):
    out = {}
    for v in videos:
        f = Path(root) / v / "answers.json"
        if f.exists():
            for k, x in json.loads(f.read_text()).items():
                try:
                    out[int(k)] = abs(float(x))
                except (TypeError, ValueError):
                    pass
    return pd.Series(out, dtype=float)


def main():
    vids = sorted(p.parent.name for p in Path("/tmp/blind_r2").glob("*/answers.json"))
    v = load_split("val_hires").set_index("qid")
    v = v[v.video_id.isin(vids)]
    t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
    key = {(a, pp.norm_question(b)): i for i, a, b in zip(t.index, t.video_id, t.question)}
    tq = [key.get((a, pp.norm_question(b))) for a, b in zip(v.video_id, v.question)]
    base = pd.Series([t.combo3.get(i) if i is not None else np.nan for i in tq], index=v.index, dtype=float)
    a1 = answers("/tmp/blind", vids).reindex(v.index)
    a2 = answers("/tmp/blind_r2", vids).reindex(v.index)
    gt = v.answer.astype(float)
    typ = np.where(v.video_type.str[1].eq("3"), "sim3", "sim2")
    L = pd.DataFrame({"a1": np.log(a1), "a2": np.log(a2), "base": np.log(base)})
    C = {"a1": L.a1, "a2": L.a2, "base": L.base, "gm(a1,base)": (L.a1 + L.base) / 2, "gm(a1,a2)": (L.a1 + L.a2) / 2,
         "med(a1,a2,base)": L[["a1", "a2", "base"]].median(axis=1), "gm(a1,a2,base)": L[["a1", "a2", "base"]].mean(axis=1),
         "gm(gm(a1,a2),base)": ((L.a1 + L.a2) / 2 + L.base) / 2}
    S = pd.DataFrame({k: E.sc(np.exp(x), gt) for k, x in C.items()})
    m = L.notna().all(axis=1)
    S["type"], S["vid"] = typ, v.video_id
    print(f"clips {len(vids)}; rows {len(v)}; with a1, a2 and base: {int(m.sum())}")
    print(S[m].groupby("type").mean(numeric_only=True).round(3).T.to_string())
    print("all:", S[m].mean(numeric_only=True).round(3).to_dict())
    for tp in ("sim2", "sim3"):
        mm = m & (S.type == tp)
        for a, b in (("med(a1,a2,base)", "gm(a1,base)"), ("gm(a1,a2)", "a1"), ("gm(a1,a2,base)", "gm(a1,base)")):
            d = (S[a] - S[b])[mm]
            lo, hi = E.boot(d, S.vid[mm])
            print(f"{tp}: {a} - {b}: {d.mean():+.4f} [{lo:+.4f}, {hi:+.4f}]")
    r = pd.DataFrame({"clip": v.video_id, "q": v.question.str[:55], "gt": gt, "a1": a1, "a2": a2, "base": base})
    r["a2/a1"] = r.a2 / r.a1
    pd.set_option("display.width", 250)
    print(r.round(3).to_string())
    print("median |log(a2/a1)| by type:", pd.Series(np.abs(np.log(r["a2/a1"])).values, index=typ).groupby(level=0).median().round(3).to_dict())


if __name__ == "__main__":
    main()
