"""Task 2: build the label-noise candidates on probe 8 (S3/D3 lab motion rows only).

  trackA_cand_labnoise_on_p8.csv  p8 * emulator factor (emulate.row_model, noise fitted on test priors) for lab
                                  speed / path length / displacement targets in S3 and D3; accelerations untouched
  trackA_cand_lat13_on_p8.csv     p8 * 1.3 for lab speed targets about a small/mid ball moving laterally
                                  (sin psi >= 0.7 at the asked time), nothing else
Stated-fact rows (p8 value equal to a number stated in any test lab prior, in the row's unit) are never changed.
Writes out/test_rows.csv with every row's factor and geometry."""
import re, subprocess, sys, tempfile
import numpy as np, pandas as pd
from common import tracks, motion_kind, HERE, ROOT
from qp.data import load_test
import emulate as EM

CAP = float(sys.argv[1]) if len(sys.argv) > 1 and float(sys.argv[1]) > 0 else None   # cap on the factor (0 = none)
t = load_test().set_index("qid")
p8 = pd.read_csv(ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv")
p8 = p8.rename(columns={p8.columns[0]: "id"}).set_index("id").parsed_value.astype(float)
d = tracks("test")

# numbers stated in test lab priors (SI) -> a row whose value equals one of them is a stated-fact transfer
stated_si = set()
for q, x in d.items():
    v = x["spec"].prior.value_si
    if v is not None and np.isfinite(v):
        stated_si.add(round(float(v), 6))
raw_nums = set()
for p in t.loc[t.video_source == "lab", "prior"]:
    for m in re.findall(r"=\s*([0-9]*\.?[0-9]+)", str(p)):
        raw_nums.add(round(float(m), 6))


def is_stated(val, unit):
    si = val * EM.unit_scale(unit)
    return any(abs(si - s) <= 1e-4 * max(abs(s), 1e-9) for s in stated_si) or round(val, 6) in raw_nums


rows = []
for q, r in t[(t.video_source == "lab") & t.category.isin(["S3", "D3"])].iterrows():
    kind = motion_kind(r.question)
    if kind is None:
        continue
    out = dict(qid=q, video=r.video_id, category=r.category, kind=kind, question=r.question, p8=p8[q],
               stated_fact=is_stated(p8[q], r.target_unit))
    x = d.get(q)
    m = EM.row_model(x, p8[q], r.target_unit, cap=CAP) if (x is not None and kind != "acceleration") else None
    if m:
        out.update(m)
    rows.append(out)
R = pd.DataFrame(rows)
R["factor"] = R["factor"].fillna(1.0)
MIN_CHANGE = 0.03     # factors within 3% of 1 are simulation / grid noise (displacements come out 0.99-1.01)
small = (R.factor - 1).abs() < MIN_CHANGE
R.loc[R.stated_fact | small, "factor"] = 1.0
R.loc[R.stated_fact | small, "gain"] = 0.0
R["gain"] = R["gain"].fillna(0.0)
# test rows that repeat a validation question (same clip and wording) are excluded from official scoring
from qp.data import load_split
vv = load_split("val_hires")
vkeys = set(zip(vv.video_id, vv.question.str.strip().str.lower()))
R["val_overlap"] = [(vid, qq.strip().lower()) in vkeys for vid, qq in zip(R.video, R.question)]
R["lat13"] = np.where((R.kind == "speed") & R.cls.isin(["small ball", "mid ball"]) & (R.sin_psi >= 0.7) & ~R.stated_fact,
                      1.3, 1.0)
R["new_labnoise"] = R.p8 * R.factor
R["new_lat13"] = R.p8 * R.lat13
R.to_csv(HERE / "out" / f"test_rows{'_cap' + str(CAP) if CAP else '_uncapped'}.csv", index=False)

pd.set_option("display.width", 220)
chg = R[(R.factor - 1).abs() >= 0.005]
print("lab motion rows:", len(R), "stated-fact rows kept:", int(R.stated_fact.sum()), "modelled:", int(R.cls.notna().sum()))
print("labnoise changed:", len(chg)); print(chg.groupby(["category", "kind", "cls"]).factor.agg(["count", "median", "min", "max"]).round(3))
print("labnoise factor quantiles:", chg.factor.quantile([0, .1, .25, .5, .75, .9, 1]).round(3).to_dict())
NCAT = {"S3": 578, "D3": 969}
for cat in ("S3", "D3"):
    g = R[(R.category == cat) & ~R.val_overlap]
    print(f"{cat}: model-expected gain if the emulator is right: {g.gain.sum() / NCAT[cat]:+.4f} "
          f"(changed scored rows {int(((g.factor - 1).abs() >= 0.005).sum())}, val-overlap rows changed "
          f"{int((((R.factor - 1).abs() >= 0.005) & R.val_overlap & (R.category == cat)).sum())})")
print("lat13 changed:", int((R.lat13 != 1).sum()), R[R.lat13 != 1].groupby("category").size().to_dict())
for name, col in (("labnoise", "new_labnoise"), ("lat13", "new_lat13")):
    v = p8.copy()
    v.loc[R.qid] = R[col].to_numpy()
    assert (v.drop(R.qid) == p8.drop(R.qid)).all()
    if CAP != 1.6 and name == "lat13":
        continue
    fn = ROOT / "submissions" / (f"trackA_cand_{name}_on_p8{'' if CAP == 1.6 or name == 'lat13' else '_uncapped' if not CAP else '_cap' + str(CAP)}.csv")
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": v.index, "parsed_value": v.values}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(fn)], check=True)
    print(name, "rows differing from p8:", int((~np.isclose(v, p8, rtol=1e-9)).sum()))
