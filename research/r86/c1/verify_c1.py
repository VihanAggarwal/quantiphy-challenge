"""Independent verification of submissions/trackA_cand_C1_on_combo3.csv (PLAN A2, C1 micro bundle).

Re-derives the expected change set from the components named in PLAN A2 / loss_audit 8.4 / r86/dsc with its own
parsing, then compares it to the CSV. Reads: test inputs (parquet + template), combo3, C1, the dsc log, and the
validation split for (video_id, question) KEYS only. No label column of any split is read.
"""
from __future__ import annotations

import re
import sys

import numpy as np
import pandas as pd

ROOT = "/home/user/quantiphy-challenge"
sys.path.insert(0, ROOT)
from qp.data import load_template  # noqa: E402

ok = True


def check(cond: bool, msg: str) -> None:
    global ok
    print(("PASS " if cond else "FAIL ") + msg)
    ok &= bool(cond)


# ---------------- inputs (raw parquet, own qid / category derivation) ----------------
d = pd.read_parquet(f"{ROOT}/data/QuantiPhy/test_dataset.parquet")
d["qid"] = np.arange(1, len(d) + 1)
d = d.set_index("qid")
# official category key: inference_type[0] + video_type[1]
d["cat"] = d.inference_type.str[0] + d.video_type.str[1]
tmpl = load_template()
check(list(tmpl.id) == list(d.index), "template ids == parquet row order 1..N")
tp = tmpl.rename(columns={"ground_truth_prior": "prior"})
check(all((tp[c].astype(str).values == d[c].astype(str).values).all() for c in ("video_id", "inference_type", "prior", "fps")),
      "template and parquet agree exactly on video_id/inference_type/prior/fps; "
      f"{int((tp.question.values != d.question.values).sum())} questions carry parquet typo fixes")

B_s = pd.read_csv(f"{ROOT}/submissions/trackA_combo3_on_combo2.csv", dtype=str, keep_default_na=False)
C_s = pd.read_csv(f"{ROOT}/submissions/trackA_cand_C1_on_combo3.csv", dtype=str, keep_default_na=False)
check(list(B_s.columns) == list(C_s.columns) == list(tmpl.columns), "column set/order identical (combo3, C1, template)")
check(len(B_s) == len(C_s) == 3289, "3289 rows each")
other = [c for c in B_s.columns if c != "parsed_value"]
check(B_s[other].equals(C_s[other]), f"all non-value columns identical to combo3 as strings ({len(other)} cols)")
base = B_s.set_index(B_s.id.astype(int)).parsed_value.astype(float)
c1 = C_s.set_index(C_s.id.astype(int)).parsed_value.astype(float)
check(list(base.index) == list(d.index), "ids 1..3289 in order")
diff_str = set(B_s.id[B_s.parsed_value != C_s.parsed_value].astype(int))
moved = set(base.index[~np.isclose(c1, base, rtol=1e-12, atol=0)])
check(diff_str == moved, f"string-level diff set == numeric diff set ({len(moved)} rows)")

# ---------------- expected change set, re-derived ----------------
exp: dict[int, tuple[float, str]] = {}


def put(q: int, v: float, comp: str) -> None:
    assert q not in exp, q
    exp[q] = (float(v), comp)


def prior_num(video: str, key: str) -> float:
    p = d.prior[d.video_id == video].unique()
    assert len(p) == 1
    m = re.search(re.escape(key) + r"\s*=\s*([0-9.]+)", p[0])
    assert m, (video, p)
    return float(m.group(1))


def rows(video: str, pat: str) -> list[int]:
    g = d[(d.video_id == video) & d.question.str.contains(pat, case=False, regex=True)]
    return list(g.index)


# B_fact: bird (0010 prior) on 0012(+seg); wingspan by same factor
bird = prior_num("simulation_0010", "length of the bird")
for v in ("simulation_0012", "simulation_0012_segmented"):
    (L,) = rows(v, r"length of the bird")
    (W,) = rows(v, r"wingspan")
    k = bird / base[L]
    put(L, bird, "B_fact"); put(W, base[W] * k, "B_fact")
# dragon: every dragon body-length question in the test set other than the clip stating it
dragon = prior_num("simulation_0283", "length of the dragon")
drg = d[d.question.str.contains(r"length of the dragon", case=False) & (d.video_id != "simulation_0283")]
print("  dragon body-length rows in test:", list(zip(drg.index, drg.video_id)))
for q in drg.index:
    put(q, dragon, "B_fact")
# C_readme: small-bird body length rows outside 0089
sb = prior_num("simulation_0089", "length of the small bird")
sbr = d[d.question.str.contains(r"length of the small bird", case=False) & (d.video_id != "simulation_0089")]
print("  small-bird length rows in test:", list(zip(sbr.index, sbr.video_id)))
for q in sbr.index:
    put(q, sb, "C_readme")
