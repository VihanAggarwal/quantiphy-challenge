"""Base answers the agent is compared with and routed onto: the Track B file submissions/trackB_probe_B2route.csv and its
validation equivalent (CPU, no model, no Track A value).

    .venv/bin/python research/trackb_agent/make_base.py

B2route is built by research/trackb_v5/build_b2.py (routing S2,D2,S3,D3, clamp b1, all components). Its "combined"
table runs the identical pipeline on the validation questions too (validation rows are pooled with the test families,
exactly as for the probe's own validation score .6371); labels are not read here. Writes, in this folder:
    base_val.csv    qid (validation), video_id, base (B2route-equivalent answer; empty where the pipeline has none),
                    stated (value set by a stated-fact rule)
    base_test.csv   id (test), base (= the B2route file, checked against a fresh test-table build), stated
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research" / "trackb_v5"))
B2_FILE = ROOT / "submissions" / "trackB_probe_B2route.csv"


def main() -> int:
    import build_b2 as B2
    from build_b1 import VAL_OFFSET
    D = B2.setup()
    route = ["S2", "D2", "S3", "D3"]
    Rc = B2.build(D, list(B2.COMPS), route, "combined")
    f = Rc["final"]
    vq = D.val.qid.to_numpy()
    val = pd.DataFrame({"qid": vq, "video_id": D.val.video_id.to_numpy(),
                        "base": f.reindex(vq + VAL_OFFSET).to_numpy(),
                        "stated": [int(q + VAL_OFFSET in Rc["stated"]) for q in vq]})
    bad = val[~(val.base > 0)]
    if len(bad):   # the validation pipeline leaves a few rows without a value (scored 0 in build_b2 --val, kept here)
        print(f"validation rows without a B2route value: {bad.qid.tolist()} ({bad.video_id.tolist()})")
    val.to_csv(HERE / "base_val.csv", index=False)
    Rt = B2.build(D, list(B2.COMPS), route, "test")
    sub = pd.read_csv(B2_FILE).set_index("id").parsed_value
    t = Rt["final"].reindex(sub.index)
    same = np.isclose(t.to_numpy(float), sub.to_numpy(float), rtol=1e-9, atol=0)
    print(f"test-table rebuild vs {B2_FILE.name}: {int(same.sum())}/{len(sub)} rows identical")
    assert same.all(), "the B2route rebuild differs from the submission file"
    test = pd.DataFrame({"id": sub.index, "base": sub.to_numpy(), "stated": [int(q in Rt["stated"]) for q in sub.index]})
    test.to_csv(HERE / "base_test.csv", index=False)
    print(f"wrote base_val.csv ({len(val)} rows, {int(val.stated.sum())} stated) and base_test.csv ({len(test)} rows, "
          f"{int(test.stated.sum())} stated)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
