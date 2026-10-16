"""Candidate: cross-render consensus for lab motion answers (lever (c)).

Lab renders X, Xs, Xx of one camera are the same capture with the background replaced: the foreground pixels, the
event and (as the identical stated priors across renders show) the labels are shared. Our answers for one question
still differ across renders, because each render got its own Claude track (geometry and the label-noise emulator
factor) or its own direct answer. Rule: for every (category, camera key, normalised question) group of lab
speed / path-length / displacement rows with >= 2 renders, every row takes the group's log-median (n = 3: the
middle value; n = 2: geometric mean). Never across a/b cameras (left/right naming flips between cameras, e.g.
0034a vs 0034b). Accelerations untouched. No lab motion row is a stated-fact row (master.pkl fact column empty).

Built ON TOP of submissions/trackA_probe_agent_sim2agent.csv; only the pooled lab motion rows change.
Usage: build_pool.py [--write]"""
import sys, subprocess, tempfile
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from qp.data import load_test

OUT = Path(__file__).resolve().parent / "out"
BASE = ROOT / "submissions/trackA_probe_agent_sim2agent.csv"
t = load_test().set_index("qid")
b = pd.read_csv(BASE)
base = b.rename(columns={b.columns[0]: "id"}).set_index("id").parsed_value.astype(float).reindex(t.index)
R = pd.read_pickle(OUT / "labmot_rows.pkl")
assert np.allclose(R.best, base.reindex(R.index))
R = R[R.kind.isin(["speed", "path_length", "displacement"]) & R.fact.isna()].copy()
# exclusions fixed before building: 2891 (0054bx soccer displacement) keeps its reviewed looming-geometry value
# (research/verify_labdist: the 0054b/0054bs value it would be pooled to is one measurement copied twice); the soccer
# ball at 0.5 s in 0054a/b renders is near rest, where the emulator does not apply and the label model is unknown.
EXCL = {2891, 2836, 2848, 2859, 2871, 2883, 2895}
R = R[~R.index.isin(EXCL)]
R["key"] = R.video_id.str.replace(r"(captured_\d{4}[ab]?)[sxX]$", r"\1", regex=True)
R["nq"] = R.question.str.lower().str.replace(r"[^a-z0-9.]", "", regex=True)
new = base.copy()
for _, g in R.groupby(["category", "key", "nq"]):
    if len(g) < 2:
        continue
    lv = np.log(g.best.to_numpy())
    pooled = float(np.exp(np.median(lv)))
    new.loc[g.index] = pooled
chg = ~np.isclose(new, base, rtol=1e-9)
D = pd.DataFrame({"video": t.video_id, "category": t.category, "source": t.video_source, "old": base, "new": new})[chg]
D = D.join(R[["kind", "scored", "overlap"]])
D["ratio"] = D.new / D.old
pd.set_option("display.width", 220); pd.set_option("display.max_rows", 200)
print("rows changed:", len(D), "| >2% change:", int((np.abs(np.log(D.ratio)) > np.log(1.02)).sum()))
print(D.groupby(["category", "source", "kind"]).size())
print("scored (old set) rows changed:", int(D.scored.fillna(False).sum()), "| validation-overlap rows:", int(D.overlap.fillna(False).sum()))
print(D.round(4).to_string())
if "--write" in sys.argv:
    fn = ROOT / "submissions/trackA_cand_next_labmot.csv"
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": new.index, "parsed_value": new.values}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(fn)], check=True)
    chk = pd.read_csv(fn); chk = chk.rename(columns={chk.columns[0]: "id"}).set_index("id").parsed_value.reindex(t.index)
    d = ~np.isclose(chk, base, rtol=1e-9)
    assert set(t.index[d]) == set(D.index), "unexpected rows differ"
    assert (t.video_source[d] == "lab").all() and t.category[d].isin(["S3", "D3"]).all()
    print("verified:", fn, "differs from base in exactly", int(d.sum()), "lab S3/D3 rows")
    D.to_csv(OUT / "pool_changes.csv")
