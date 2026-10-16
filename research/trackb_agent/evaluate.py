"""Score the open-weight agent (RUN_PRESET "agent") on validation against the B2route-equivalent validation answers and
fix the per-type routing with the pre-registered rule (RESULT.md). CPU only; validation labels are read for scoring only.

    .venv/bin/python research/trackb_agent/evaluate.py --root <pulled outputs/trackb_agent> [--write]

Inputs: <root>/val/answers/*.json (qp/open/run_agent.py on split val_hires), research/trackb_agent/base_val.csv
(make_base.py: B2route's pipeline on the validation questions). Per clip type (sim3, sim2, internet, lab):
    base        B2route-equivalent answer
    agent       agent answer where it gave one, else base (what the build would submit); stated-fact rows keep base
    gm          geometric mean of agent and base where both exist (informational)
Score = mean item MRA (qp.mra.item_scores) over the type's validation questions. Decision per type:
    agent if agent >= base + 0.02; gm(agent, base) if within 0.02; base otherwise (no agent answer on the type: base).
--write stores the decision in research/trackb_agent/routing.json (read by build_sub.py). Also prints the macro MRA of
base and of the routed composite, clip-bootstrap 90% intervals of agent - base per type (information only, not part
of the rule), the end reasons of the agent runs and a leakage audit of the transcripts.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))
import common as C  # noqa: E402
from qp.mra import item_scores, score  # noqa: E402

LEAK = re.compile(r"QuantiPhy-validation|ground_truth|submission_template|/data/QuantiPhy|quantiphy-challenge|"
                  r"/content/drive|outputs/trackb|\.\./", re.I)


def boot(d: pd.Series, clips: pd.Series, n: int = 2000, seed: int = 0) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    g = d.groupby(clips)
    s, c = g.sum(), g.size()
    k = len(s)
    if k == 0:
        return float("nan"), float("nan")
    idx = rng.integers(0, k, size=(n, k))
    m = s.to_numpy()[idx].sum(1) / c.to_numpy()[idx].sum(1)
    return float(np.percentile(m, 5)), float(np.percentile(m, 95))


def audit(split_dir: Path) -> None:
    hits, denied, n = [], 0, 0
    for p in sorted((split_dir / "transcripts").glob("*.json")) if (split_dir / "transcripts").exists() else []:
        tr = json.loads(p.read_text())
        n += 1
        for t in tr.get("turns", []):
            txt = t.get("text") or ""
            if t.get("role") == "assistant" and LEAK.search(txt):
                hits.append((tr.get("video_id"), LEAK.search(txt).group(0)))
            if t.get("role") == "user" and ("outside the workspace" in txt or "network access is disabled" in txt):
                denied += 1
    print(f"\nleakage audit ({n} transcripts): {len(hits)} assistant turn(s) naming paths outside the workspace"
          f"{': ' + str(hits[:10]) if hits else ''}; {denied} sandbox refusal(s) (file outside workspace / network)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True, help="outputs/trackb_agent (pulled from the colab-outputs branch)")
    ap.add_argument("--write", action="store_true", help="write research/trackb_agent/routing.json")
    ap.add_argument("--routing", default=str(HERE / "routing.json"))
    a = ap.parse_args(argv)
    from qp.data import load_validation
    vdir = Path(a.root) / "val"
    gt = load_validation().set_index("qid")
    base_t = C.load_base("base_val.csv").set_index("qid")
    v = gt.join(base_t[["base", "stated"]], how="left")
    v["type"] = [C.clip_type(s, t) for s, t in zip(v.video_source, v.video_type)]
    ag, src, recs = C.agent_answers(vdir)
    v["agent_raw"] = ag.reindex(v.index)
    v["src"] = src.reindex(v.index)
    st = v.stated.fillna(0).astype(bool)
    v["agent"] = v.agent_raw.where(v.agent_raw.notna() & ~st, v.base)
    v["gm"] = C.gm(v.agent_raw.where(~st), v.base)
    S = pd.DataFrame({m: item_scores(v[m].to_numpy(), v.answer.to_numpy()) for m in ("base", "agent", "gm")},
                     index=v.index).fillna(0.0)          # a missing value scores 0 (official evaluator)
    print(f"validation: {len(v)} questions, {v.video_id.nunique()} clips; agent answered {int(v.agent_raw.notna().sum())} "
          f"({int(v.video_id[v.agent_raw.notna()].nunique())} clips); sources {v.src.value_counts().to_dict()}")
    ends = pd.Series([r.get("end") for r in recs.values()]).value_counts().to_dict() if recs else {}
    steps = [r.get("n_steps", 0) for r in recs.values() if r.get("n_steps")]
    print(f"agent runs: {len(recs)} answers files; ends {ends}; steps/clip {np.mean(steps) if steps else 0:.1f}; "
          f"forced {sum(1 for r in recs.values() if r.get('forced'))}")
    base_macro = score(v.assign(parsed_value=v.base).reset_index())["mra"]
    print(f"base (B2route-equivalent) validation macro MRA {base_macro:.4f}")

    rows, decision = [], {}
    for t in C.TYPES:
        m = v.type == t
        n_ag = int((v.agent_raw.notna() & m & ~st).sum())
        sb, sa, sg = (float(S.loc[m, k].mean()) if m.any() else float("nan") for k in ("base", "agent", "gm"))
        d = S.loc[m, "agent"] - S.loc[m, "base"]
        lo, hi = boot(d, v.video_id[m]) if m.any() else (float("nan"), float("nan"))
        decision[t] = C.decide(sa, sb, n_ag)
        rows.append({"type": t, "questions": int(m.sum()), "clips": int(v.video_id[m].nunique()), "agent_rows": n_ag,
                     "base": sb, "agent": sa, "gm": sg, "agent-base": sa - sb, "boot90_lo": lo, "boot90_hi": hi,
                     "decision": decision[t]})
    R = pd.DataFrame(rows)
    print("\nper clip type (mean item MRA over the type's validation questions; agent = agent else base):")
    print(R.round(4).to_string(index=False))
    final = C.routed(v.base, v.agent_raw, v.type, v.stated, decision)
    rt_macro = score(v.assign(parsed_value=final).reset_index())
    print(f"\nrouted composite on validation: macro {rt_macro['mra']:.4f} (base {base_macro:.4f}); per category "
          + ", ".join(f"{k} {x:.3f}" for k, x in rt_macro["per_category"].items()))
    print("(the composite is scored on the same questions that chose the routing: an optimistic estimate)")
    audit(vdir)
    if a.write:
        out = {"rule": f"agent if agent >= base + {C.MARGIN}; gm(agent, base) if within {C.MARGIN}; base otherwise",
               "decision": decision, "scores": json.loads(R.to_json(orient="records")),
               "val_macro_base": base_macro, "val_macro_routed": rt_macro["mra"], "root": str(Path(a.root).resolve()),
               "written": time.strftime("%Y-%m-%d %H:%M:%S")}
        Path(a.routing).write_text(json.dumps(out, indent=2))
        print(f"\nwrote {a.routing}: {decision}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
