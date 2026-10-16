"""Build a Track B candidate from the open-weight agent's test answers on top of submissions/trackB_probe_B2route.csv,
with the per-type routing fixed on validation by evaluate.py (routing.json; pre-registered rule in RESULT.md).

    .venv/bin/python research/trackb_agent/build_sub.py --root <pulled outputs/trackb_agent> \
        [--routing research/trackb_agent/routing.json] [--out submissions/trackB_cand_agent.csv]

First the transcript audit (common.audit_clips: qp.open.agent_loop.audit_transcript and the local string scan; either
flags -> flagged): flagged clips are EXCLUDED (printed; their rows, and twin rows copied from them, keep B2route).
Per test row (routing type = common.route_types: clip_type of its inputs, sim3 / sim2 / internet / lab, except that a
row answered from a twin's original - source 'twin:<orig>:<qid>' from the agent loop or from the fill below - and every
row of a segmented twin whose original is in the split are routed by the ORIGINAL clip's type, so segmented internet
twins follow the internet decision):
    stated-fact rows of the B2route build (base_test.csv stated = 1) keep the B2route value;
    type "agent" -> the agent answer, "gm" -> geometric mean of agent and B2route, "base" -> B2route;
    rows the agent did not answer keep B2route.
Segmented twins: run_agent already copies the original clip's answer to the same normalised question; any twin row still
without an answer takes it here too (research/blind/build_agent_sub.py mapping, qp.postprocess.norm_question; source
'twin:<orig>:<qid>'), except rows of excluded clips.
Every value comes from open-weight model outputs and model-free code; no label and no closed-model output is read.
The stated-fact check printed at the end (test rows whose answer a sibling clip states as its prior; r86 master table)
is information only; it never changes the routing.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import common as C  # noqa: E402
from qp import postprocess as pp  # noqa: E402


def fill_twins(t: pd.DataFrame, ag: pd.Series, src: pd.Series, exclude=()) -> tuple[pd.Series, pd.Series, int]:
    """Twin rows still without an answer take the original clip's answer to the same normalised question (source
    'twin:<orig>:<qid>', so common.route_types routes them by the original's type). Rows of excluded clips stay empty."""
    ag, src = ag.copy(), src.astype(object).copy()
    ex = {str(x) for x in exclude}
    orig = {(v, pp.norm_question(q)): i for i, v, q in zip(t.index, t.video_id, t.question) if not v.endswith("_segmented")}
    n = 0
    for i, v, q in zip(t.index, t.video_id, t.question):
        if v.endswith("_segmented") and v not in ex and np.isnan(ag[i]):
            o = v[: -len("_segmented")]
            j = orig.get((o, pp.norm_question(q)))
            if j is not None and not np.isnan(ag[j]):
                ag[i], src[i] = ag[j], f"twin:{o}:{j}"
                n += 1
    return ag, src, n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True)
    ap.add_argument("--routing", default=str(HERE / "routing.json"))
    ap.add_argument("--out", default=str(ROOT / "submissions" / "trackB_cand_agent.csv"))
    a = ap.parse_args(argv)
    routing = json.loads(Path(a.routing).read_text())
    decision = routing["decision"]
    assert set(decision) <= set(C.TYPES) and set(decision.values()) <= {"agent", "gm", "base"}, decision
    from qp.data import load_split
    t = load_split("test").set_index("qid")
    assert "answer" not in t.columns
    bt = C.load_base("base_test.csv").set_index("id").reindex(t.index)
    base, stated = bt.base.astype(float), bt.stated.fillna(0).astype(int)
    assert base.notna().all()
    tdir = Path(a.root) / "test"
    _, _, recs = C.agent_answers(tdir)
    flagged = C.audit_clips(tdir, recs)              # Track B rule: flagged clips keep the base
    ag, src, recs = C.agent_answers(tdir, exclude=flagged)
    ag, src = ag.reindex(t.index), src.reindex(t.index)
    ag, src, n_tw = fill_twins(t, ag, src, flagged)
    types = C.route_types(t, src)
    own = pd.Series([C.clip_type(s, v) for s, v in zip(t.video_source, t.video_type)], index=t.index)
    final = C.routed(base, ag, types, stated, decision)
    print(f"routing (from validation, {routing.get('written', '?')}): {decision}")
    print(f"agent answers: {int(ag.notna().sum())}/{len(t)} test rows ({len(recs)} clips, {len(flagged)} excluded; "
          f"{n_tw} filled from twins here)")
    rr = types != own
    if rr.any():
        pairs = pd.Series([f"{x} -> {y}" for x, y in zip(own[rr], types[rr])]).value_counts()
        print(f"rows routed by their original clip's type (twins): {int(rr.sum())} ("
              + ", ".join(f"{k}: {c}" for k, c in pairs.items()) + ")")
    ch = ~np.isclose(final.to_numpy(), base.to_numpy(), rtol=1e-9)
    tab = pd.crosstab(types[ch].rename("type"), t.category[ch]) if ch.any() else pd.DataFrame()
    print(f"rows changed vs B2route: {int(ch.sum())}; stated rows kept: {int((stated.astype(bool) & ag.notna()).sum())}")
    if len(tab):
        print(tab.to_string())
    lr = np.log(final[ch] / base[ch]).abs()
    if len(lr):
        print(f"median |log(new/base)| {lr.median():.3f}; share > log 1.5: {(lr > np.log(1.5)).mean():.1%}")
    # information only: stated facts (exact values a sibling clip states as its prior)
    mp = ROOT / "research/r86/loss_audit/master.pkl"
    if mp.exists():
        from qp.mra import item_scores
        m = pd.read_pickle(mp).reindex(t.index)
        fm = m.fact.notna() & ag.notna() & ~stated.astype(bool)
        if not fm.any():
            print("stated-fact check (info): every fact row is already set by the B2route facts rule")
        else:
            s_ag = np.nan_to_num(item_scores(ag[fm].to_numpy(), m.fact[fm].to_numpy())).mean()
            s_b = np.nan_to_num(item_scores(base[fm].to_numpy(), m.fact[fm].to_numpy())).mean()
            print(f"stated-fact check (info) on {int(fm.sum())} rows not set by the facts rule: agent {s_ag:.3f} vs "
                  f"B2route {s_b:.3f}; by type " + ", ".join(
                      f"{k} {np.nan_to_num(item_scores(ag[fm & (types == k)], m.fact[fm & (types == k)])).mean():.3f}"
                      f"/{np.nan_to_num(item_scores(base[fm & (types == k)], m.fact[fm & (types == k)])).mean():.3f}"
                      for k in C.TYPES if (fm & (types == k)).any()))
    assert final.notna().all() and np.isfinite(final).all() and (final > 0).all()
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": final.index, "parsed_value": final.to_numpy()}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, a.out], check=True)
    print("wrote", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
