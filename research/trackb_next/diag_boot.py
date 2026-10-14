"""Clip-bootstrap 90% CIs (2000 resamples of the 24 validation clips) for the diagnosis deltas.

    .venv/bin/python research/trackb_next/diag_boot.py   (after diagnose.py and diag_mix_cvq.py)
"""
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
CATS = ("S2", "D2", "S3", "D3")


def boot(df, a, b, n=2000, seed=0):
    vids = df.video_id.unique()
    idx = {v: np.where(df.video_id.to_numpy() == v)[0] for v in vids}
    cat = df.category.to_numpy()
    A, B = df[a].to_numpy(float), df[b].to_numpy(float)
    rng = np.random.default_rng(seed)
    point = np.mean([B[cat == c].mean() - A[cat == c].mean() for c in CATS])
    out = []
    for _ in range(n):
        s = np.concatenate([idx[v] for v in rng.choice(vids, len(vids))])
        out.append(np.mean([B[s][cat[s] == c].mean() - A[s][cat[s] == c].mean() for c in CATS if (cat[s] == c).any()]))
    return point, np.quantile(out, .05), np.quantile(out, .95)


D = pd.read_csv(HERE / "diag_rows.csv")
from diagnose import items  # noqa: E402
for k in ("QQ", "QC", "CQ", "CC", "PcTq", "PqTc"):
    D[f"it_{k}"] = items(np.where(np.isfinite(D[k]), D[k], D.caw), D.y)
for a, b in (("it_QQ", "it_QC"), ("it_QQ", "it_CQ"), ("it_QQ", "it_PcTq"), ("it_QQ", "it_PqTc")):
    p, lo, hi = boot(D, a, b)
    print(f"{b[3:]:6s} - {a[3:]:6s}: {p:+.3f}  90% CI [{lo:+.3f}, {hi:+.3f}]")
R = pd.read_csv(HERE / "diag_mix_cvq_rows.csv")
for a, b in (("it_cvq", "it_cvqP+cT"), ("it_cvq", "it_cP+cvqT"), ("it_cvq", "it_claude")):
    p, lo, hi = boot(R, a, b)
    print(f"{b[3:]:10s} - {a[3:]:4s}: {p:+.3f}  90% CI [{lo:+.3f}, {hi:+.3f}]")
