"""Step 1 (free): is there a systematic world-AABB bias in Claude's direct size answers on 3D simulation?

If sim size labels were world-axis-aligned bounding boxes of yawed objects, the labels of HORIZONTAL dimensions
(length / width) of elongated objects would exceed the object's own (intrinsic) dimensions, so Claude's direct
answers (which estimate intrinsic sizes) would be systematically LOW on length/width (log(pred/gt) < 0), most
strongly on width of long objects (W|cos| + L|sin| inflates W by up to L/W), while heights stay unbiased.

Data (no new API calls, labels only for evaluation):
  (a) validation: 3D non-lab size questions (val_hires), direct answers of the 3 cached runs
      (val_hr_v1_high, val_hr_v2_high, val_opus_high) and their log-median;
  (b) test stated size facts on 3D simulation rows (qp.postprocess "facts": a size stated as the prior of another
      clip of the scene family), Claude's direct answer = log-median of the 3 test runs (research/simfov table).
  (c) extra: validation 2D simulation size rows (same Blender label pipeline; pipeline answer and direct answer).

    .venv/bin/python research/aabb/step1_bias.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp import postprocess as pp  # noqa: E402
from qp.data import load_split  # noqa: E402
from qp.mra import item_scores  # noqa: E402

ELONG = re.compile(r"\b(?:car|bus|truck|van|boat|ship|yacht|bench|pier|train|tram|plane|airplane|jet|bicycle|bike|"
                   r"motorcycle|sofa|couch|table|bed|desk|canoe|kayak|log|dock|board|trailer|tractor|vehicle|"
                   r"taxi|suv|jeep|limo|bridge|fence|wall|shelf|cabinet|crate|container|piano|rocket|shark|whale|"
                   r"horse|cow|dog|cat|fish|dolphin|crocodile|alligator|deer|lion|tiger|elephant|giraffe)\b", re.I)


def dim_word(q: str) -> str:
    ql = q.lower()
    for w in ("wingspan", "diameter", "radius", "thickness", "depth", "length", "width", "height", "tall", "long",
              "wide"):
        if re.search(rf"\b{w}\b", ql):
            return {"tall": "height", "long": "length", "wide": "width", "radius": "diameter"}.get(w, w)
    return "other"


def obj_noun(q: str) -> str:
    m = re.search(r"\bof (?:the |a |an |three |two )?(.+?)(?:\s*\(|\s+in\s+(?:meters|metres|m\b|cm|centimeters)|"
                  r"\?|？|,|$)", q.strip(), re.I)
    return (m.group(1) if m else q).strip().lower()[:40]


def lmed(df: pd.DataFrame) -> pd.Series:
    with np.errstate(all="ignore"):
        return np.exp(np.log(df.where(df > 0)).median(axis=1, skipna=True))


def direct(path: Path, idx) -> pd.Series:
    d = pd.read_csv(path).set_index("id")
    return pd.to_numeric(d.direct_value, errors="coerce").reindex(idx)


def summarize(df: pd.DataFrame, title: str) -> None:
    """df: columns pred, lab, q (question), video."""
    df = df.copy()
    df["lr"] = np.log(df.pred / df.lab)
    df["dim"] = df.q.map(dim_word)
    df["obj"] = df.q.map(obj_noun)
    df["elong"] = df.obj.str.contains(ELONG)
    df["horiz"] = df.dim.isin(["length", "width"])
    df["score"] = item_scores(df.pred.to_numpy(), df.lab.to_numpy())
    print(f"\n==== {title}: n={len(df)} rows, {df.video.nunique()} clips ====")
    print(f"all: median log(pred/gt) {df.lr.median():+.3f}, mean {df.lr.mean():+.3f}, "
          f"frac under {np.mean(df.lr < 0):.2f}, MRA {df.score.mean():.3f}")

    def agg(g):
        return pd.Series({"n": len(g), "med_lr": g.lr.median(), "mean_lr": g.lr.mean(),
                          "frac_under": np.mean(g.lr < 0), "frac_under_10pct": np.mean(g.lr < -0.105),
                          "frac_over_10pct": np.mean(g.lr > 0.095), "MRA": g.score.mean()})

    print("by dimension word:")
    print(df.groupby("dim").apply(agg, include_groups=False).round(3).to_string())
    print("by (elongated object, horizontal dim):")
    print(df.groupby(["elong", "horiz"]).apply(agg, include_groups=False).round(3).to_string())
    # clip-bootstrap CI of the median-ish signal: mean lr on elongated horizontal minus elongated/other heights
    rng = np.random.default_rng(0)
    vids = df.video.unique()
    eh = df[df.elong & df.horiz]
    if len(eh) >= 3:
        bs = []
        for _ in range(4000):
            k = rng.choice(vids, len(vids))
            x = pd.concat([eh[eh.video == v] for v in k])
            if len(x):
                bs.append(x.lr.mean())
        print(f"elongated horizontal rows: mean log(pred/gt) {eh.lr.mean():+.3f}, clip-bootstrap 90% "
              f"[{np.percentile(bs, 5):+.3f}, {np.percentile(bs, 95):+.3f}] over {eh.video.nunique()} clips")
    # within-clip contrast (removes a clip-wide scale error): mean lr of horizontal dims minus mean lr of heights
    cc = df[df.dim.isin(["length", "width", "height"])].groupby(["video", "horiz"]).lr.mean().unstack()
    cc = cc.dropna()
    if len(cc):
        cc["horiz_minus_height"] = cc[True] - cc[False]
        print("within-clip contrast, mean log(pred/gt) horizontal (True) vs height (False):")
        print(cc.round(3).to_string())
        print(f"  mean contrast over {len(cc)} clips: {cc.horiz_minus_height.mean():+.3f} "
              f"(clips with horizontal lower: {(cc.horiz_minus_height < 0).sum()}/{len(cc)})")
    pd.set_option("display.width", 220)
    print("rows (sorted by log ratio):")
    print(df.sort_values("lr")[["video", "obj", "dim", "pred", "lab", "lr", "score"]].round(3).to_string(index=False))


def main():
    # (a) validation 3D non-lab size rows, val runs
    v = load_split("val_hires").set_index("qid")
    m3 = (v.video_type.str[1] == "3") & (v.video_source != "lab")
    v3 = v[m3]
    runs = {k: direct(ROOT / p, v3.index) for k, p in (("v1", "runs/val_hr_v1_high/val_hires.csv"),
                                                        ("v2", "runs/val_hr_v2_high/val_hires.csv"),
                                                        ("opus", "runs/val_opus_high/val.csv"))}
    med = lmed(pd.DataFrame(runs))
    size_mask = v3.question.map(dim_word) != "other"
    # keep size questions only: those asking a dimension and the unit is a length and not a distance between objects
    is_size = size_mask & ~v3.question.str.contains(r"distance|above the|clear height",
                                                    case=False, regex=True)
    a = pd.DataFrame({"pred": med[is_size], "lab": v3.answer[is_size].astype(float), "q": v3.question[is_size],
                      "video": v3.video_id[is_size].str.replace("_segmented", "", regex=False)})
    summarize(a, "VALIDATION 3D non-lab size rows, 3-run log-median of direct answers (val runs)")
    for k, s in runs.items():
        x = a.assign(pred=s.reindex(a.index))
        x = x[x.pred > 0]
        print(f"  run {k}: n={len(x)} median log(pred/gt) {np.log(x.pred / x.lab).median():+.3f}, "
              f"elong-horiz median "
              f"{np.log(x.pred / x.lab)[x.q.map(dim_word).isin(['length', 'width']) & x.q.map(obj_noun).str.contains(ELONG)].median():+.3f}")

    # (b) test stated size facts on 3D sim rows, test runs (dmed from simfov replay table)
    t = pd.read_csv(ROOT / "research/simfov/out/table.csv").set_index("qid")
    test = load_split("test").set_index("qid")
    _, log = pp.apply_rules(t.dmed.reindex(test.index).fillna(1.0), test.reset_index(), rules=("facts",),
                            speed_guard=0)
    f = log[log.applied].copy()
    f["qid"] = f.qid.astype(int)
    f = f[f.qid.isin(t.index)].set_index("qid")
    f = f[t.kind.reindex(f.index) == "size"]
    b = pd.DataFrame({"pred": t.dmed.reindex(f.index), "lab": f.new.astype(float), "q": test.question.reindex(f.index),
                      "video": test.video_id.reindex(f.index).str.replace("_segmented", "", regex=False)})
    b = b[b.pred > 0]
    summarize(b, "TEST stated size facts on 3D simulation (exact), 3-run log-median of direct answers (test runs)")

    # (c) validation 2D simulation size rows (pipeline geometry answer and direct answer of val_hr_v1_high)
    m2 = (v.video_type.str[1] == "2") & (v.video_source == "simulation")
    v2 = v[m2]
    d1 = pd.read_csv(ROOT / "runs/val_hr_v1_high/val_hires.csv").set_index("id").reindex(v2.index)
    is2 = (v2.question.map(dim_word) != "other") & ~v2.question.str.contains(r"distance|above the",
                                                                              case=False, regex=True)
    for col in ("parsed_value", "direct_value"):
        c = pd.DataFrame({"pred": pd.to_numeric(d1[col], errors="coerce")[is2], "lab": v2.answer[is2].astype(float),
                          "q": v2.question[is2], "video": v2.video_id[is2].str.replace("_segmented", "", regex=False)})
        c = c[c.pred > 0]
        summarize(c, f"VALIDATION 2D simulation size rows, val_hr_v1_high {col}")


if __name__ == "__main__":
    main()
