"""Own candidates on physb2 (test inputs + cached runs + earlier built candidates only; no labels, no API).

 d3simmot_x1035  D3 simulation/segmented MOTION rows that hold the plain 3-run median (no fact, K, pool or rule) and
                 their segmented copies: x1.035. Evidence (label-free): on 30 exact stated-fact rows of D3 sim motion
                 (6 scene families) the 3-run median reads -3.5% (family-clustered 90% CI -4.4%..-2.5%); x1.035 on those
                 rows +.013 per row [-.005, +.038]. No validation rows exist for this subset.
 d2sizeenv       probe 12's D2 size-envelope rows (articulated objects: labelled size = envelope over the animation),
                 transplanted onto physb2 where physb2 still holds probe 8's value. The S2 version was measured +.002
                 (probe 18) and adopted; the D2 version (65 rows) was never uploaded.
 s3p             labsize study's never-uploaded `_s3p` variant: S3 scene captured_0037-0040 lab sizes x0.958 (42 rows).
 sim3d_noguard   the 5 S3 rows the sim3d motion-family transfer skipped only because of its 2x guard (the guarded
                 version scored S3 +.003 in probe 18, which supports the stated-label premise).
 labsize_x097    D3 lab SIZE rows derived from our camera geometry (|ln(value/own geometry)| < .25), excluding rows the
                 Table-6 candidate touches, stated prior numbers, ball identities and the rectified table: x0.97.
                 Evidence: lab ball/prop extents from Claude boxes run 3.6% over precise ellipse fits (path85_lab
                 f-audit, 84 measurements), stated lab sizes read +5.6% (balls) / +8.5% (others) through geometry,
                 D3 lab stated-fact rows +3.4% (15 rows), validation lab sizes median +1.9% (13 rows, eval only).
Each writes submissions/trackA_cand_<name>_on_physb2.csv (changes only its rows) and out/rows_<name>.csv."""
import re, subprocess, tempfile
from common import *
import qp.postprocess as pp

t = pd.read_pickle(OUT / "table.pkl")
L = np.log(t[["d1", "d2", "d3"]].where(t[["d1", "d2", "d3"]] > 0))
t["med3"] = np.exp(L.median(axis=1))
base = t.base.copy()


def write(name, new, note):
    ch = ~np.isclose(new, base, rtol=1e-12)
    assert np.isfinite(new).all() and (new > 0).all()
    assert not (ch & t.overlap).any(), "validation-overlap rows must stay"
    rows = t.loc[ch, ["video_id", "category", "src", "kind", "question"]].assign(old=base[ch], new=new[ch])
    rows.to_csv(OUT / f"rows_{name}.csv")
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": new.index, "parsed_value": new.values}).to_csv(fh, index=False)
    out = SUB / f"trackA_cand_{name}_on_physb2.csv"
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(out)], check=True,
                   stdout=subprocess.DEVNULL)
    print(f"{name}: {int(ch.sum())} rows {t.loc[ch, 'category'].value_counts().to_dict()}, median ratio "
          f"{np.exp(np.log(new[ch] / base[ch]).median()):.3f} | {note}")


def transplant(cand, ref, cats):
    c = read_sub(SUB / cand).reindex(t.index); r = read_sub(SUB / ref).reindex(t.index)
    m = (~np.isclose(c, r, rtol=1e-9)) & np.isclose(base, r, rtol=1e-9) & t.category.isin(cats) & ~t.overlap
    new = base.copy(); new[m] = c[m]
    return new


# 1. D3 sim motion x1.035
facts = pd.read_csv(OUT / "facts_log.csv")
fact_q = set(facts.qid)
pure = (t.category == "D3") & (t.srcg == "sim") & t.motion & np.isclose(base, t.med3, rtol=1e-6) & ~t.index.isin(fact_q)
elig = pure.copy()
key = {(v, pp.norm_question(q)): i for i, v, q in zip(t.index, t.video_id, t.question)}
for q in t.index[(t.category == "D3") & (t.src == "seg") & t.motion & ~pure]:
    o = key.get((pp.twin_original(t.video_id[q]), pp.norm_question(t.question[q])))
    if o is not None and pure.get(o, False) and np.isclose(base[q], base[o], rtol=1e-6) and q not in fact_q:
        elig[q] = True
elig &= ~t.overlap
new = base.copy(); new[elig] = base[elig] * 1.035
write("d3simmot_x1035", new, "D3 sim motion plain-median rows x1.035")

# 2. D2 size envelope (probe 12 D2 part)
new = transplant("trackA_probe12_p8_sizeenv_lat13.csv", "trackA_probe8_p7b_d2fixes_d3labphys.csv", ["D2"])
s2all = read_sub(SUB / "trackA_cand_s2all_on_physb2.csv").reindex(t.index)
taken = ~np.isclose(s2all, base, rtol=1e-9)        # bird-family rows: the mask-measured family values win
new[taken] = base[taken]
write("d2sizeenv", new, "probe-12 D2 size envelope rows (minus the s2all bird-family rows)")

# 3. S3 scene 0037-0040 x0.958
write("s3p", transplant("trackA_cand_labsize_s3p_on_p8.csv", "trackA_cand_labsize_main_on_p8.csv", ["S3"]),
      "labsize _s3p rows")

# 4. sim3d motion families without the 2x guard (extra rows only)
write("sim3d_noguard", transplant("trackA_cand_sim3d_motionfam_on_p8.csv", "trackA_cand_sim3d_motionfam_guard_on_p8.csv", ["S3", "D3"]),
      "sim3d motion-family rows beyond the 2x guard")

# 5. D3 lab size x0.97 on geometry-derived, non-Table-6, non-stated rows
t6 = read_sub(SUB / "trackA_cand_labT6_on_physb2.csv").reindex(t.index)
nums = set()
for p in t[t.src == "lab"].prior:
    for m_ in re.finditer(r"([\d.]+)\s*(cm|mm|m)\b", p):
        v, u = float(m_.group(1)), m_.group(2)
        cm = {"cm": v, "mm": v / 10, "m": v * 100}[u]
        nums |= {round(cm, 4), round(cm / 100, 6)}
special = {6.7, 7.0, 23.2, 4.0, 17.5, 74.5, 60.3, 76.0, 0.067, 0.07, 0.232, 0.04, 0.175, 0.745, 0.603, 0.76}
lab = (t.category == "D3") & (t.src == "lab") & (t.kind == "size") & ~t.overlap
lab &= np.isclose(t6, base, rtol=1e-9)
lab &= np.abs(np.log(base / t.r_geo_value)) < 0.25
lab &= ~pd.Series([any(abs(b - n) <= 1e-6 * max(1, n) for n in nums | special) for b in base], index=t.index)
new = base.copy(); new[lab] = base[lab] * 0.97
write("labsize_x097", new, "D3 lab geometry sizes x0.97 (non-Table-6)")
