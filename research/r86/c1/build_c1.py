"""Track A item A2 (PLAN.md section 2): "C1 micro bundle" on combo3.

    .venv/bin/python research/r86/c1/build_c1.py

Base: submissions/trackA_combo3_on_combo2.csv. Output: submissions/trackA_cand_C1_on_combo3.csv (written through
scripts/make_submission.py) and research/r86/c1/changes_C1.csv (one line per changed row).

Inputs used: test inputs (questions, stated priors, depth tracks), the combo3 answers, and fixed a-priori constants.
No test labels. No validation labels: the validation split is read only for (video_id, question) keys, to flag the
unscored overlap rows in the change log; its answer column is dropped before anything else happens.

Components (and nothing else; A_qpool and E_kin rows from research/r86/dsc are deliberately NOT applied):
  B_fact    (7)  research/r86/dsc lever B: stated size facts of the same asset in a clip the families missed.
                 simulation_0012(+seg) bird length -> 0010's stated prior 1.19 m, wingspan rescaled by the same factor;
                 dragon body length 0282/0302/0309 -> 0283's stated prior 0.75 m.
  C_readme  (3)  dsc lever C: small-bird length rows of 0088/0090/0091 -> 0089's stated prior 0.94 m.
  D_depthid (2)  dsc lever D: simulation_0026(+seg) human depth track is byte-identical to 0025's, which states
                 'speed of the person = 1.3m/s' -> 1.3.
  AUD_0020  (3)  loss audit section 8.4: simulation_0020 whole-clip rescale so the person is 1.8 m (canonical adult
                 height; the gravity-prior scale makes the clip ~5x too large). Rows 8, 9, 10 all x 1.8/9.44.
  AUD_CAP  (30)  loss audit section 8.4: S2 sim constant-acceleration pooling on the clips the audit names
                 (0223, 0224(+seg), 0253, 0254, 0255(+seg), 0256, 0234, 0235): every timed acceleration answer of the
                 clip's single non-articulated object takes the clip median when it lies within +-20% of it
                 (at least 2 such rows per clip).
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from qp.data import load_split, load_test  # noqa: E402

OUTD = Path(__file__).resolve().parent
BASE = ROOT / "submissions/trackA_combo3_on_combo2.csv"
OUT = ROOT / "submissions/trackA_cand_C1_on_combo3.csv"
DSC = ROOT / "research/r86/dsc/changes_famcons.csv"

t = load_test().set_index("qid")
sub = pd.read_csv(BASE)
assert list(sub.id) == list(t.index)
base = sub.set_index("id")["parsed_value"].astype(float)
new = base.copy()
log: list[dict] = []


def setv(q: int, v: float, comp: str, why: str) -> None:
    assert comp and q not in {r["qid"] for r in log}, f"qid {q} set twice"
    log.append(dict(qid=q, video_id=t.video_id[q], category=t.category[q], question=t.question[q],
                    old=float(base[q]), new=float(v), ratio=float(v) / float(base[q]), component=comp, why=why))
    new[q] = float(v)


def stated(video: str, pat: str) -> float:
    """A number from a clip's stated prior (test input)."""
    pri = t.prior[t.video_id == video].unique()
    assert len(pri) == 1, (video, pri)
    m = re.search(pat, pri[0])
    assert m, (video, pri[0], pat)
    return float(m.group(1))


# ---- B_fact / C_readme / D_depthid: recomputed from the stated priors, then checked against the dsc log ----------
bird = stated("simulation_0010", r"length of the bird = ([\d.]+)m")
dragon = stated("simulation_0283", r"length of the dragon = ([\d.]+)m")
sbird = stated("simulation_0089", r"length of the small bird = ([\d.]+)m")
person = stated("simulation_0025", r"speed of the person = ([\d.]+)m/s")
assert (bird, dragon, sbird, person) == (1.19, 0.75, 0.94, 1.3)
for q, w in ((6, 7), (1649, 1650)):  # (body length row, wingspan row) of the same clip
    assert "length of the bird" in t.question[q] and "wingspan" in t.question[w] and t.video_id[q] == t.video_id[w]
    k = bird / base[q]
    setv(q, bird, "B_fact", f"0010 stated prior length of the bird = {bird}m (same asset; 0012 = top-down camera)")
    setv(w, base[w] * k, "B_fact", f"wingspan x{k:.3f} (same-clip scale implied by the bird-length fact)")
for q in (992, 1469, 1486):
    assert "length of the dragon" in t.question[q]
    setv(q, dragon, "B_fact", f"0283 stated prior length of the dragon = {dragon}m (same asset)")
for q in (134, 145, 149):
    assert "length of the small bird" in t.question[q]
    setv(q, sbird, "C_readme", f"0089 stated prior length of the small bird = {sbird}m (README: body length = AABB)")
