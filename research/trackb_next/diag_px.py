"""2D validation rows: where do the open tracks go wrong, prior pixel motion or target pixel extent?

    .venv/bin/python research/trackb_next/diag_px.py

For every 2D validation question (S2 + D2, 69 rows) the 2D solver is answer = target_px x prior_value / prior_px.
We solve with the Qwen spec on three track sources (Qwen3-VL boxes `qwen`, SAM 2 prompted by Qwen boxes `cvq`,
and - DIAGNOSTIC YARDSTICK ONLY - Claude's Track A tracks rescaled to the same 854 px frame) and compare
prior_px and target_px with the label-implied ratio: an error of the answer splits exactly into
log(answer / gt) = log(target_px / target_px*) - log(prior_px / prior_px*), where only the ratio is identified by the
label; we therefore report each source's prior_px and target_px relative to the Claude source, and the answer error.
"""
from __future__ import annotations

import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "research" / "trackb_dense"))
sys.path.insert(0, str(HERE))
warnings.filterwarnings("ignore")

from diagnose import CLAUDE_RUN, items, renamed, scaled, src_of  # noqa: E402
from qp.claude_annotate import load_annotations, with_depth_info  # noqa: E402
from qp.geometry import solve  # noqa: E402
from qp.spec import QuestionSpec, RoleTrack  # noqa: E402
from tbcommon import RUN, load_dir, questions  # noqa: E402


def main():
    val = questions("val")
    val = val[val.category.isin(["S2", "D2"])].reset_index(drop=True)
    qspecs = {int(q): QuestionSpec.from_dict(v["spec"]) for rec in load_dir(RUN / "val" / "qwen" / "specs").values()
              for q, v in rec.get("questions", {}).items()}
    src = {"qwen": load_dir(RUN / "val" / "qwen" / "annotate"), "cvq": load_dir(RUN / "val" / "cvq" / "annotate"),
           "cv": load_dir(RUN / "val" / "cv" / "annotate")}
    depth_texts = dict(zip(val.qid.astype(int), val.depth_info.fillna("")))
    crecs = {p.stem: with_depth_info(json.loads(p.read_text()), depth_texts)
             for p in sorted((CLAUDE_RUN / "records").glob("*.json"))}
    cann = load_annotations(crecs)
    cmeta = {r["video_id"]: r["meta"] for r in crecs.values()}
    rows = []
    for r in val.itertuples():
        q, spec = int(r.qid), qspecs.get(int(r.qid))
        if spec is None:
            continue
        row = dict(qid=q, video_id=r.video_id, cat=r.category, src=src_of(r.video_id), tk=r.tk, y=r.answer,
                   prior=r.prior[:60], question=r.question[:80])
        size = None
        for name, recs in src.items():
            rec = recs.get(r.video_id)
            if not rec:
                continue
            size = size or rec["meta"]["image_size"]
            tr = [RoleTrack.from_dict(t) for t in rec.get("tracks", {}).get(str(q), [])]
            a = solve(spec, tr, tuple(rec["meta"]["image_size"]), float(rec["meta"]["fps"]))
            row.update({f"{name}_val": a.value, f"{name}_ppx": a.debug.get("prior_px"),
                        f"{name}_tpx": a.debug.get("target_px"), f"{name}_flags": ";".join(a.flags)})
        ann = cann.get(q)
        if ann and r.video_id in cmeta and size:
            cs = cmeta[r.video_id]["image_size"]
            ct = scaled(renamed(ann.tracks, spec), size[0] / cs[0], size[1] / cs[1])
            a = solve(spec, ct, tuple(size), float(src["qwen"][r.video_id]["meta"]["fps"]))
            row.update(claude_val=a.value, claude_ppx=a.debug.get("prior_px"), claude_tpx=a.debug.get("target_px"),
                       claude_flags=";".join(a.flags))
        rows.append(row)
    D = pd.DataFrame(rows)
    for s in ("qwen", "cvq", "cv"):
        D[f"{s}_lp"] = np.log(D[f"{s}_ppx"].astype(float) / D.claude_ppx.astype(float))
        D[f"{s}_lt"] = np.log(D[f"{s}_tpx"].astype(float) / D.claude_tpx.astype(float))
        D[f"{s}_it"] = items(D[f"{s}_val"].astype(float), D.y)
    D["claude_it"] = items(D.claude_val.astype(float), D.y)
    D.to_csv(HERE / "diag_px_rows.csv", index=False)
    print(f"2D rows {len(D)}; item means: " + " ".join(f"{s} {D[f'{s}_it'].mean():.3f}" for s in ("qwen", "cv", "cvq", "claude")))
    for s in ("qwen", "cvq", "cv"):
        lp, lt = D[f"{s}_lp"].abs(), D[f"{s}_lt"].abs()
        print(f"\n{s} vs Claude tracks (|log ratio| of the pixel measurement; n with both):")
        for nm, v in (("prior_px (motion of the prior object, or its extent)", lp), ("target_px (asked extent / motion)", lt)):
            v = v.dropna()
            print(f"  {nm:55s} n {len(v):3d} median {v.median():.3f}  >15% {np.mean(v > math.log(1.15)):.0%}  "
                  f">50% {np.mean(v > math.log(1.5)):.0%}")
        by = D.groupby(["cat", "tk"]).agg(n=("qid", "size"), it=(f"{s}_it", "mean"), it_claude=("claude_it", "mean"),
                                          prior_med=(f"{s}_lp", lambda x: x.abs().median()),
                                          target_med=(f"{s}_lt", lambda x: x.abs().median()))
        print(by.round(3).to_string())
    print("\nlargest Qwen target-extent misses (S2/D2 size rows):")
    sz = D[D.tk == "size"].assign(a=D.qwen_lt.abs()).sort_values("a", ascending=False).head(12)
    print(sz[["qid", "video_id", "question", "qwen_lt", "cvq_lt", "qwen_lp", "cvq_lp", "qwen_it", "cvq_it", "claude_it"]]
          .round(2).to_string(index=False))


if __name__ == "__main__":
    main()
