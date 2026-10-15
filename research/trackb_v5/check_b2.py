"""Checks for the Track B probe B2route and the candidate B1clamp (research/trackb_v5/build_b2.py).

    .venv/bin/python research/trackb_v5/check_b2.py submissions/trackB_probe_B2route.csv submissions/trackB_cand_B1clamp.csv

1. Clean inputs: re-runs both builds under a Python audit hook, lists every data file opened and every subprocess,
   fails if a Track A / closed-model answer file is opened (same FORBIDDEN pattern and allowed exceptions as
   check_b1.py), and asserts the audited rebuilds equal the submission files.
2. Value check: every row that differs from B1 and whose value equals a value in any Track A file
   (submissions/trackA_*.csv, research/r86/plan86/trackA_*.csv) is traced to an open-pipeline origin (an open
   member's own value, a log-median of open members, the L4 formula or a clamp bound).
3. Stated-fact rows (research/trackb_dense/out/fact_labels.csv, values stated in the test priors): final answers
   unchanged vs B1; raw (pre-rule) item change of the routing on those rows, by category.
4. B1clamp: differs from B1 only on clamp rows, all car-width rows matched by the widened regex only.
5. scripts/make_submission.py accepts both files unchanged.
"""
from __future__ import annotations

import itertools
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from check_b1 import FORBIDDEN  # noqa: E402


def audit(argvs):
    opened, procs = [], []

    def hook(ev, args):
        if ev == "open" and args and isinstance(args[0], (str, bytes, Path)):
            opened.append(str(args[0]))
        elif ev == "subprocess.Popen":
            procs.append(" ".join(map(str, args[1])) if len(args) > 1 and isinstance(args[1], (list, tuple)) else str(args))

    sys.addaudithook(hook)
    import build_b2  # noqa: E402
    for av in argvs:
        build_b2.main(av)
    return opened, procs


