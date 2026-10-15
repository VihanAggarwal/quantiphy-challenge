"""Checks for the Track B candidate B1 (research/trackb_v5/build_b1.py).

    .venv/bin/python research/trackb_v5/check_b1.py submissions/trackB_cand_B1.csv

1. Clean inputs: re-runs the build under a Python audit hook and lists every file it opens (and every subprocess);
   fails if any Track A / closed-model answer file is opened. The pseudo-label routing table (member names only) is
   the one development-time Track A dependency (FAQ: disclosed); its contents are printed.
2. Value check: every B1 row that differs from v3 and whose value equals a value in any Track A file
   (submissions/trackA_*.csv, research/r86/plan86/trackA_*.csv) is traced to its open-pipeline origin (an open
   member's own value, the L4 formula, or a clamp bound); 2b recomputes the L4 rows from test inputs.
3. Stated-fact rows (research/trackb_dense/out/fact_labels.csv, exact values from the test priors): final answers
   unchanged vs v3; raw (pre-rule) item change of the components on those rows.
4. scripts/make_submission.py accepts the file unchanged.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FORBIDDEN = re.compile(r"trackA|combo|claude|opus|sonnet|gpt|openai|gemini|argon|sol_|muse|runs/(?!_postprocess_cache/)"
                       r"|research/labnoise/out/(?!fit_noise\.json$)", re.I)
# Files that are read but carry no Track A answer value into the output, each verified below:
#  runs/_postprocess_cache/{thumbs,twins,falls}_v3.*  qp.postprocess FrameCache: video-frame thumbnails / twin alignment
#                                                     / fall fits computed from the test videos (model-free)
#  research/labnoise/out/fit_noise.json               loaded at import by research/labnoise/emulate.py (Track A noise fit
#                                                     on Claude tracks); labnoise_open.factors overrides both sigma_z
#                                                     values (0.02 / 0.02 from the open-track fit), checked in 1b
#  research/path85b_phys/changes_ffbd.csv             L4: only `new` is used; it is recomputed from the stated
#                                                     acceleration, question time, fps and model-free t0 in 2b


def audit_build(out: str):
    opened, procs = [], []

    def hook(ev, args):
        if ev == "open" and args and isinstance(args[0], (str, bytes, Path)):
            opened.append(str(args[0]))
        elif ev == "subprocess.Popen":
            procs.append(" ".join(map(str, args[1])) if len(args) > 1 and isinstance(args[1], (list, tuple)) else str(args))

    sys.addaudithook(hook)
    sys.path.insert(0, str(HERE))
    import build_b1  # noqa: E402
    build_b1.main(["--out", out])
    return opened, procs


def main():
    sub = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "submissions/trackB_cand_B1.csv")
    tmp = Path(tempfile.mkdtemp()) / "B1_audit.csv"
    opened, procs = audit_build(str(tmp))
    files = sorted({str(Path(p).resolve()) for p in opened if not p.startswith("/proc") and Path(p).is_file()})
    data = [f for f in files if not re.search(r"/(\.venv|site-packages|lib/python[0-9.]+|__pycache__)/|\.py[c]?$|/usr/", f)]
    bad = [f for f in data if FORBIDDEN.search(f.replace(str(ROOT), "").replace("/tmp/claude-0/", "/tmp/"))]
    print(f"1. build opened {len(data)} data files (code / library files omitted); by directory:")
    for d, n in pd.Series([str(Path(f).parent) for f in data]).value_counts().sort_index().items():
        print(f"     {n:5d}  {d}")
    print("   subprocesses:", procs)
    print("   Track A / closed-model files opened:", bad or "none")
    assert not bad, bad
    rt = ROOT / "research/r86/intel_tb_pseudolabel/routing_base8_min25_k2.csv"
    R = pd.read_csv(rt)
    print("   routing table S2 rows (member names; pl_mra = development-time pseudo-label score, not used by the build):")
    print(R[R.cell.str.startswith("S2")][["cell", "members"]].to_string(index=False))
    print("   S2 fallback set (fallback_category_sets.json):", __import__("json").load(
        open(ROOT / "research/r86/intel_tb_pseudolabel/fallback_category_sets.json"))["S2"])

    # 1b. the Track A noise fit loaded by emulate.py does not reach the L1 factors
    import build_b1 as B  # noqa: E402
    import emulate as EM  # noqa: E402  (imported by labnoise_open.factors)
    D = B.Data()
    D.add_method("cv_geo_only", B.read_csv(B.RUN / "test/cv/cv_geometry.csv", D.test.qid),
                 B.read_csv(B.RUN / "val/cv/cv_geometry.csv", D.val.qid))
    post = B.build(D, ["l2q"])[1]
    f0 = B.LN.factors("test", "qwen", post, 0.02, 0.02)
    keep = dict(EM.PARAMS)
    EM.PARAMS.update(sigma_zb=float("nan"), sigma_zL=float("nan"))
    try:
        f1 = B.LN.factors("test", "qwen", post, 0.02, 0.02)
    finally:
        EM.PARAMS.update(keep)
    same = np.allclose(f0.factor.to_numpy(), f1.factor.to_numpy(), equal_nan=True) and (f0.id.to_numpy() == f1.id.to_numpy()).all()
    print(f"1b. L1 factors with the Track A fit_noise.json sigmas replaced by NaN: identical = {same} "
          f"({int((f0.factor != 1).sum())} rows with factor != 1)")
    assert same

    b1 = pd.read_csv(sub).set_index("id").parsed_value
    au = pd.read_csv(tmp).set_index("id").parsed_value
    assert np.allclose(b1, au.reindex(b1.index), rtol=1e-12), "audited rebuild differs from the submission file"
    print("   audited rebuild == submission file: OK")

    v3 = pd.read_csv(ROOT / "submissions/trackB_v3_catmedian_famrules.csv").set_index("id").parsed_value.reindex(b1.index)
    ch = ~np.isclose(b1, v3, rtol=1e-9)
    hits = {}
    for f in sorted((ROOT / "submissions").glob("trackA_*.csv")) + sorted((ROOT / "research/r86/plan86").glob("trackA_*.csv")):
        a = pd.read_csv(f)
        a = pd.to_numeric(a.set_index(a.columns[0])["parsed_value"], errors="coerce").reindex(b1.index)
        eq = ch & np.isclose(b1, a, rtol=1e-9)
        if eq.any():
            hits[f.name] = b1.index[eq].tolist()
    n_files = len(list((ROOT / "submissions").glob("trackA_*.csv"))) + len(list((ROOT / "research/r86/plan86").glob("trackA_*.csv")))
    rows = sorted({q for v in hits.values() for q in v})
    print(f"2. changed B1 rows: {int(ch.sum())}; rows whose B1 value equals a value in any of {n_files} Track A files: "
          f"{len(rows)}. Open-pipeline origin of each:")
    sys.path.insert(0, str(ROOT / "research/path85b_phys"))
    import build_freefall as FF  # noqa: E402
    t = D.test.set_index("qid")
    pos = pd.Series(np.arange(len(D.test)), index=D.test.qid)
    l4 = {}
    C = pd.read_csv(ROOT / "research/path85b_phys/changes_ffbd.csv")
    C = C[C.qid.map(t.category) == "D2"]
    for ev, (clips, acc, clean) in FF.EVENTS.items():
        t0 = float(FF.T0.loc[clean, "t0"].median())
        for q in C.qid[C.event == ev]:
            m = re.search(r"speed of the .* at time ([0-9.]+)\s*s", t.question[q])
            fps = float(t.fps[q])
            l4[q] = acc * (round(float(m.group(1)) * fps) / fps - t0 - 0.5 / fps)
    l4 = pd.Series(l4)
    unexplained = []
    for q in rows:
        why = []
        if q in l4.index and np.isclose(b1[q], l4[q], rtol=1e-12):
            why.append("L4 formula a*(t_k - t0 - 1/(2 fps))")
        mem = [m for m, P in D.P["test"].items() if np.isfinite(P.iloc[pos[q]]) and np.isclose(b1[q], P.iloc[pos[q]], rtol=1e-9)]
        if mem:
            why.append("open member value " + "/".join(mem))
        if any(np.isclose(b1[q] * B.TO_M.get(str(t.target_unit[q]).strip().lower(), 1.0), x) for x in (1.5, 2.3, 2.0)):
            why.append("clamp bound")
        files = [k for k, v in hits.items() if q in v]
        print(f"     qid {q} ({t.video_id[q]}, {t.category[q]}) B1 {b1[q]:.4g} = {', '.join(why) or 'UNEXPLAINED'}"
              f"  [equal in {len(files)} Track A file(s)]")
        if not why:
            unexplained.append(q)
    print("   unexplained:", unexplained or "none")
    assert not unexplained

    # 2b. L4 values recomputed from the stated acceleration, the question time, the clip fps and the model-free t0
    rec = l4
    ok4 = np.allclose(b1.reindex(rec.index), rec, rtol=1e-12)
    print(f"2b. L4: {len(rec)} D2 rows; B1 value == a*(t_k - t0 - 1/(2 fps)) recomputed from test inputs: {ok4}")
    assert ok4

    from qp.mra import item_scores  # noqa: E402
    fl = pd.read_csv(ROOT / "research/trackb_dense/out/fact_labels.csv", index_col=0)
    fl = fl[fl.index < 100000]
    fch = ~np.isclose(b1.reindex(fl.index), v3.reindex(fl.index), rtol=1e-9)
    print(f"3. stated-fact rows: {len(fl)}; final answer changed vs v3: {int(fch.sum())}"
          + (f" {fl.index[fch].tolist()}" if fch.any() else ""))
    r0 = B.build(D, [])[0].reindex(fl.index)
    for comp in ("s2route", "l2q", "l6s"):
        r1 = B.build(D, [comp])[0].reindex(fl.index)
        m = ~np.isclose(r0, r1, rtol=1e-9, equal_nan=True)
        i0 = item_scores(r0.to_numpy(float), fl.lab.to_numpy(float))
        i1 = item_scores(r1.to_numpy(float), fl.lab.to_numpy(float))
        by = pd.DataFrame({"d": i1 - i0, "c": fl.cat})[m].groupby("c").d.agg(["size", "mean"]).round(3)
        print(f"   raw {comp}: fact rows changed {int(m.sum())}, item {np.nanmean(i0[m]) if m.any() else float('nan'):.3f}"
              f" -> {np.nanmean(i1[m]) if m.any() else float('nan'):.3f}; by category {by.to_dict('index')}")

    chk = Path(tempfile.mkdtemp()) / "resubmit.csv"
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), sub, str(chk)], check=True)
    c2 = pd.read_csv(chk).set_index("id").parsed_value
    assert np.allclose(c2, b1.reindex(c2.index), rtol=0, atol=0), "make_submission changed values"
    print("4. scripts/make_submission.py: passes, values unchanged")


if __name__ == "__main__":
    main()
