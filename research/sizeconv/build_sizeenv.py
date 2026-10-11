"""Task A: size-envelope candidate for articulated objects in 2D simulation clips.

factor(size quantity) = envelope / extent used now, along the image axis the extent runs on:
  envelope = p90 over frames of the segmented-twin mask side when >= MIN_MASK clean frames, else the max over
             frames of Claude's box side (>= MIN_BOX boxes)
  'now'    = the solver's median extent length, when Claude's median box side agrees with it within
             AGREE (the box and the extent line measure the same thing); otherwise the median box/mask side
             (pure temporal envelope, so a box that includes fins, tail or a rider does not count)
  clipped to [1, CAP].
An answer is multiplied by factor(target) when its target is an articulated size, and divided by
factor(prior) when its prior is one (a prior measured too small inflates every answer of the clip).
Twins (simulation_X / simulation_X_segmented) share one factor (geometric mean).

    python research/sizeconv/build_sizeenv.py            # validation evaluation + test candidate
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import RAW, ROOT, load, read_csv  # noqa: E402
import envelope as E  # noqa: E402
from qp.mra import item_scores  # noqa: E402

MIN_MASK, MIN_BOX = 20, 3
AGREE = 0.10        # log(median box side / extent) above this: the box includes parts the extent line leaves out
CAP = 1.25
MISMATCH = 1.5    # box side vs extent beyond this ratio: different parts measured, no factor
BASE = ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv"
OUT = ROOT / "submissions/trackA_cand_sizeenv_on_p8.csv"


def factors(env: pd.DataFrame, cap=CAP, use_mask=True, pct="m_p90") -> pd.DataFrame:
    env = env.copy()
    f, src = [], []
    for r in env.itertuples():
        if r.axis not in ("h", "v") or not np.isfinite(r.cur):
            f.append(1.0); src.append("skip_axis"); continue
        if use_mask and np.isfinite(getattr(r, "n_mask", np.nan)) and r.n_mask >= MIN_MASK:
            env_s, med_s, s = getattr(r, pct), r.m_med, "mask"
        elif np.isfinite(getattr(r, "n_box", np.nan)) and r.n_box >= MIN_BOX:
            env_s, med_s, s = r.box_max, r.box_med, "box"
        else:
            f.append(1.0); src.append("skip_obs"); continue
        bm = getattr(r, "box_med", np.nan)
        rel = bm / r.cur if np.isfinite(bm) else 1.0
        if not 1 / MISMATCH <= rel <= MISMATCH:   # box and extent line describe different things: skip
            f.append(1.0); src.append("skip_mismatch"); continue
        # box much wider than the extent line (fins, tail, wings outside the measured body): temporal envelope
        # only; otherwise the envelope over the extent used now (Claude often already picked the widest frames)
        same = rel < np.exp(AGREE)
        ratio = env_s / r.cur if same else env_s / med_s
        f.append(float(np.clip(ratio, 1.0, cap))); src.append(s + ("" if same else "_temporal"))
    env["f"], env["src"] = f, src
    env["fam"] = env.video_id.str.replace("_segmented", "", regex=False)
    # twins share a factor: geometric mean over the family's records of the same object, dimension and role
    g = env.groupby(["fam", "key", "dim", "role"])["f"].transform(lambda s: float(np.exp(np.log(s).mean())))
    env["f_fam"] = g
    return env


def question_factor(env: pd.DataFrame) -> pd.Series:
    t = env[env.role == "target"].groupby("qid")["f_fam"].first()
    p = env[env.role == "prior"].groupby("qid")["f_fam"].first()
    idx = t.index.union(p.index)
    return (t.reindex(idx).fillna(1.0) / p.reindex(idx).fillna(1.0)).rename("factor")


def evaluate_val(env_val: pd.DataFrame, **kw):
    df, _, _ = load("val_hires")
    from qp.data import load_validation
    gt = load_validation().set_index("qid")
    base = read_csv(RAW["val_hires"], df.index)
    fac = question_factor(factors(env_val, **kw)).reindex(df.index).fillna(1.0)
    new = base * fac
    ch = fac.index[~np.isclose(fac, 1.0)]
    s0 = item_scores(base[ch], gt.answer[ch]); s1 = item_scores(new[ch], gt.answer[ch])
    out = pd.DataFrame({"video": df.video_id[ch], "cat": df.category[ch], "q": df.question[ch].str[:50],
                        "factor": fac[ch].round(3), "gt/base": (gt.answer[ch] / base[ch]).round(3),
                        "s_base": s0, "s_new": s1})
    return out


def main():
    env_test = pd.read_csv(ROOT / "research/sizeconv/out/env_test.csv")
    env_val = pd.read_csv(ROOT / "research/sizeconv/out/env_val.csv")
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400)
    for kw in ({}, {"cap": 1.5}, {"use_mask": False}, {"pct": "m_max"}):
        v = evaluate_val(env_val, **kw)
        print("VAL", kw or "default", "changed", len(v), "mean item base %.3f -> new %.3f" % (v.s_base.mean(), v.s_new.mean()))
    print(evaluate_val(env_val).to_string())

    df, _, _ = load("test")
    base = read_csv(BASE, df.index)
    raw = read_csv(RAW["test"], df.index)
    F = factors(env_test)
    F.to_csv(ROOT / "research/sizeconv/out/env_test_factors.csv", index=False)
    fac = question_factor(F).reindex(df.index).fillna(1.0)
    # eligibility: rows equal to the raw pipeline value, or rescaled clip-wide (p8/raw equal to the clip's
    # median p8/raw within 1%: refine-off re-solves, K scale corrections, twin copies of a rescaled clip).
    # Rows with an idiosyncratic p8/raw are family facts or pools: left untouched.
    rr = (base / raw)
    clip_med = rr.groupby(df.video_id.str.replace("_segmented", "", regex=False)).transform("median")
    eligible = np.isclose(base, raw, rtol=1e-9) | (np.abs(np.log(rr / clip_med)) < 0.01)
    want = ~np.isclose(fac, 1.0)
    apply = want & eligible
    mult = fac.where(apply, 1.0)
    # twin copies: a segmented clip's row that carries its original's answer (same question and prior) follows
    # the original's decision and multiplier, so the twins stay in sync
    key = df.question.str.strip().str.lower() + "|" + df.prior.str.strip().str.lower()
    orig_of = {}
    for q in df.index[df.video_id.str.endswith("_segmented")]:
        o = df.index[(df.video_id == df.video_id[q][:-len("_segmented")]) & (key == key[q])]
        if len(o) == 1 and np.isclose(base[q], base[o[0]], rtol=1e-9):
            orig_of[q] = o[0]
    for q, o in orig_of.items():
        mult[q] = mult[o]
    print("twin copies synced:", len(orig_of), "of which changed:", int(sum(not np.isclose(mult[q], 1) for q in orig_of)))
    out = base * mult
    ch = out.index[~np.isclose(out, base)]
    print("\nTEST: rows wanting a change %d, eligible %d, not eligible %d" % (want.sum(), apply.sum(), (want & ~eligible).sum()))
    print("changed by category", df.category[ch].value_counts().to_dict())
    r = (out[ch] / base[ch])
    print(pd.DataFrame({"cat": df.category[ch], "r": r}).groupby("cat")["r"].describe().round(3))
    print("protected rows (changed=False):", [q for q in fac.index[want & ~eligible] if np.isclose(out[q], base[q])])
    pd.DataFrame({"qid": ch, "video": df.video_id[ch].values, "cat": df.category[ch].values,
                  "q": df.question[ch].values, "base": base[ch].values, "new": out[ch].values,
                  "factor": r.values}).to_csv(ROOT / "research/sizeconv/out/sizeenv_changes.csv", index=False)
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": out.index, "parsed_value": out.values}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(OUT)], check=True)


if __name__ == "__main__":
    main()
