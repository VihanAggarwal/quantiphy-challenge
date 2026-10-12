"""Build submissions/trackB_v2_median4_famrules.csv: Track B log-median of the four open-weight methods
(scripts/trackb_build.py --combine median, raw) + qp.postprocess preset 'trackb' (scripts/postprocess.py).

    .venv/bin/python research/trackb_rules/build_v2.py [RUN_DIR]     # default /tmp/claude-0/tb2/x/trackb_v1"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import common  # noqa: E402
from common import ROOT, load_split, median4  # noqa: E402

OUT = Path(__file__).parent / "out"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        common.RUN = Path(sys.argv[1])
    OUT.mkdir(exist_ok=True)
    t = load_split("test")
    raw = median4("test", t.qid)
    pd.DataFrame({"id": t.qid, "parsed_value": raw.to_numpy()}).to_csv(OUT / "trackB_median4_raw_test.csv", index=False)
    py = sys.executable
    subprocess.run([py, str(ROOT / "scripts/postprocess.py"), str(OUT / "trackB_median4_raw_test.csv"),
                    str(OUT / "trackB_v2_post_test.csv"), "--preset", "trackb", "--log", str(OUT / "trackB_v2_log.csv")],
                   check=True)
    subprocess.run([py, str(ROOT / "scripts/make_submission.py"), str(OUT / "trackB_v2_post_test.csv"),
                    str(ROOT / "submissions/trackB_v2_median4_famrules.csv")], check=True)
