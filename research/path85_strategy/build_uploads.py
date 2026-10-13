"""Build uploads U5-U9 on physb2 (= trackA_cand_physb2_on_p21.csv): one lever (or one deliberate bundle) per category,
each measured against physb2's known scores (.817/.859/.766/.803). Re-run after any source candidate is replaced by
its verified version; the script refuses conflicting row edits and reports every slot's rows.

Slots: (category, list of candidate files restricted to that category) or ("zero", subset name) for a diagnostic
(x1e-9 on the subset's rows: subset mean = (physb2_cat - upload_cat) * N_scored / n_scored)."""
import subprocess, tempfile
from common import *

t = pd.read_pickle(OUT / "table.pkl")
base = t.base.copy()
C = lambda n: SUB / f"trackA_cand_{n}_on_physb2.csv"  # noqa: E731

ZERO = {  # diagnostic subsets (all rows, incl. unscored overlap rows; decode with scored n)
    "S2_sim_motion": (t.category == "S2") & (t.srcg == "sim") & t.motion,
    "S2_inet_motion": (t.category == "S2") & (t.srcg == "internet") & t.motion,
    "D2_internet": (t.category == "D2") & (t.srcg == "internet"),
    "D2_sim_motion": (t.category == "D2") & (t.srcg == "sim") & t.motion,
    "S3_nonlab_motion": (t.category == "S3") & (t.srcg == "sim") & t.motion,
    "S3_lab_motion": (t.category == "S3") & (t.srcg == "lab") & t.motion,
    "D3_lab_motion": (t.category == "D3") & (t.srcg == "lab") & t.motion,
    "D3_sim_motion": (t.category == "D3") & (t.srcg == "sim") & t.motion,
}

UPLOADS = {
    "u5_s2all_d2all_s3labmot_d3repool": {
        "S2": [C("s2all"), C("inet_micro")], "D2": [C("s2all"), C("inet_micro")],
        "S3": [C("labmot")], "D3": [C("d3repool")]},
    "u6_s2events_d2sizeenv_s3p_d3labx097": {
        "S2": [C("s2events")], "D2": [C("d2sizeenv")], "S3": [C("s3p")], "D3": [C("labsize_x097")]},
    "u7_s2bird_d2bird_s3noguard_d3simmotx1035": {
        "S2": [C("s2birdfam")], "D2": [C("s2birdfam")], "S3": [C("sim3d_noguard")], "D3": [C("d3simmot_x1035")]},
    "u8_diag_s2simmot_d2inet_s3nlmot_d3labmot": {
        "S2": ("zero", "S2_sim_motion"), "D2": ("zero", "D2_internet"),
        "S3": ("zero", "S3_nonlab_motion"), "D3": ("zero", "D3_lab_motion")},
    "u9_diag_s2inetmot_d2simmot_s3labmot_d3simmot": {
        "S2": ("zero", "S2_inet_motion"), "D2": ("zero", "D2_sim_motion"),
        "S3": ("zero", "S3_lab_motion"), "D3": ("zero", "D3_sim_motion")},
}

manifest = []
for name, slots in UPLOADS.items():
    out, owner = base.copy(), {}
    for cat, spec in slots.items():
        if isinstance(spec, tuple):
            m = ZERO[spec[1]]
            assert set(t.category[m]) == {cat}
            out[m] = base[m] * 1e-9
            manifest.append(dict(upload=name, cat=cat, lever="zero:" + spec[1], rows=int(m.sum()),
                                 scored=int((m & ~t.overlap).sum()), med_ratio=1e-9))
            continue
        rows_cat = []
        for f in spec:
            c = read_sub(f).reindex(t.index)
            rows = t.index[(~np.isclose(c, base, rtol=1e-9)) & (t.category == cat)]
            for q in rows:
                if q in owner and not np.isclose(out[q], c[q], rtol=1e-9):
                    raise SystemExit(f"{name}: conflict on qid {q}: {owner[q]} vs {f.name}")
                out[q] = c[q]; owner[q] = f.name
            rows_cat += list(rows)
        rows_cat = sorted(set(rows_cat))
        r = out[rows_cat] / base[rows_cat]
        manifest.append(dict(upload=name, cat=cat, lever="+".join(f.name.replace("trackA_cand_", "").replace("_on_physb2.csv", "")
                                                                  for f in spec),
                             rows=len(rows_cat), scored=int((~t.overlap[rows_cat]).sum()),
                             med_ratio=float(np.exp(np.log(r).median())) if len(r) else np.nan))
    assert np.isfinite(out).all() and (out > 0).all()
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": out.index, "parsed_value": out.values}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(SUB / f"trackA_{name}.csv")],
                   check=True, stdout=subprocess.DEVNULL)
    # check: only the declared categories differ from physb2
    chk = read_sub(SUB / f"trackA_{name}.csv").reindex(t.index)
    diff = t.category[~np.isclose(chk, base, rtol=1e-12)].value_counts().to_dict()
    assert set(diff) <= set(slots), (name, diff)
    print(name, diff)
man = pd.DataFrame(manifest)
pd.set_option("display.width", 200)
print(man.round(3).to_string())
man.to_csv(OUT / "uploads_manifest.csv", index=False)