dep = {v: t.depth_info[t.video_id == v].iloc[0] for v in ("simulation_0025", "simulation_0026")}
hum = {v: re.findall(r"distance_human_camera = ([\d.]+)", s) for v, s in dep.items()}
assert hum["simulation_0025"] == hum["simulation_0026"] == ["114.8319", "114.8356"], hum
for q in (1115, 1689):
    assert "speed of the person" in t.question[q] and t.video_id[q].startswith("simulation_0026")
    setv(q, person, "D_depthid", f"0025 identical human depth track {hum['simulation_0025']}, states {person} m/s")

dsc = pd.read_csv(DSC)
keep = dsc[dsc.lever.isin(["B_fact", "C_readme", "D_depthid"])].set_index("qid")
mine = {r["qid"]: r for r in log}
assert set(keep.index) == set(mine) and len(keep) == 12
for q, r in keep.iterrows():  # same rows, same base, same values as the dsc build
    assert np.isclose(r.old, mine[q]["old"], rtol=1e-12) and np.isclose(r.new, mine[q]["new"], rtol=1e-12), q
    assert r.lever == mine[q]["component"]
excluded = dsc[dsc.lever.isin(["A_qpool", "E_kin"])]

# ---- AUD_0020: simulation_0020 rescale to a 1.8 m person -----------------------------------------------------------
PERSON_H = 1.8
rows20 = t.index[t.video_id == "simulation_0020"].tolist()
assert rows20 == [8, 9, 10] and "height of the person" in t.question[8]
k20 = PERSON_H / base[8]
for q in rows20:
    setv(q, base[q] * k20, "AUD_0020", f"clip rescale x{k20:.4f} = {PERSON_H} m person / {base[8]:.3f} m")

# ---- AUD_CAP: S2 sim constant-acceleration pooling --------------------------------------------------------------
CAP_CLIPS = [f"simulation_{c}" for c in ("0223", "0224", "0224_segmented", "0253", "0254", "0255",
                                           "0255_segmented", "0256", "0234", "0235")]
TOL = 0.20
timed_acc = t.question.str.contains("acceleration", case=False) & t.question.str.contains(r"\d\s*s\b", case=True)
cap_report = []
for v in CAP_CLIPS:
    g = t[(t.video_id == v) & timed_acc]
    assert len(g) >= 2 and (g.category == "S2").all(), v
    objs = g.question.str.extract(r"acceleration of the (.+?) at", flags=re.I)[0].str.replace("moving ", "").unique()
    assert len(objs) == 1, (v, objs)  # one object per clip
    vals = base[g.index]
    med = float(np.median(vals))
    inside = vals[(vals / med >= 1 - TOL) & (vals / med <= 1 + TOL)]
    assert len(inside) >= 2, v
    cap_report.append(dict(video_id=v, object=objs[0], n=len(g), n_inside=len(inside), median=med,
                           min_ratio=float((vals / med).min()), max_ratio=float((vals / med).max())))
    for q in inside.index:
        setv(q, med, "AUD_CAP", f"clip median of {len(g)} timed accelerations (all within +-{TOL:.0%}: "
                                f"{(vals / med).min():.3f}-{(vals / med).max():.3f})")

# ---- checks and outputs -----------------------------------------------------------------------------------------
L = pd.DataFrame(log)
vv = load_split("val_hires")[["video_id", "question"]]  # keys only; the answer column is never read
vk = {(a, b.strip().lower()) for a, b in zip(vv.video_id, vv.question)}
L["scored"] = [(a, b.strip().lower()) not in vk for a, b in zip(L.video_id, L.question)]
ch = ~np.isclose(new, base, rtol=1e-12)
moved = set(L.qid[~np.isclose(L.new, L.old, rtol=1e-12)])
assert set(new.index[ch]) == moved, "a row outside the change log moved"
assert np.isfinite(new).all() and (new > 0).all() and len(new) == 3289
assert not set(L.qid) & set(excluded.qid), "an A_qpool / E_kin row was touched"

with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
    pd.DataFrame({"id": new.index, "parsed_value": new.values}).to_csv(fh, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(OUT)], check=True)
chk = pd.read_csv(OUT).set_index("id")["parsed_value"]
assert np.allclose(chk.values, new.values, rtol=1e-12)
cols = ["qid", "video_id", "category", "component", "old", "new", "ratio", "scored", "question", "why"]
L[cols].to_csv(OUTD / "changes_C1.csv", index=False)
pd.DataFrame(cap_report).to_csv(OUTD / "cap_clips.csv", index=False)

pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70); pd.set_option("display.max_rows", 200)
print(L[cols[:-2]].to_string(index=False))
print("\nrows set per component x category:")
print(pd.crosstab(L.component, L.category, margins=True))
print("\nrows that MOVE (|log ratio| > 1e-12) per category (all / scored):")
mv = L[~np.isclose(L.new, L.old, rtol=1e-12)]
print(mv.groupby("category").agg(moved=("qid", "size"), scored=("scored", "sum")).to_string())
print("\nnot applied (dsc A_qpool / E_kin):", len(excluded), excluded.lever.value_counts().to_dict())
print(pd.DataFrame(cap_report).to_string(index=False))
