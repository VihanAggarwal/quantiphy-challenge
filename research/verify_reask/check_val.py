"""Adversarial re-check of research/reask validation claims (EVALUATION ONLY; no test answers set here).

1. offset-corrected re-ask gain: (alt - base) on a flag minus (alt - base) on all rows of the same source,
   because the stand-in re-asks (val_opus_high = 480p copies, val_hr_v2_high = v2 prompt) are not the test config.
2. which 5th member carries the 3D non-lab high-spread gain (xhigh vs other runs).
3. 2D conf<=0.3 geometric mean of base and one re-ask (the report's +.020, n=20).
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.mra import item_scores  # noqa: E402

r = pd.read_csv(ROOT / "research/reask/val_rows.csv").set_index("qid")
vids = r.video_id.unique()
rng = np.random.default_rng(1)


def col(run, split, c):
    return pd.read_csv(ROOT / run / f"{split}.csv").set_index("id")[c].reindex(r.index)


def boot_d(d, mask, B=4000):
    per = pd.DataFrame({"s": d.where(mask, 0).fillna(0), "n": mask.astype(int), "v": r.video_id}).groupby("v").sum()
    per = per.reindex(vids).fillna(0)
    k = rng.integers(0, len(vids), size=(B, len(vids)))
    sv, nv = per.s.to_numpy()[k].sum(1), per.n.to_numpy()[k].sum(1)
    return per.s.sum() / max(per.n.sum(), 1), *np.percentile(sv / np.maximum(nv, 1), [5, 95])


print("== 1. one re-ask, offset-corrected (flag gain minus same-source all-row gain) ==")
for src in ["ALL", "2D", "lab", "3Dnl"]:
    g = pd.Series(True, index=r.index) if src == "ALL" else (r.src == src)
    for alt in ["v1b", "v2"]:
        d_all = (r[alt] - r.base)[g].mean()
        for fn, f in {"conf<=0.3": r.conf <= .3, "conf<=0.2": r.conf <= .2}.items():
            m = g & f
            if m.sum() < 5:
                continue
            d = (r[alt] - r.base) - d_all
            e, lo, hi = boot_d(d, m)
            print(f"  {src:4s} {alt:3s} {fn:9s} n={int(m.sum()):3d} raw={(r[alt]-r.base)[m].mean():+.3f}"
                  f" all-row offset={d_all:+.3f} corrected={e:+.3f} [{lo:+.3f},{hi:+.3f}]")

print("\n== 2. 3D non-lab high spread: which 5th member carries the gain ==")
D = pd.DataFrame({k: col(*v, "direct_value") for k, v in {
    "v1b": ("runs/val_opus_high", "val"), "v2": ("runs/val_hr_v2_high", "val_hires"),
    "med": ("runs/val_opus_med", "val"), "med2": ("runs/val_opus_med2", "val"),
    "fable": ("runs/val_fable_high", "val"), "xhigh": ("runs/val_opus_xhigh", "val"),
    "v2b": ("runs/val_v2_high", "val")}.items()})
D["base"] = r.direct_value
gm = lambda cs: np.exp(np.log(D[cs].where(D[cs] > 0)).median(axis=1, skipna=True))  # noqa: E731
S = lambda p: pd.Series(item_scores(p.fillna(r.parsed_value), r.answer), index=r.index)  # noqa: E731
m = (r.src == "3Dnl") & (r.dspread3 > .15)
m_all = r.src == "3Dnl"
base3 = S(gm(["base", "v1b", "v2"]))
for fifth in ["xhigh", "fable", "med", "med2"]:
    s5 = S(gm(["base", "v1b", "v2", "v2b", fifth]))
    e, lo, hi = boot_d(s5 - base3, m)
    e2, lo2, hi2 = boot_d(s5 - base3, m_all)
    print(f"  med5(+v2b+{fifth:5s}) - med3: spread>.15 n={int(m.sum())} {e:+.3f} [{lo:+.3f},{hi:+.3f}];"
          f" all 3Dnl n={int(m_all.sum())} {e2:+.3f} [{lo2:+.3f},{hi2:+.3f}]")
for c in D.columns:
    print(f"  single member {c:5s} on spread>.15: {S(D[c])[m].mean():.3f}  (all 3Dnl {S(D[c])[m_all].mean():.3f},"
          f" missing {int(D[c][m_all].isna().sum())})")

print("\n== 3. 2D conf<=0.3: geometric mean of base with one re-ask ==")
m2 = (r.src == "2D") & (r.conf <= .3)
for alt, c in [("v1b", ("runs/val_opus_high", "val")), ("v2", ("runs/val_hr_v2_high", "val_hires"))]:
    a = col(*c, "parsed_value")
    g = np.exp((np.log(r.parsed_value) + np.log(a.where(a > 0).fillna(r.parsed_value))) / 2)
    e, lo, hi = boot_d(S(g) - r.base, m2)
    e2, _, _ = boot_d(S(g) - r.base, r.src == "2D")
    print(f"  gmean(base,{alt}) - base: conf<=0.3 n={int(m2.sum())} {e:+.3f} [{lo:+.3f},{hi:+.3f}]; all 2D {e2:+.3f}")
