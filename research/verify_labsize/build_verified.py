"""Stricter rebuild of the research/labsize main candidate (adversarial review, research/verify_labsize).
Test inputs only; no validation labels are read here.

Changes vs trackA_cand_labsize_main_on_p8.csv (rules as in research/labsize/build_candidate.py):
  TB  table -> 74.5 x 59.6 cm: median over f in {711, 722, 740, 763, 790} of the ALL-8-view rectification
      medians (table_views.measure: 76.8/75.9/74.5/73.6/71.9 x 60.2/59.7/59.6/59.1/58.4). The original 76.0 x 60.3
      came from a 6-view subset at f 711-763 chosen after the validation table label had been seen; the card
      (0038x, +7..+14% at f 722) points to f ~ 780-790, so the f-robust centre is used. Any table length in
      71-78 cm then scores 1.0.
  BI  unchanged (tennis ball 0001, red pendulum ball 0010 = 0027's, 0054 orange ball = basketball; frames checked).
  EL  unchanged (0014 cup / 0.891 [reproduced: sin(ray, table normal) at the cup centre, f 722], notebook length
      17.3 [segmented corners on the 0014 plane give long sides 17.1-19.4; any value in that range beats 12.2],
      pen 14.9 [plane 15.4 reproduced], notebook thickness pooled 1.46).
  RP  render median only where it carries information:
      - skip groups with two renders only (median of two = geometric mean, no consensus),
      - skip groups where no two renders agree within 10% (no consensus: 0018 box width, 0024 book width,
        0062 shopping-bag width),
      - flat objects lying on a surface (book, whiteboard): fronto-parallel readings of a receding side are biased
        low in every render, so a render is only moved UP to the median, never down (0023s book width 9.6 is
        the least foreshortened reading and stays; 0053x 13.7 stays),
      - whiteboard rows are left at probe 8: main's render median moved 0062 length 83 -> 96.6 although the
        study's own floor rectification gives 85.7.
  WB, SP  not included (single-scene, no committed code reproduces the whiteboard numbers; SP is a hedge).

    .venv/bin/python research/verify_labsize/build_verified.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "labsize"))
import build_candidate as bc  # noqa: E402
from common import BASE, ROOT, read_sub  # noqa: E402

TABLE_LONG, TABLE_SHORT = 0.745, 0.596
FLAT = {"book", "note book", "notebook", "whiteboard"}


def build():
    base = read_sub(BASE).parsed_value.astype(float)
    main, log = bc.build("main")
    s = bc.lab_size_rows()
    new = base.copy()
    keep = []
    for _, r in log.iterrows():
        q = r.qid
        if r.rule in ("BI", "EL"):
            new[q] = main[q]
            keep.append((q, r.rule))
        elif r.rule == "TB":
            new[q] = (TABLE_LONG if r.dim == "length" else TABLE_SHORT) / s.loc[q, "usc"]
            keep.append((q, "TB"))
    # RP with the stricter gate, recomputed from probe 8 per (event, question)
    rp = log[log.rule == "RP"]
    for (ev, qn), g in s[s.index.isin(rp.qid)].groupby(["event", "qn"]):
        grp = s[(s.event == ev) & (s.qn == qn)]
        vals = base[grp.index] * grp.usc
        lv = np.log(vals.values)
        if len(grp) < 3:
            continue
        if grp.obj.iloc[0] == "whiteboard":
            continue
        pair_ok = any(abs(lv[i] - lv[j]) <= np.log(1.10) for i in range(len(lv)) for j in range(i + 1, len(lv)))
        if not pair_ok:
            continue
        med = float(np.exp(np.median(lv)))
        for q in grp.index:
            if q not in set(rp.qid):
                continue
            v = vals[q]
            if grp.obj.iloc[0] in FLAT and med < v:
                continue
            new[q] = med / grp.usc[q]
            keep.append((q, "RP"))
    return base, new, pd.DataFrame(keep, columns=["qid", "rule"]), s


if __name__ == "__main__":
    base, new, keep, s = build()
    ch = new.index[(new - base).abs() > 1e-9 * base.abs()]
    k = keep.drop_duplicates("qid").set_index("qid").reindex(ch)
    out = pd.DataFrame({"video": s.loc[ch, "video_id"], "cat": s.loc[ch, "category"], "rule": k.rule,
                        "obj": s.loc[ch, "obj"], "dim": s.loc[ch, "dim"], "p8": base[ch], "new": new[ch]})
    out["ratio"] = out.new / out.p8
    pd.set_option("display.width", 200); pd.set_option("display.max_rows", 200)
    print(out.round(3).to_string())
    print(out.groupby(["rule", "cat"]).agg(n=("p8", "size"), med_ratio=("ratio", "median")).round(3))
    HERE.joinpath("out").mkdir(exist_ok=True)
    out.to_csv(HERE / "out/changes_verified.csv")
    pred = HERE / "out/pred_verified.csv"
    pd.DataFrame({"id": new.index, "parsed_value": new.values}).to_csv(pred, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), str(pred),
                    str(ROOT / "submissions/trackA_cand_labsize_verified_on_p8.csv")], check=True)
