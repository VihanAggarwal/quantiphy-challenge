"""Role mixes with the SAM 2 (cvq) tracks on the Qwen spec, validation (480p, as the Colab val run):
which role still limits the best open tracks? Claude tracks = DIAGNOSTIC YARDSTICK ONLY.

    .venv/bin/python research/trackb_next/diag_mix_cvq.py
"""
from __future__ import annotations

import json
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
from diagnose import CLAUDE_RUN, geo, items, macro, renamed, scaled  # noqa: E402
from qp.claude_annotate import load_annotations, with_depth_info  # noqa: E402
from qp.spec import QuestionSpec, RoleTrack  # noqa: E402
from tbcommon import RUN, base_preds, load_dir, questions  # noqa: E402


def main():
    val = questions("val")
    caw = base_preds("val", val.qid)["caw"].reindex(val.qid).to_numpy(float)
    qspecs = {int(q): QuestionSpec.from_dict(v["spec"]) for rec in load_dir(RUN / "val" / "qwen" / "specs").values()
              for q, v in rec.get("questions", {}).items()}
    srcs = {"qwen": load_dir(RUN / "val" / "qwen" / "annotate"), "cvq": load_dir(RUN / "val" / "cvq" / "annotate")}
    dt = dict(zip(val.qid.astype(int), val.depth_info.fillna("")))
    crecs = {p.stem: with_depth_info(json.loads(p.read_text()), dt) for p in sorted((CLAUDE_RUN / "records").glob("*.json"))}
    cann, cmeta = load_annotations(crecs), {r["video_id"]: r["meta"] for r in crecs.values()}
    pri = lambda ts: [t for t in ts if t.role.startswith("prior")]  # noqa: E731
    tar = lambda ts: [t for t in ts if t.role.startswith("target")]  # noqa: E731
    out = {k: [] for k in ("cvq", "cvqP+cT", "cP+cvqT", "qwenP+cvqT", "cvqP+qwenT", "claude")}
    for r in val.itertuples():
        q, spec = int(r.qid), qspecs.get(int(r.qid))
        rec = srcs["qwen"].get(r.video_id)
        size, fps = tuple(rec["meta"]["image_size"]), float(rec["meta"]["fps"])
        tq = [RoleTrack.from_dict(t) for t in rec["tracks"].get(str(q), [])]
        crec = srcs["cvq"].get(r.video_id) or {"tracks": {}}
        tv = [RoleTrack.from_dict(t) for t in crec["tracks"].get(str(q), [])]
        ann = cann.get(q)
        cs = cmeta[r.video_id]["image_size"]
        tc = scaled(renamed(ann.tracks, spec), size[0] / cs[0], size[1] / cs[1]) if ann and spec else []
        out["cvq"].append(geo(spec, tv, size, fps)[0])
        out["cvqP+cT"].append(geo(spec, pri(tv) + tar(tc), size, fps)[0])
        out["cP+cvqT"].append(geo(spec, pri(tc) + tar(tv), size, fps)[0])
        out["qwenP+cvqT"].append(geo(spec, pri(tq) + tar(tv), size, fps)[0])
        out["cvqP+qwenT"].append(geo(spec, pri(tv) + tar(tq), size, fps)[0])
        out["claude"].append(geo(spec, tc, size, fps)[0])
    y, c = val.answer.to_numpy(float), val.category.to_numpy()
    rows = {}
    for k, v in out.items():
        v = np.array(v, float)
        rows[k] = dict(**macro(items(np.where(np.isfinite(v), v, caw), y), c), geo_cov=float(np.isfinite(v).mean()))
    print("geometry with CaW fallback, Qwen spec, 480p validation (159 q)")
    print(pd.DataFrame(rows).T.round(3).to_string())
    it = {k: items(np.where(np.isfinite(np.array(v, float)), np.array(v, float), caw), y) for k, v in out.items()}
    R = val[["qid", "video_id", "category", "tk", "question"]].assign(
        **{f"it_{k}": v for k, v in it.items()}, **{f"v_{k}": np.array(v, float) for k, v in out.items()}, y=y)
    R.to_csv(HERE / "diag_mix_cvq_rows.csv", index=False)
    R["gain_target"] = R["it_cvqP+cT"] - R.it_cvq
    R["gain_prior"] = R["it_cP+cvqT"] - R.it_cvq
    print("\nitem points gained by Claude-quality TARGET tracks on top of cvq (sum, n) per category x target kind")
    print(R.groupby(["category", "tk"]).agg(n=("qid", "size"), gain_target=("gain_target", "sum"),
                                            gain_prior=("gain_prior", "sum"), it_cvq=("it_cvq", "mean")).round(2).to_string())
    print("\nrows with the largest target gains")
    print(R.sort_values("gain_target", ascending=False).head(25)[["qid", "video_id", "category", "tk", "question",
          "it_cvq", "gain_target"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
