"""Validation evaluation (labels read here only; nothing here sets a test answer).

1. Rows the candidates change that are also validation questions (24 validation videos are test videos; 128 of
   159 validation questions are identical to test questions): item score before / after.
2. Premise check of rule MF: run the same transfer gates on the validation questions (simulation and segmented
   clips, any category) with the TEST scene families and stated priors, and compare the transferred value with the
   validation label.
3. Context for the size / convention checks: label / answer ratios of probe 8 on the validation copies of the
   3D non-lab test questions, by dimension word.
    .venv/bin/python research/sim3d/evaluate_val.py
"""
from __future__ import annotations

import build_candidate as B
from common import ROOT, BASE, load_split, table, read_sub, np, pd
from qp.mra import item_scores


def main():
    full = load_split("test")
    tq = full.set_index("qid")
    val = load_split("val_hires")
    m = val.merge(full[["qid", "video_id", "question"]].rename(columns={"qid": "tqid"}), on=["video_id", "question"],
                  how="left")
    m = m[m.tqid.notna()].copy()
    m["tqid"] = m.tqid.astype(int)
    base = read_sub(BASE, tq.index).parsed_value.astype(float)
    print("1. validation copies of changed rows")
    for name in ("motionfam", "motionfam_guard"):
        c = pd.read_csv(ROOT / f"submissions/trackA_cand_sim3d_{name}_on_p8.csv").set_index("id").parsed_value
        x = m.assign(old=base.reindex(m.tqid).values, new=c.reindex(m.tqid).values)
        ch = x[~np.isclose(x.old, x.new, rtol=1e-9)]
        so, sn = item_scores(ch.old, ch.answer), item_scores(ch.new, ch.answer)
        print(f"   {name}: {len(ch)} changed rows have a validation copy; item score {np.nansum(so):.1f} -> "
              f"{np.nansum(sn):.1f}  " + "; ".join(f"{q}: gt {g:g} {o:.4g}->{n:.4g}" for q, g, o, n in
                                                     zip(ch.tqid, ch.answer, ch.old, ch.new)))
    # 2. premise check on validation questions
    vt = table("val_hires")   # validation clips are test clips: families / stated priors come from the test inputs
    gt = val.set_index("qid").answer
    fam_rows = B.motion_facts(full, vt, pd.Series(1.0, index=vt.index), set())
    print(f"2. premise: validation 3D non-lab speed/accel questions reached by the MF gates: {len(fam_rows)}")
    if len(fam_rows):
        fam_rows["label"] = gt.reindex(fam_rows.qid).values
        fam_rows["err"] = fam_rows.new / fam_rows.label - 1
        for r in fam_rows.itertuples():
            print(f"   val {r.qid} {r.video_id}: {r.question[:60]} | transferred {r.new:.4g} gt {r.label:g} "
                  f"({100 * r.err:+.1f}%)  from {r.line}")
    # 3. probe 8 on validation copies of 3D non-lab rows, by dimension
    t = table()
    x = m[m.tqid.isin(t.index)].copy()
    x["p8"] = base.reindex(x.tqid).values
    x["dim"] = t.dim.reindex(x.tqid).values
    x["kind"] = t.kind.reindex(x.tqid).values
    x["r"] = x.answer / x.p8
    x["s"] = item_scores(x.p8, x.answer)
    print(f"3. probe 8 on the {len(x)} validation copies of 3D non-lab questions: mean item {x.s.mean():.3f}")
    print(x.groupby(["kind", "dim"]).agg(n=("r", "size"), median_label_over_p8=("r", "median"),
                                         item=("s", "mean")).round(3).to_string())


if __name__ == "__main__":
    main()
