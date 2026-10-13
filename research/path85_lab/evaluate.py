"""Report for the path85_lab candidates (EVALUATION ONLY for validation labels).
(1) Validation overlap rows (lab, 38 questions / 6 events): physb2 vs candidate, video-clustered bootstrap.
(2) Label-free: Table-6 rows scored against Table 6 (premise: Table 6 == label, 10/10 on validation), per category,
    converted to overall MRA with the scored N (S3 538, D3 933)."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]; sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
from qp.data import load_test, load_split
from qp.mra import item_scores
import table6 as T6
t = load_test().set_index("qid")
rd = lambda p: (lambda d: d.rename(columns={d.columns[0]: "id"}).set_index("id").parsed_value.astype(float).reindex(t.index))(pd.read_csv(p))
base = rd(ROOT / "submissions/trackA_cand_physb2_on_p21.csv")
N = {"S2": 553, "D2": 1137, "S3": 538, "D3": 933}
vv = load_split("val_hires"); vk = {(a, b.strip().lower()): ans for a, b, ans in zip(vv.video_id, vv.question, vv.answer)}
t["val_label"] = [vk.get((a, b.strip().lower()), np.nan) for a, b in zip(t.video_id, t.question)]
t["ev"] = t.video_id.str.replace(r"^(captured_\d+[ab]?)[sxX]?$", r"\1", regex=True)
for name in ("labT6", "labmot", "path85lab"):
    c = rd(ROOT / f"submissions/trackA_cand_{name}_on_physb2.csv")
    ch = ~np.isclose(c, base, rtol=1e-9)
    print(f"== {name}: rows changed {int(ch.sum())} {t.loc[ch, 'category'].value_counts().to_dict()}, scored (non-overlap) "
          f"{int((ch & t.val_label.isna()).sum())}")
    v = t[t.val_label.notna() & (t.video_source == "lab")].copy()
    v["s0"] = item_scores(base[v.index], v.val_label); v["s1"] = item_scores(c[v.index], v.val_label)
    d = v[~np.isclose(c[v.index], base[v.index], rtol=1e-9)]
    if len(d):
        rng = np.random.default_rng(0); evs = v.ev.unique()
        dsum = v.groupby("ev").apply(lambda x: (x.s1 - x.s0).sum()).reindex(evs).to_numpy(); cnt = v.groupby("ev").size().reindex(evs).to_numpy()
        idx = rng.integers(0, len(evs), (4000, len(evs))); bs = dsum[idx].sum(1) / cnt[idx].sum(1)
        print(f"   validation lab overlap rows (n={len(v)}, {len(evs)} events): changed {len(d)}; item sum {v.s0.sum():.1f} -> {v.s1.sum():.1f}; "
              f"mean {v.s0.mean():.3f} -> {v.s1.mean():.3f}, 90% clustered CI of change [{np.percentile(bs, 5):+.3f}, {np.percentile(bs, 95):+.3f}]")
        for q, r in d.iterrows():
            print(f"     {r.video_id:16s} {r.question[:60]:60s} label {r.val_label:8.3f} base {base[q]:8.3f} -> {c[q]:8.3f}  {r.s0:.1f}->{r.s1:.1f}")
    # label-free: Table-6 premise on scored rows
    m = [T6.match(a, b) for a, b in zip(t.video_id, t.question)]
    t6 = pd.Series([x[1] if x else np.nan for x in m], index=t.index)
    unit = t.target_unit
    t6 = np.where(unit == "m", t6 / 100, np.where(unit == "mm", t6 * 10, t6))
    t6 = pd.Series(t6, index=t.index)
    sel = ch & t6.notna() & t.val_label.isna() & (t.video_source == "lab")
    if sel.any():
        g0 = item_scores(base[sel], t6[sel]); g1 = item_scores(c[sel], t6[sel])
        df = pd.DataFrame({"cat": t.category[sel], "g": g1 - g0})
        for cat, x in df.groupby("cat"):
            print(f"   if Table 6 == label: {cat} {len(x)} scored rows, +{x.g.sum():.2f} item pts -> overall {x.g.sum() / N[cat] / 4:+.4f}")