# D_depthid: 0026(+seg) person speed rows; check depth tracks
dep = {v: d.depth_info[d.video_id == v].unique() for v in ("simulation_0025", "simulation_0026", "simulation_0026_segmented")}
print("  depth_info 0025:", dep["simulation_0025"], "\n  depth_info 0026:", dep["simulation_0026"],
      "\n  depth_info 0026s:", dep["simulation_0026_segmented"])
hum = {v: re.findall(r"human[^=]*=\s*([0-9.]+)", " ".join(x)) for v, x in dep.items()}
check(hum["simulation_0025"] == hum["simulation_0026"] and len(hum["simulation_0025"]) == 2,
      f"0025/0026 human depth track identical {hum['simulation_0025']}")
ps = prior_num("simulation_0025", "speed of the person")
for v in ("simulation_0026", "simulation_0026_segmented"):
    for q in rows(v, r"speed of the person"):
        put(q, ps, "D_depthid")
# AUD_0020: whole clip x 1.8 / person height
g20 = d[d.video_id == "simulation_0020"]
(hq,) = [q for q in g20.index if "height of the person" in d.question[q]]
k20 = 1.8 / base[hq]
for q in g20.index:
    put(q, base[q] * k20, "AUD_0020")
# AUD_CAP: own parse of timed acceleration questions
tre = re.compile(r"acceleration of the (?:moving )?(.+?) at (?:time )?([0-9.]+)\s*s\b", re.I)


def cap_groups(videos):
    out = {}
    for v in videos:
        g = d[(d.video_id == v)]
        hits = [(q, tre.search(s)) for q, s in g.question.items()]
        hits = [(q, m.group(1).lower(), float(m.group(2))) for q, m in hits if m]
        out[v] = hits
    return out


CAP = ["simulation_" + c for c in ("0223", "0224", "0224_segmented", "0253", "0254", "0255", "0255_segmented",
                                    "0256", "0234", "0235")]
# any acceleration question in those clips the regex misses?
for v in CAP:
    acc_all = d[(d.video_id == v) & d.question.str.contains("accel", case=False)].index
    got = {q for q, _, _ in cap_groups([v])[v]}
    check(set(acc_all) == got, f"{v}: all {len(acc_all)} acceleration questions parsed as timed")
for v, hits in cap_groups(CAP).items():
    objs = {o for _, o, _ in hits}
    vals = base[[q for q, _, _ in hits]]
    med = float(np.median(vals))
    ins = vals[(vals / med - 1).abs() <= 0.20 + 1e-12]
    assert len(objs) == 1 and len(ins) >= 2, (v, objs, len(ins))
    for q in ins.index:
        put(q, med, "AUD_CAP")

E = pd.DataFrame([(q, v, c) for q, (v, c) in exp.items()], columns=["qid", "exp", "comp"]).set_index("qid")
E["cat"] = d.cat[E.index]; E["old"] = base[E.index]; E["c1"] = c1[E.index]
E["moves"] = ~np.isclose(E.exp, E.old, rtol=1e-12, atol=0)
check(len(E) == 45, f"expected set size {len(E)} == 45")
check(np.allclose(E.c1, E.exp, rtol=1e-12, atol=0), f"C1 values == re-derived values on all {len(E)} rows "
      f"(max rel diff {float(((E.c1 - E.exp) / E.exp).abs().max()):.2e})")
check(set(E.index[E.moves]) == moved, f"rows that move in C1 ({len(moved)}) == re-derived moving rows "
      f"({int(E.moves.sum())}); nothing else changed")
print(pd.crosstab(E.comp, E.cat, margins=True).to_string())
print("moved per category:", E[E.moves].groupby("cat").size().to_dict(), " set per category:",
      E.groupby("cat").size().to_dict())
check(E[E.moves].groupby("cat").size().to_dict() == {"D2": 11, "D3": 2, "S2": 24, "S3": 2}, "moved S2 24 / D2 11 / S3 2 / D3 2")
cat_c1 = d.cat.copy()
for c in ("S2", "D2", "S3", "D3"):
    m = cat_c1 == c
    print(f"  {c}: rows {int(m.sum())}, changed {int((~np.isclose(c1[m], base[m], rtol=1e-12, atol=0)).sum())}")

# ---------------- dsc consistency, exclusions ----------------
dsc = pd.read_csv(f"{ROOT}/research/r86/dsc/changes_famcons.csv").set_index("qid")
fac = dsc[dsc.lever.isin(["B_fact", "C_readme", "D_depthid"])]
check(set(fac.index) == set(E.index[E.comp.isin(["B_fact", "C_readme", "D_depthid"])]), "fact row set == dsc B/C/D")
check(np.allclose(fac.new, E.exp[fac.index], rtol=1e-12) and np.allclose(fac.old, base[fac.index], rtol=1e-12),
      "dsc B/C/D old == combo3 and new == re-derived")
