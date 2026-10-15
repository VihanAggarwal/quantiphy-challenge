"""Build a Track A candidate from the agentic-measurement answers (/tmp/blind_test/<video>/answers.json).

Rows replaced: every scored test row of a clip whose agent answered it, for the clip types given (default: 3D simulation),
plus their segmented twins (same normalised question in <video>_segmented takes the original's agent answer).
Rows kept: rows whose base value equals an exact stated fact (family facts rule), and every other row.
Archives answers + notes into research/blind/out/<video>/ (small files only).

    .venv/bin/python research/blind/build_agent_sub.py BASE_CSV OUT_CSV [--root /tmp/blind_test] [--types sim3]
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp import postprocess as pp  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("out")
    ap.add_argument("--root", default="/tmp/blind_test")
    ap.add_argument("--types", default="sim3", help="comma list of sim3, sim2, internet")
    a = ap.parse_args()
    t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
    d = pd.read_csv(a.base)
    base = d.rename(columns={d.columns[0]: "id"}).set_index("id")["parsed_value"].astype(float).reindex(t.index)
    root = Path(a.root)
    arch = ROOT / "research/blind/out"
    ag = {}
    for vd in sorted(p for p in root.iterdir() if p.is_dir()):
        f = vd / "answers.json"
        if not f.exists():
            continue
        try:
            for k, x in json.loads(f.read_text()).items():
                try:
                    val = abs(float(x))
                except (TypeError, ValueError):
                    continue
                if np.isfinite(val) and val > 0:
                    ag[(vd.name, int(k))] = val
        except json.JSONDecodeError:
            print("bad json", f)
            continue
        o = arch / vd.name
        o.mkdir(parents=True, exist_ok=True)
        for fn in ("answers.json", "notes.md"):
            if (vd / fn).exists():
                shutil.copy(vd / fn, o / fn)
    types = set(a.types.split(","))
    kind = np.where(t.srcg.eq("sim") & t.video_type.str[1].eq("3"), "sim3",
                    np.where(t.srcg.eq("sim") & t.video_type.str[1].eq("2"), "sim2",
                             np.where(t.srcg.eq("internet"), "internet", "lab")))
    ans = pd.Series(np.nan, index=t.index)
    for i, v in zip(t.index, t.video_id):
        x = ag.get((v, i))
        if x is not None:
            ans[i] = x
    # segmented twins take the original's answer to the same normalised question
    orig = {(v, pp.norm_question(q)): i for i, v, q in zip(t.index, t.video_id, t.question) if not v.endswith("_segmented")}
    for i, v, q in zip(t.index, t.video_id, t.question):
        if v.endswith("_segmented") and np.isnan(ans[i]):
            j = orig.get((v[: -len("_segmented")], pp.norm_question(q)))
            if j is not None and not np.isnan(ans.get(j, np.nan)):
                ans[i] = ans[j]
    is_fact = t.fact.notna() & np.isclose(base, t.fact.fillna(-1), rtol=1e-6)
    use = ans.notna() & pd.Series(np.isin(kind, list(types)), index=t.index) & ~is_fact
    out = base.copy()
    out[use] = ans[use]
    sc = use & t.scored
    print(f"agent answers: {len(ag)}; rows replaced {int(use.sum())} (scored {int(sc.sum())}):",
          t.loc[sc].category.value_counts().to_dict(), "| facts kept:", int((ans.notna() & is_fact).sum()))
    lr = np.log(ans[sc] / base[sc]).abs()
    print(f"median |log(agent/base)| {lr.median():.3f}; share > log 1.5: {(lr > np.log(1.5)).mean():.1%}")
    # held-out check on exact stated facts (agent never saw the sibling clips that state them)
    fm = ans.notna() & t.fact.notna() & pd.Series(np.isin(kind, list(types)), index=t.index)
    if fm.any():
        from qp.mra import item_scores
        raw = t.r_parsed_value.where(~(t.category.isin(["S3", "D3"]) & t.srcg.eq("sim")), t.dmed)
        s_ag = np.nan_to_num(item_scores(ans[fm].to_numpy(), t.fact[fm].to_numpy()))
        s_raw = np.nan_to_num(item_scores(raw[fm].to_numpy(), t.fact[fm].to_numpy()))
        print(f"stated-fact check on {int(fm.sum())} rows ({t.video_id[fm].nunique()} clips): agent {s_ag.mean():.3f} vs our raw {s_raw.mean():.3f}")
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": out.index, "parsed_value": out.values}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, a.out], check=True)


if __name__ == "__main__":
    main()
