"""Adversarial review of research/internet/: stricter, verified internet candidate on probe 8.

Kept (from research/internet/build_candidates.py, unchanged logic):
  FWD    forward one-frame difference for speeds at a time (paper App. D.3), same cap 15% and stated-fact guard,
         EXCEPT internet_0029 (60->50 fps frame dropping: a one-frame difference of the annotators can span a
         dropped frame, so the direction of the correction is unknown; the internet study itself left the clip's
         time base alone).
  WINACC accelerations between asked windows, gated: only when the window speeds differ by >= 5% of their mean
         (internet speed precision on validation is ~4% |log err|; below that the difference is noise). Keeps 0032
         (3 rows, 6.6-16.6%) and 0037 (14%); drops 0039 (dv = 1.9% of v, x0.15 move is a coin flip).
  ACORN  0061 / 0068 "height of the acorn" = 8 cm stated in internet_0067 (same toy acorn, checked on frames).
Dropped:
  TWIN   pooling segmented twins with originals: evaluated on the 7 twins whose original is a validation
         question (labels used for evaluation only): item score sum 6.4 -> 6.4, mean |log err| .0723 -> .0742.
  PHYSB  hypothesis probe; not part of a verified file.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research/internet"))
import build_candidates as bc  # noqa: E402  (module-level code only loads inputs)

OUT = ROOT / "submissions/trackA_cand_internet_verified_on_p8.csv"
SKIP_FWD_VIDEOS = {"internet_0029"}
WIN_MIN_REL_DV = 0.05


def main() -> None:
    base, df = bc.base, bc.df
    cur = base.copy()
    log: list = []
    bc.rule_fwd(cur, log)
    for q in list(cur.index):
        if df.video_id.get(q) in SKIP_FWD_VIDEOS and cur[q] != base[q]:
            log.append((q, "FWD-undo", f"{cur[q]:.4g} -> {base[q]:.4g} (0029 time base ambiguous)"))
            cur[q] = base[q]
    for q, ((a, a0, a1), (b, b0, b1)) in bc.WINACC.items():
        va, vb = cur[a], cur[b]
        rel = abs(vb - va) / ((va + vb) / 2)
        if rel < WIN_MIN_REL_DV:
            log.append((q, "WINACC", f"skip: window speeds {va:.4g} / {vb:.4g} differ by {rel:.1%} < 5%"))
            continue
        new = abs(vb - va) / ((b0 + b1) / 2 - (a0 + a1) / 2)
        log.append((q, "WINACC", f"{cur[q]:.4g} -> {new:.4g} (x{new / cur[q]:.3f}; dv {rel:.1%})"))
        cur[q] = new
    bc.rule_acorn(cur, log)
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
        cur.rename("parsed_value").rename_axis("id").reset_index().to_csv(f.name, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), f.name, str(OUT)], check=True,
                   stdout=subprocess.DEVNULL)
    cand = pd.read_csv(OUT).set_index("id").parsed_value
    chg = cand.index[~np.isclose(cand, base.reindex(cand.index), rtol=1e-9)]
    lg = pd.DataFrame(log, columns=["qid", "rule", "note"])
    lg.to_csv(Path(__file__).with_name("log_verified.csv"), index=False)
    print(lg.to_string(index=False))
    print(f"changed {len(chg)} {df.category[chg].value_counts().to_dict()} -> {OUT.name}")


if __name__ == "__main__":
    main()