exc = dsc[dsc.lever.isin(["A_qpool", "E_kin"])]
check(len(exc) == 29 and not (set(exc.index) & set(E.index)), f"A_qpool/E_kin ({len(exc)}) disjoint from C1 set")
check(np.array_equal(c1[exc.index].values, base[exc.index].values), "A_qpool/E_kin rows unchanged vs combo3")
famc = pd.read_csv(f"{ROOT}/research/r86/dsc/cand_famcons_on_combo3.csv").set_index("id").parsed_value
dd = set(famc.index[~np.isclose(famc, c1, rtol=1e-12, atol=0)])
check(dd == (set(exc.index) | (moved - set(fac.index))) and len(dd) == 56,
      f"C1 vs dsc candidate differs on {len(dd)} rows = 29 excluded + 27 audit movers")

# ---------------- validation overlap from keys only ----------------
keys = set()
for path, vc, qc in ((f"{ROOT}/data/QuantiPhy-validation/validation_dataset.csv", "video_id", "question"),):
    hdr = pd.read_csv(path, nrows=0).columns
    vv = pd.read_csv(path, usecols=[vc, qc])  # keys only; label column never loaded
    keys |= {(a, str(b).strip().lower()) for a, b in zip(vv[vc], vv[qc])}
print("  validation csv columns (header only):", list(hdr))
vvid = {k[0] for k in keys}
E["overlap"] = [(d.video_id[q], d.question[q].strip().lower()) in keys for q in E.index]
E["vid_in_val"] = [d.video_id[q] in vvid for q in E.index]
check(not E.overlap.any(), "none of the 45 rows is a validation-overlap (scored=False) row")
print("  C1 rows whose video id appears in validation at all:", int(E.vid_in_val.sum()))
print("  test rows that are validation overlap overall:",
      int(sum((a, b.strip().lower()) in keys for a, b in zip(d.video_id, d.question))))

# ---------------- generic CAP scan (what the audit's '33 rows' could be) ----------------
s2sim = sorted(d.video_id[(d.cat == "S2") & d.video_id.str.startswith("simulation")].unique())
gen = []
for v, hits in cap_groups(s2sim).items():
    if len(hits) < 2:
        continue
    objs = {o for _, o, _ in hits}
    vals = base[[q for q, _, _ in hits]]
    med = float(np.median(vals))
    ins = vals[(vals / med - 1).abs() <= 0.20 + 1e-12]
    gen.append(dict(video=v, objs="/".join(sorted(objs)), n=len(hits), n_in=len(ins), named=v in CAP,
                    overlap=any((v, d.question[q].strip().lower()) in keys for q, _, _ in hits),
                    mv=int((~np.isclose(ins, med, rtol=1e-12)).sum()),
                    mv1=int(((ins / med - 1).abs() > 0.01).sum())))
G = pd.DataFrame(gen)
print(G.to_string(index=False))
q2 = G[(G.n_in >= 2)]
print("  generic: clips with >=2 within +-20%:", len(q2), "rows qualifying:", int(q2.n_in.sum()),
      "moving:", int(q2.mv.sum()), "moving >1%:", int(q2.mv1.sum()))
nm = G[G.named]
print("  named clips: rows", int(nm.n_in.sum()), "moving", int(nm.mv.sum()), "moving >1%", int(nm.mv1.sum()))
mvr = np.abs(np.log(E.exp[E.moves & (E.comp == "AUD_CAP")] / E.old[E.moves & (E.comp == "AUD_CAP")]))
print(f"  AUD_CAP move size: median {np.expm1(np.median(mvr)):.4f}, max {np.expm1(mvr.max()):.4f}")

# ---------------- the audit's "33 qualify / 23 move > 1%" reproduced on the pre-combo3 routed answers -------------
# master.pkl: only answer/key columns are selected; its 'val' (label) column is dropped unread.
M = pd.read_pickle(f"{ROOT}/research/r86/loss_audit/master.pkl")[["video_id", "question", "r_parsed_value"]]
M.index = np.arange(1, len(M) + 1)
raw_q, raw_mv1, raw_named, outside = 0, 0, 0, []
for v, hits in cap_groups(s2sim).items():
    if len(hits) < 2 or any(o == "astronaut" for _, o, _ in hits):
        continue
    x = M.r_parsed_value[[q for q, _, _ in hits]].astype(float)
    med = float(np.median(x)); ins = x[(x / med - 1).abs() <= 0.20]
    if len(ins) < 2:
        continue
    raw_q += len(ins); raw_mv1 += int(((ins / med - 1).abs() > 0.01).sum()); raw_named += len(ins) * (v in CAP)
    outside += [q for q in E.index[E.comp == "AUD_CAP"] if d.video_id[q] == v and q not in ins.index]
print(f"  raw routed base: generic qualify {raw_q}, move >1% {raw_mv1}; named clips qualify {raw_named}")
print("  C1 AUD_CAP rows outside +-20% on the raw base:",
      {q: round(float(E.exp[q] / E.old[q]), 3) for q in outside})
print("\nOVERALL", "PASS" if ok else "FAIL")
