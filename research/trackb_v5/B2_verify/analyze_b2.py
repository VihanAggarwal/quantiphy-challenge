"""Verifier: re-derive every row-count / attribution claim of B2_BUILD.md from the independent rebuild (indep_b2.py),
and compare with the builder's B2_rows.csv / B2_spillover.csv / B1clamp_rows.csv.

    .venv/bin/python research/trackb_v5/B2_verify/analyze_b2.py [scratch dir with builder outputs]
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.argv = sys.argv[:1] + sys.argv[1:]
SCR = Path(sys.argv[1]) if len(sys.argv) > 1 else None
sys.path.insert(0, str(Path(__file__).parent))
import indep_b2 as I  # noqa: E402

ROOT, qids, tq = I.ROOT, I.qids, I.tq
SUB = ROOT / "submissions"
HERE5 = ROOT / "research/trackb_v5"
B1, B2, B1C, V3F = (I.sub(SUB / f) for f in ("trackB_cand_B1.csv", "trackB_probe_B2route.csv",
                                            "trackB_cand_B1clamp.csv", "trackB_v3_catmedian_famrules.csv"))
CATS = I.CATS
cat = pd.Series(I.cat, index=qids)
scored = pd.Series(~I.D.dup, index=I.D.test.qid.to_numpy()).reindex(qids)
ALL4 = ("S2", "D2", "S3", "D3")


def pc(mask, scored_only=False):
    m = pd.Series(mask, index=qids).astype(bool)
    return {c: (f"{int((m & (cat == c)).sum())}/{int((m & scored & (cat == c)).sum())}") for c in CATS}


def section(t):
    print("\n## " + t)


section("1. rows changed per category (all/scored), from the files")
print("B2route vs B1 :", pc(I.diff(B2, B1)), "total", int(I.diff(B2, B1).sum()))
print("B2route vs v3 :", pc(I.diff(B2, V3F)))
print("B1clamp vs B1 :", pc(I.diff(B1C, B1)), "total", int(I.diff(B1C, B1).sum()))
print("B1clamp vs v3 :", pc(I.diff(B1C, V3F)))
print("B1 vs v3      :", pc(I.diff(B1, V3F)))
# format: non-value columns identical to B1
for nm in ("trackB_probe_B2route.csv", "trackB_cand_B1clamp.csv"):
    a, b = pd.read_csv(SUB / nm), pd.read_csv(SUB / "trackB_cand_B1.csv")
    print(f"{nm}: rows {len(a)}, columns == B1 columns {list(a.columns) == list(b.columns)}, id order == B1 "
          f"{a.id.tolist() == b.id.tolist()}, non-value columns identical to B1 "
          f"{a.drop(columns='parsed_value').equals(b.drop(columns='parsed_value'))}, all finite > 0 "
          f"{bool((np.isfinite(a.parsed_value) & (a.parsed_value > 0)).all())}, ids unique {a.id.is_unique}")

R1 = I.build(("S2",))
R2 = I.build(ALL4)
section("2. components inside B2route")
# routing table rows per cell + fallback composition
fbrows = {}
for c in ("D2", "S3", "D3"):
    inc = (cat == c).to_numpy()
    routed = np.isin(I.CELL, [r.cell for r in I.RT.itertuples()])
    fbrows[c] = pd.Series(I.CELL[inc & ~routed]).value_counts().to_dict()
print("fallback rows by cell:", fbrows)
print("routed-row empties / to b1set:", {k: v for k, v in R2["info"].items() if "empty" in k or "b1set" in k})
# L2'
lab = I.lab
dq = pd.Series(~np.isclose(I.M["qwen_fov"], I.M["qwen_geo"], rtol=1e-9, equal_nan=True), index=qids)
print("rows where qwen_fov != qwen_geo:", int(dq.sum()), "all lab:", bool(not (dq & ~pd.Series(lab, index=qids)).any()),
      "by category", dq.groupby(cat).sum().to_dict())
pv = R2["prov"]
uses_fov = pv.str.contains("qwen_fov")
print("B2route S3 rows with qwen_fov in their raw set, among qwen_fov!=qwen_geo rows:",
      pd.Series(I.CELL, index=qids)[dq & uses_fov & (cat == "S3")].value_counts().to_dict(),
      "total", int((dq & uses_fov & (cat == "S3")).sum()))
print("B2route D3 rows with qwen_fov in their raw set, among qwen_fov!=qwen_geo rows:",
      int((dq & uses_fov & (cat == "D3")).sum()), "| D3 lab rows where L2' had an effect in B1:",
      int((dq & (cat == "D3") & R1["prov"].str.contains("qwen_fov")).sum()))
# L6s
l6 = pv[pv.str.startswith("l6s|")]
print("L6s rows:", len(l6), "over which routed set:",
      l6.str.replace(r"^l6s\|", "", regex=True).str.replace(r"^cell:([^:]+):(.*)$", r"\1 = \2", regex=True)
      .value_counts().to_dict())
# L1
s1, s2 = set(R1["l1"].index), set(R2["l1"].index)
print(f"L1 rows: B1 {len(s1)}, B2route {len(s2)}, both {len(s1 & s2)}, B1 only {sorted(s1 - s2)}, B2 only {sorted(s2 - s1)}")
# L4
print("L4 rows:", len(R2["l4"]), "final values equal B1:", bool(np.allclose(B2.loc[R2["l4"].index], B1.loc[R2["l4"].index], rtol=1e-12)))
# stated
print("stated rows: B1", len(R1["stated"]), "B2route", len(R2["stated"]), "same set", R1["stated"] == R2["stated"],
      "| final values changed on stated rows:", int(I.diff(B2.loc[sorted(R2["stated"])], B1).sum()))
# clamp
c1, c2 = set(R1["clamp"]), set(R2["clamp"])
print(f"clamp: B1 {len(c1)} {pd.Series(R1['clamp']).value_counts().to_dict()}, B2route {len(c2)} "
      f"{pd.Series(R2['clamp']).value_counts().to_dict()}, both {len(c1 & c2)}, B1 only {len(c1 - c2)}, new {sorted(c2 - c1)}")
b1only = sorted(c1 - c2)
to_m = lambda q, v: v * I.TOM[str(tq.target_unit[q]).lower().strip()]  # noqa: E731
print("   B1-only clamp rows: kinds", pd.Series({q: R1["clamp"][q] for q in b1only}).value_counts().to_dict(),
      "B2route values (m):", f"{min(to_m(q, B2[q]) for q in b1only):.3f}-{max(to_m(q, B2[q]) for q in b1only):.3f}")
for q in sorted(c2 - c1):
    print(f"   new clamp row {q} {tq.video_id[q]} {cat[q]} {R2['clamp'][q]}: post-rule {R2['post'][q]:.4g} "
          f"{tq.target_unit[q]} -> {B2[q]:.4g}; raw source {pv[q]}")

section("3. alone / leave-one-out / spill (scored and all)")
raw1 = R1["raw"]
alone, loo = {}, {}
for c in ("D2", "S3", "D3"):
    Ra = I.build(("S2", c))
    ch = I.diff(Ra["final"], B1)
    sp = ch & ~I.diff(Ra["raw"], raw1)
    alone[c] = (ch, sp)
    print(f"route {c} alone vs B1: {pc(ch)} | pool spill (raw unchanged) outside {pc(sp & (cat != c))} inside "
          f"{pc(sp & (cat == c))}")
    Rl = I.build(tuple(x for x in ALL4 if x != c))
    loo[c] = I.diff(B2, Rl["final"])
ch2 = I.diff(B2, B1)
rawch = I.diff(R2["raw"], raw1)
spill = ch2 & ~rawch
print("B2route raw unchanged but final changed (pool spill):", pc(spill))
own = pd.Series([loo[c][q] if c in loo else False for q, c in zip(qids, cat)], index=qids)
other = pd.Series([any(loo[x][q] for x in loo if x != c) for q, c in zip(qids, cat)], index=qids)
inter = ch2 & ~own & ~other
for nm, m in (("own only", ch2 & own & ~other), ("own + other", ch2 & own & other), ("other only", ch2 & ~own & other),
              ("interaction only (no single drop undoes it)", inter)):
    print(f"   {nm:44s} {pc(m)}")
for c in loo:
    print(f"   rows touched by route {c} (leave-one-out) outside {c}: {pc(loo[c] & ch2 & (cat != c))}")
print("   interaction-only rows:", list(qids[inter.to_numpy()]))
for q in (12, 1746):
    print(f"   qid {q}: B1 {B1[q]:.4g} -> B2 {B2[q]:.4g}; alone D2/S3/D3 changed:",
          [bool(alone[c][0][q]) for c in ("D2", "S3", "D3")])

section("4. alternatives")
Rn = I.build(ALL4, l2q_route=False)
d = I.diff(Rn["final"], B2)
print("routed sets verbatim (no L2' inside):", pc(d), "rows", int(d.sum()), "| lab S3 rows among them",
      int((d & pd.Series(lab, index=qids) & (cat == "S3")).sum()))
Rx = I.build(ALL4, l6s=False)
print("routing wins over L6s: raw differs", pc(I.diff(Rx["raw"], R2["raw"])), "| final differs", pc(I.diff(Rx["final"], B2)))
K = I.keep(R2["final"], ("S2", "D2", "S3"), SUB / "trackB_cand_B1.csv")
print("--keep S2,D2,S3 (independent): D3 rows == B1:", not I.diff(K[cat == "D3"], B1).any(),
      "| other rows == B2route:", not I.diff(K[cat != "D3"], B2).any())
if SCR and (SCR / "B2_keep3.csv").exists():
    Kb = I.sub(SCR / "B2_keep3.csv")
    print("builder --keep S2,D2,S3 output == independent keep:", not I.diff(Kb, K).any())

section("5. B1clamp")
chc = I.diff(B1C, B1)
rows = list(qids[chc.to_numpy()])
print("B1clamp changed rows:", rows, pc(chc))
print("   all scored:", bool(scored[chc].all()), "| values (m):", sorted({round(to_m(q, B1C[q]), 4) for q in rows}),
      "| B1 values (m):", sorted({round(to_m(q, B1[q]), 3) for q in rows}))
print("   the 19 rows in B2route (m):", f"{min(to_m(q, B2[q]) for q in rows):.3f}-{max(to_m(q, B2[q]) for q in rows):.3f}",
      {q: round(to_m(q, B2[q]), 3) for q in rows})
Rc = I.build(("S2",), clamp="wide")
print("   independent B1clamp clamp rows", len(Rc["clamp"]), pd.Series(Rc["clamp"]).value_counts().to_dict())
# regex equivalence over all test questions: builder regex vs my token parser
CAR_NEW = (r"\bwidth of the (?:(?!(?:the|a|an|that|which|where|of)\b)[\w'-]+ ){0,4}car\b(?!['’]s\b)"
           r"(?! (?:park|door|window|wheel|tire|tyre|seat|roof|lane|mirror|light|bumper|hood|trunk|space|spot)s?\b)")
ql = tq.question.str.lower()
rx = ql.str.contains(f"(?:{I.CAR1})|(?:{CAR_NEW})", regex=True)
mine = ql.map(I.car_wide)
print("   builder wide regex vs my token parser on all", len(ql), "test questions: disagreements",
      list(ql.index[rx != mine]))
widthcar = ql.str.contains("width") & ql.str.contains(r"\bcars?\b")
print("   questions with 'width' and 'car':", int(widthcar.sum()), "| matched by B1 regex",
      int((widthcar & ql.str.contains(I.CAR1)).sum()), "| by wide", int((widthcar & rx).sum()))
for q in ql.index[widthcar & ~rx]:
    print(f"     not matched: {q} {cat[q]} B1 {B1[q]:.3f} | {tq.question[q]}")
toy = ql.str.contains("toy") | tq.prior.astype(str).str.lower().str.contains("toy")
print("   wide-only matches with 'toy' (skipped):", list(ql.index[rx & ~ql.str.contains(I.CAR1) & toy]),
      "| stated (skipped):", sorted(set(ql.index[rx & ~ql.str.contains(I.CAR1)]) & Rc["stated"]))
phr = pd.Series({q: re.search(r"width of the ([^?]*?car)\b", ql[q]).group(1) for q in ql.index[rx & ~ql.str.contains(I.CAR1)]})
print("   wide-only phrases:", phr.value_counts().to_dict())

section("6. builder row files")
if (HERE5 / "B2_rows.csv").exists():
    BR = pd.read_csv(HERE5 / "B2_rows.csv", index_col=0)
    chs = set(qids[ch2.to_numpy()])
    print("B2_rows.csv rows", len(BR), "| changed==True rows", int(BR.changed.sum()), "== my changed set",
          set(BR.index[BR.changed]) == chs)
    myatt = pd.Series({q: "+".join(f"route_{c}" for c in ("D2", "S3", "D3") if loo[c][q]) for q in qids})
    a = BR.attribution.fillna("")
    print("   attribution column == my leave-one-out on all its rows:", bool((a == myatt.reindex(BR.index)).all()))
    print("   raw_changed == mine:", bool((BR.raw_changed == rawch.reindex(BR.index)).all()),
          "| spill == mine:", bool((BR.spill == spill.reindex(BR.index)).all()))
    print("   new value == B2route file:", not I.diff(BR.new.reindex(qids).dropna(), B2).any())
    w = BR[BR.changed].new_winner.str.replace(r"x[0-9.]+ ", "", regex=True)
    kind = np.select([w.str.startswith("clamp"), w.str.startswith("l1"), w.str.startswith("rule:pool"),
                      w.str.startswith("l6s"), w.str.startswith("fallback"), w.str.startswith("cell")],
                     ["clamp", "L1 x routed", "pool rule", "L6s (pooling changed)", "fallback set", "routed cell"], "other")
    print(pd.crosstab(kind, BR[BR.changed].category).to_string())
    # independent check of the 'winner' classification: pool rule applied on the row in B2route (from the rule log)
    lg = R2["log"]
    pooled = set(lg[lg.applied & (lg.rule == "pool")].qid.astype(int))
    wp = set(BR.index[BR.changed & BR.new_winner.str.startswith("rule:pool")])
    print("   rows with winner 'pool rule' == changed rows where pool applied and no later step (L1/L4/clamp/stated):",
          wp == {q for q in chs if q in pooled and q not in R2["l1"].index and q not in R2["clamp"]
                 and q not in R2["l4"].index and q not in R2["stated"]})
if (HERE5 / "B2_spillover.csv").exists():
    SP = pd.read_csv(HERE5 / "B2_spillover.csv")
    idc = next(c for c in SP.columns if c.lower() in ("qid", "id", "unnamed: 0"))
    mine = {q for q in qids[ch2.to_numpy()] if spill[q] or any(loo[x][q] for x in loo if x != cat[q])}
    print(f"B2_spillover.csv lines {len(SP)}, distinct qids {SP[idc].nunique()}; my set (changed and raw-unchanged, or "
          f"touched by another category's routing) {len(mine)}; equal: {set(SP[idc]) == mine}")
    print("   kinds:", SP.kind.value_counts().to_dict() if "kind" in SP else "-")
if (HERE5 / "B1clamp_rows.csv").exists():
    CR = pd.read_csv(HERE5 / "B1clamp_rows.csv", index_col=0)
    print("B1clamp_rows.csv changed rows == mine:", set(CR.index[CR.changed]) == set(rows))

section("7. stated-fact rows (values stated in the test priors) and validation-overlap rows")
from qp.mra import item_scores  # noqa: E402
fl = pd.read_csv(ROOT / "research/trackb_dense/out/fact_labels.csv", index_col=0)
fl = fl[fl.index < 100000]
print("fact rows", len(fl), "final changed vs B1 in B2route", int(I.diff(B2.reindex(fl.index), B1).sum()),
      "| in B1clamp", int(I.diff(B1C.reindex(fl.index), B1).sum()))
r0 = R1["raw"].reindex(fl.index)
for c in ("D2", "S3", "D3"):
    r = I.build(("S2", c))["raw"].reindex(fl.index)
    m = I.diff(r, r0).to_numpy()
    i0, i1 = item_scores(r0.to_numpy(float), fl.lab.to_numpy(float)), item_scores(r.to_numpy(float), fl.lab.to_numpy(float))
    print(f"   raw route {c}: fact rows changed {int(m.sum())}, item {np.nanmean(i0[m]):.3f} -> {np.nanmean(i1[m]):.3f}")
# validation-overlap (unscored) rows: changed, and equal to the validation label?
import qp.postprocess as pp  # noqa: E402
Vv = I.QD.load_validation()
vlab = {(v, pp.norm_question(q)): float(a) for v, q, a in zip(Vv.video_id, Vv.question, Vv.answer)}
dup = ~scored
dupq = qids[dup.to_numpy()]
for nm, s in (("B2route", B2), ("B1clamp", B1C)):
    chd = [q for q in dupq if I.diff(s.loc[[q]], B1).iloc[0]]
    eq = [q for q in chd if np.isclose(s[q], vlab.get((tq.video_id[q], pp.norm_question(tq.question[q])), np.nan), rtol=1e-6)]
    print(f"{nm}: validation-overlap rows {len(dupq)}, changed vs B1 {len(chd)}, equal to their validation label {eq}")
