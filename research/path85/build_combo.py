"""Build submissions/trackA_cand_path85_combo.csv on physb2 (= trackA_cand_physb2_on_p21.csv) from the path85 levers
that survived adversarial verification (not refuted, no rule violation). No API, no labels used to set answers.

Levers (one owner per row; the build refuses conflicting edits):
  S2, D2  s2all     = bird family 0088-0091 + name-family stated facts + event/extrapolation fixes
                      MINUS qid 1874 (0171_segmented speed at 0.5 s; operator chosen against the 0171 validation label
                      -> reverted to physb2, per both s2events and s2all verifiers)
  S2, D2  inet_micro = credit-card typo 0040 + gym basketball size pooled 0048/0059/0064
  S3      labmot    = is_stated() unit bug fix + pooling the two 0034 cameras
  D3      d3repool  = family pools/K re-derived on the 3-run ensemble
  D3      NBpool    = teal notebook width/length pooled from our own 0013/0014(/0023/0024) answers (10 rows split off
                      the labT6 candidate; uses no Table-6 value)
NOT included: the Table-6 prop sizes (T6A/T6B rows of labT6): team policy (research/gemini/HANDOFF.md) forbids them and
one verifier flagged them; add with --t6 only after the user approves (writes a separate file).
Validation labels are attached only to REPORT the effect on unscored overlap rows.
    .venv/bin/python research/path85/build_combo.py [--t6]
"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research/path85_strategy"))
from common import read_sub, clustered_boot, N_SCORED, SUB  # noqa: E402
from qp.mra import item_scores  # noqa: E402

T6 = "--t6" in sys.argv
t = pd.read_pickle(ROOT / "research/path85_strategy/out/table.pkl")
base = read_sub(SUB / "trackA_cand_physb2_on_p21.csv").reindex(t.index)
assert np.allclose(base, t.base)
C = lambda n: SUB / f"trackA_cand_{n}_on_physb2.csv"  # noqa: E731
chg = pd.read_csv(ROOT / "research/path85_lab/out/changes_t6.csv")
nb_rows = set(chg.qid[chg.rule == "NBpool"])
t6_rows = set(chg.qid[chg.rule.isin(["T6A", "T6B"])])
REVERT = {1874}

SLOTS = [("s2all", ["S2", "D2"], None), ("inet_micro", ["S2", "D2"], None), ("labmot", ["S3"], None),
         ("d3repool", ["D3"], None), ("labT6", ["D3"], nb_rows)]
if T6:
    SLOTS.append(("labT6", ["S3", "D3"], t6_rows))

out, owner = base.copy(), {}
for name, cats, only in SLOTS:
    c = read_sub(C(name)).reindex(t.index)
    rows = t.index[(~np.isclose(c, base, rtol=1e-9)) & t.category.isin(cats)]
    if only is not None:
        rows = [q for q in rows if q in only]
    tag = name if only is None else (name + ("[NBpool]" if only is nb_rows else "[T6]"))
    for q in rows:
        if q in owner and not np.isclose(out[q], c[q], rtol=1e-9):
            raise SystemExit(f"conflict on qid {q}: {owner[q]} vs {tag}")
        out[q] = c[q]; owner[q] = tag
    print(f"{tag:20s} {cats}: {len(rows)} rows {t.loc[list(rows), 'category'].value_counts().to_dict()}")
for q in REVERT:
    print(f"revert qid {q} ({t.video_id[q]}): {out[q]:.4g} -> physb2 {base[q]:.4g}  [was {owner.get(q)}]")
    out[q] = base[q]; owner.pop(q, None)

# ---- checks
ch = ~np.isclose(out, base, rtol=1e-12)
assert len(out) == 3289 and out.notna().all() and np.isfinite(out).all() and (out > 0).all()
print("changed vs physb2:", int(ch.sum()), t.category[ch].value_counts().to_dict(),
      "| scored:", t.category[ch & ~t.overlap].value_counts().to_dict(),
      "| overlap (unscored):", int((ch & t.overlap).sum()))
u5 = read_sub(SUB / "trackA_u5_s2all_d2all_s3labmot_d3repool.csv").reindex(t.index)
d5 = t.index[~np.isclose(out, u5, rtol=1e-12)]
print("differs from U5 on:", sorted(d5), "(expected 1874 + NBpool" + (" + T6" if T6 else "") + ")")
assert set(d5) == REVERT | nb_rows | (t6_rows if T6 else set())

# ---- report-only: validation overlap rows (unscored on test; partly in-sample, NOT evidence)
m = t.overlap & t.val.notna()
s0, s1 = item_scores(base[m].to_numpy(), t.val[m].to_numpy()), item_scores(out[m].to_numpy(), t.val[m].to_numpy())
d = pd.Series(s1 - s0, index=t.index[m])
mu, lo, hi = clustered_boot(d, t.video_id[m].str.replace("_segmented", ""))
print(f"validation overlap rows n={int(m.sum())}: macro physb2 "
      f"{pd.Series(s0, index=t.index[m]).groupby(t.category[m]).mean().mean():.4f} -> combo "
      f"{pd.Series(s1, index=t.index[m]).groupby(t.category[m]).mean().mean():.4f}; changed rows "
      f"{int((d != 0).sum())}, item sum {d.sum():+.2f}, clustered 90% CI of mean change [{lo:+.4f}, {hi:+.4f}]")

name = "trackA_cand_path85_combo_T6.csv" if T6 else "trackA_cand_path85_combo.csv"
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
    pd.DataFrame({"id": out.index, "parsed_value": out.values}).to_csv(fh, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(SUB / name)], check=True)
f = pd.read_csv(SUB / name)
v = pd.to_numeric(f.parsed_value, errors="coerce")
print(f"re-read {name}: {len(f)} rows, unique ids {f.id.is_unique}, finite>0 {int((np.isfinite(v) & (v > 0)).sum())}")
pd.DataFrame({"qid": t.index[ch], "video": t.video_id[ch], "cat": t.category[ch], "lever": [owner[q] for q in t.index[ch]],
              "overlap": t.overlap[ch], "old": base[ch], "new": out[ch], "ratio": (out / base)[ch]}).to_csv(
    Path(__file__).parent / ("changes_combo_T6.csv" if T6 else "changes_combo.csv"), index=False)
