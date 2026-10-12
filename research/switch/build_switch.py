"""Subset method-switch probes on p21: within a subset, rows that still hold the raw pipeline answer and were routed to
geometry take Claude's direct answer ('direct') or the geometric mean of geometry and direct ('gm'). Family/fact/rule
rows (p21 != raw pipeline) are never touched. Each category gets one switch so one upload measures four.
probe22: S2 internet->direct | D2 simulation static->direct | S3 lab static->direct | D3 lab static->direct
probe23: S2 simulation motion->gm | D2 internet->direct | S3 lab static->gm | D3 lab static->gm"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from qp.data import load_test
t = load_test().set_index("qid"); q = t.question.str.lower()
t["kind"] = np.where(q.str.contains("acceler|veloc|speed|travel"), "motion", "static")
t["src"] = t.video_source.replace({"segmentation": "simulation"})
tr = pd.read_csv(ROOT / "runs/test_v1_high_854/test.csv").set_index("id").reindex(t.index)
p21 = pd.read_csv(ROOT / "submissions/trackA_best_p21.csv"); p21 = p21.rename(columns={p21.columns[0]: "id"}).set_index("id").parsed_value.reindex(t.index)
ok = np.isclose(p21, tr.parsed_value, rtol=1e-6) & tr.method.fillna("").str.startswith("geometry") & (tr.direct_value > 0) & (tr.geo_value > 0)
def sub(cat, src=None, kind=None):
    m = ok & (t.category == cat)
    if src: m &= t.src == src
    if kind: m &= t.kind == kind
    return m
def build(name, specs):
    v = p21.copy()
    for cat, src, kind, how in specs:
        m = sub(cat, src, kind)
        v[m] = tr.direct_value[m] if how == "direct" else np.sqrt(tr.direct_value[m] * tr.geo_value[m])
        r = (v[m] / p21[m]); print(f"{name} {cat} {src or '*'} {kind or '*'} -> {how}: {int(m.sum())} rows, median ratio {r.median():.3f}, |log|>0.1: {int((np.log(r).abs() > 0.1).sum())}")
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": v.index, "parsed_value": v.values}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(ROOT / f"submissions/trackA_{name}.csv")], check=True)
build("probe22_p21_switch_direct", [("S2", "internet", None, "direct"), ("D2", "simulation", "static", "direct"),
                                    ("S3", "lab", "static", "direct"), ("D3", "lab", "static", "direct")])
build("probe23_p21_switch_gm", [("S2", "simulation", "motion", "gm"), ("D2", "internet", None, "direct"),
                                ("S3", "lab", "static", "gm"), ("D3", "lab", "static", "gm")])