def main():
    sub2 = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "submissions/trackB_probe_B2route.csv")
    subc = sys.argv[2] if len(sys.argv) > 2 else str(ROOT / "submissions/trackB_cand_B1clamp.csv")
    tmp = Path(tempfile.mkdtemp())
    opened, procs = audit([["--out", str(tmp / "B2.csv")], ["--out", str(tmp / "B1c.csv"), "--route", "S2", "--clamp", "wide"]])
    files = sorted({str(Path(p).resolve()) for p in opened if not p.startswith("/proc") and Path(p).is_file()})
    data = [f for f in files if not __import__("re").search(r"/(\.venv|site-packages|lib/python[0-9.]+|__pycache__)/|\.py[c]?$|/usr/", f)]
    bad = [f for f in data if FORBIDDEN.search(f.replace(str(ROOT), "").replace("/tmp/claude-0/", "/tmp/"))]
    print(f"1. the two builds opened {len(data)} data files (code / library files omitted); by directory:")
    for d, n in pd.Series([str(Path(f).parent) for f in data]).value_counts().sort_index().items():
        print(f"     {n:5d}  {d}")
    print("   subprocesses:", [p.replace(str(tmp), "<tmp>") for p in procs])
    print("   Track A / closed-model files opened:", bad or "none")
    assert not bad, bad
    R = pd.read_csv(ROOT / "research/r86/intel_tb_pseudolabel/routing_base8_min25_k2.csv")
    print("   routing table (member names; n_fit / pl_mra are development-time pseudo-label numbers, not read by the build):")
    print(R[["cell", "n_fit", "members"]].to_string(index=False))
    print("   fallback sets:", __import__("json").load(open(ROOT / "research/r86/intel_tb_pseudolabel/fallback_category_sets.json")))

    import build_b2 as B2  # noqa: E402
    subs = {}
    for name, f, au in (("B2route", sub2, tmp / "B2.csv"), ("B1clamp", subc, tmp / "B1c.csv")):
        s = pd.read_csv(f).set_index("id").parsed_value
        a = pd.read_csv(au).set_index("id").parsed_value
        assert np.allclose(s, a.reindex(s.index), rtol=1e-12), f"audited rebuild differs from {f}"
        print(f"   audited rebuild == {Path(f).name}: OK")
        subs[name] = s

    D = B2.setup()
    t = D.test.set_index("qid")
    b1 = pd.read_csv(B2.B1_FILE).set_index("id").parsed_value.reindex(t.index)
    pos = pd.Series(np.arange(len(D.test)), index=D.test.qid)
    sys.path.insert(0, str(ROOT / "research/path85b_phys"))
    import build_freefall as FF  # noqa: E402
    import re  # noqa: E402
    C = pd.read_csv(ROOT / "research/path85b_phys/changes_ffbd.csv")
    C = C[C.qid.map(t.category) == "D2"]
    l4 = {}
    for ev, (clips, acc, clean) in FF.EVENTS.items():
        t0 = float(FF.T0.loc[clean, "t0"].median())
        for q in C.qid[C.event == ev]:
            m = re.search(r"speed of the .* at time ([0-9.]+)\s*s", t.question[q])
            fps = float(t.fps[q])
            l4[q] = acc * (round(float(m.group(1)) * fps) / fps - t0 - 0.5 / fps)
    l4 = pd.Series(l4)
    members = ["caw", "cv_geo", "cv_geo_only", "cvq_geo", "qwen_geo", "qwen_fov", "qwen_direct", "qwen35", "gemma4"]
    tfiles = sorted((ROOT / "submissions").glob("trackA_*.csv")) + sorted((ROOT / "research/r86/plan86").glob("trackA_*.csv"))
    TA = {}
    for f in tfiles:
        a = pd.read_csv(f)
        TA[f.name] = pd.to_numeric(a.set_index(a.columns[0])["parsed_value"], errors="coerce").reindex(t.index)
    for name, s in subs.items():
        s = s.reindex(t.index)
        ch = B2.changed(s, b1)
        hits = {k: set(t.index[ch & np.isclose(s, a, rtol=1e-9)]) for k, a in TA.items()}
        rows = sorted(set().union(*hits.values()))
        print(f"2. {name}: rows changed vs B1 {int(ch.sum())}; rows whose value equals a value in any of {len(tfiles)} "
              f"Track A files: {len(rows)}. Open-pipeline origin of each:")
        unexplained = []
        for q in rows:
            why = []
            if q in l4.index and np.isclose(s[q], l4[q], rtol=1e-12):
                why.append("L4 formula")
            vals = {m: float(D.P["test"][m].iloc[pos[q]]) for m in members}
            mem = [m for m, v in vals.items() if np.isfinite(v) and np.isclose(s[q], v, rtol=1e-9)]
            if mem:
                why.append("open member value " + "/".join(mem))
            else:
                for k in (2, 3):
                    for ms in itertools.combinations(members, k):
                        x = np.array([vals[m] for m in ms])
                        x = x[np.isfinite(x) & (x > 0)]
                        if len(x) and np.isclose(s[q], np.exp(np.median(np.log(x))), rtol=1e-9):
                            why.append("log-median " + "+".join(ms))
                            break
                    if why:
                        break
            if any(np.isclose(s[q] * B2.TO_M.get(str(t.target_unit[q]).strip().lower(), 1.0), x) for x in (1.5, 2.3, 2.0)):
                why.append("clamp bound")
            n = sum(q in v for v in hits.values())
            print(f"     qid {q} ({t.video_id[q]}, {t.category[q]}) {s[q]:.4g} = {', '.join(why) or 'UNEXPLAINED'}"
                  f"  [equal in {n} Track A file(s)]")
            if not why:
                unexplained.append(q)
        print("   unexplained:", unexplained or "none")
        assert not unexplained

    from qp.mra import item_scores  # noqa: E402
    fl = pd.read_csv(ROOT / "research/trackb_dense/out/fact_labels.csv", index_col=0)
    fl = fl[fl.index < 100000]
    for name, s in subs.items():
        fch = B2.changed(s.reindex(fl.index), b1.reindex(fl.index))
        print(f"3. {name}: stated-fact rows {len(fl)}; final answer changed vs B1: {int(fch.sum())}"
              + (f" {fl.index[fch].tolist()}" if fch.any() else ""))
        assert not fch.any()
    r0 = B2.build(D, list(B2.COMPS), ["S2"])["raw"].reindex(fl.index)
    for rc in (["S2", "D2"], ["S2", "S3"], ["S2", "D3"], ["S2", "D2", "S3", "D3"]):
        r1 = B2.build(D, list(B2.COMPS), rc)["raw"].reindex(fl.index)
        m = B2.changed(r1, r0).to_numpy()
        i0 = item_scores(r0.to_numpy(float), fl.lab.to_numpy(float))
        i1 = item_scores(r1.to_numpy(float), fl.lab.to_numpy(float))
        by = pd.DataFrame({"d": i1 - i0, "c": fl.cat})[m].groupby("c").d.agg(["size", "mean"]).round(3)
        print(f"   raw route {'+'.join(rc[1:])} vs B1 raw: fact rows changed {int(m.sum())}, item "
              f"{np.nanmean(i0[m]) if m.any() else float('nan'):.3f} -> {np.nanmean(i1[m]) if m.any() else float('nan'):.3f};"
              f" by category {by.to_dict('index')}")

    sc = subs["B1clamp"].reindex(t.index)
    chc = B2.changed(sc, b1)
    q = t.question.str.lower()
    old = q.str.contains(B2.CAR_B1, regex=True)
    new = q.str.contains(f"(?:{B2.CAR_B1})|(?:{B2.CAR_NEW})", regex=True)
    extra = t.index[new & ~old]
    print(f"4. B1clamp: rows changed vs B1 {int(chc.sum())} {t.category[chc].value_counts().to_dict()}; rows matched only by"
          f" the widened regex {len(extra)}; changed rows all among them: {set(t.index[chc]) <= set(extra)}")
    assert set(t.index[chc]) <= set(extra)
    for i in extra:
        print(f"     qid {i:5d} {t.category[i]} {t.video_id[i]:26s} B1 {b1[i]:.3f} -> {sc[i]:.3f}  {t.question[i]}")
    for i in t.index[q.str.contains("width") & q.str.contains(r"\bcars?\b") & ~new]:
        print(f"     not matched: qid {i:5d} {t.category[i]} B1 {b1[i]:.3f}  {t.question[i]}")

    for name, f in (("B2route", sub2), ("B1clamp", subc)):
        chk = tmp / f"resub_{name}.csv"
        subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), f, str(chk)], check=True)
        c2 = pd.read_csv(chk).set_index("id").parsed_value
        assert np.allclose(c2, subs[name].reindex(c2.index), rtol=0, atol=0), "make_submission changed values"
        print(f"5. scripts/make_submission.py on {Path(f).name}: passes, values unchanged")


if __name__ == "__main__":
    main()
