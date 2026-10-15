"""Independent re-derivation of Track B candidate B1 (verifier; does NOT import build_b1.py).

Re-implements each component from its written definition (B1_BUILD.md / PLAN.md B1) on top of the shared base
(harness.Data member table + qp.postprocess preset "trackb", which reproduces the uploaded v3), then compares the
result with submissions/trackB_cand_B1.csv row by row.

    .venv/bin/python <this> [--scramble-val] [--audit] [--out path]
--scramble-val: replace every validation answer with random numbers before anything is loaded (label-leak test).
--audit:        record every file opened / subprocess spawned.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/home/user/quantiphy-challenge")
OPENED, PROCS = [], []


def hook(ev, args):
    if ev == "open" and args and isinstance(args[0], (str, bytes, Path)):
        OPENED.append(str(args[0]))
    elif ev.startswith("subprocess") or ev == "os.system":
        PROCS.append(repr(args)[:300])


ap = argparse.ArgumentParser()
ap.add_argument("--scramble-val", action="store_true")
ap.add_argument("--audit", action="store_true")
ap.add_argument("--out", default="")
A = ap.parse_args()
if A.audit:
    sys.addaudithook(hook)

for p in (ROOT, ROOT / "research/trackb_dense", ROOT / "research/trackb_v5"):
    sys.path.insert(0, str(p))
import qp.data as QD  # noqa: E402

if A.scramble_val:
    _orig = QD.load_validation

    def _scr(*a, **k):
        df = _orig(*a, **k).copy()
        df["answer"] = np.random.default_rng(123).uniform(0.01, 100, len(df))
        return df
    QD.load_validation = _scr
    import tbcommon as _tbc  # noqa: E402
    _tbc.load_validation = _scr

from qp import postprocess as pp  # noqa: E402
import tbcommon as TBC  # noqa: E402
from harness import Data  # noqa: E402
import labnoise_open as LN  # noqa: E402
from build_v5 import l6s_values  # noqa: E402  (the v5plus L6s definition; checked separately against v5plus raw)

D = Data()
T = D.test.reset_index(drop=True)
qids = T.qid.to_numpy()
cat = T.category.to_numpy()
RUN = TBC.RUN

# ---- members: read the base files myself, cross-check against harness, take re-solved variants from harness
def rd(path):
    d = pd.read_csv(path)
    s = pd.to_numeric(d.rename(columns={d.columns[0]: "id"}).set_index("id")["parsed_value"], errors="coerce").abs()
    return s.where(np.isfinite(s) & (s > 0)).reindex(qids).to_numpy(float)


FILES = {"caw": "caw/caw.csv", "cv_geo": "cv/geometry.csv", "cv_geo_only": "cv/cv_geometry.csv",
         "cvq_geo": "cvq/geometry.csv", "qwen_geo": "qwen/geometry.csv", "qwen_direct": "qwen/direct.csv",
         "qwen35": "qwen35/direct.csv", "gemma4": "gemma4/direct.csv"}
M = {m: rd(RUN / "test" / f) for m, f in FILES.items()}
for m in M:
    if m in D.P["test"]:
        assert np.allclose(M[m], D.P["test"][m].to_numpy(float), equal_nan=True), m
M["qwen_fov"] = D.P["test"]["qwen_fov"].to_numpy(float)


def lmed(ms):
    L = np.log(np.vstack([M[m] for m in ms]))
    L[~np.isfinite(L)] = np.nan
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return np.exp(np.nanmedian(L, 0))


V3 = {"S2": ["caw", "cv_geo", "qwen_direct"], "D2": ["caw", "cv_geo", "qwen_direct", "qwen_geo"],
      "S3": ["cv_geo", "qwen_geo", "qwen_direct"], "D3": ["caw", "qwen_geo", "qwen_direct"]}


def raw_of(l2q=False, s2route=False, l6s=False):
    raw = np.full(len(T), np.nan)
    for c, ms in V3.items():
        ms = [("qwen_fov" if (l2q and c in ("S3", "D3") and m == "qwen_geo") else m) for m in ms]
        raw[cat == c] = lmed(ms)[cat == c]
    info = {}
    if s2route:
        R = pd.read_csv(ROOT / "research/r86/intel_tb_pseudolabel/routing_base8_min25_k2.csv")
        fb = json.load(open(ROOT / "research/r86/intel_tb_pseudolabel/fallback_category_sets.json"))["S2"]

        def kind(u):  # pseudo_tb.py definition
            u = str(u).lower()
            return "A" if ("s^2" in u or "s2" in u or "s²" in u) else ("V" if "/s" in u or "per s" in u else "L")
        cell = (T.category + "|" + T.video_source.astype(str).str.split("_").str[0] + "|" + T.target_unit.map(kind)).to_numpy()
        s2 = cat == "S2"
        v = np.where(s2, lmed(fb), np.nan)
        routed = np.zeros(len(T), bool)
        for r in R.itertuples():
            if not r.cell.startswith("S2|"):
                continue
            m = cell == r.cell
            v[m] = lmed(r.members.split("+"))[m]
            routed |= m
            info[r.cell] = int(m.sum())
        bad = s2 & ~(np.isfinite(v) & (v > 0))
        info["empty_routed"] = int(bad.sum())
        v[bad] = lmed(fb)[bad]
        info["routed"], info["fallback"] = int((routed & s2).sum()), int((s2 & ~routed).sum())
        raw = np.where(s2, v, raw)
    if l6s:
        s = l6s_values(D)
        pos = pd.Series(np.arange(len(T)), index=qids)
        s = s[pd.Series(s.index).map(pd.Series(cat, index=qids)).to_numpy() == "D2"]
        raw[pos[s.index].to_numpy()] = s.to_numpy()
        info["l6s_rows"] = int(len(s))
    return pd.Series(raw, index=qids), info


PR = pp.PRESETS["trackb"]
STATED = ("facts", "motionfam", "freefall", "labfacts")


def rules(raw):
    return pp.apply_rules(raw, D.test, rules=PR["rules"], speed_guard=PR["speed_guard"], options=PR["options"])


# L4 recomputed from test inputs (stated acceleration, question time, fps, model-free t0 of the clean 2D clips)
EVENTS = {"magnifier": (9.8, ["simulation_0203", "simulation_0204"]), "typewriter": (9.8, ["simulation_0207"]),
          "droplet": (9.7, ["simulation_0199", "simulation_0200"])}
T0 = pd.read_csv(ROOT / "research/path85b_phys/fall_t0.csv").set_index("video_id")
CH = pd.read_csv(ROOT / "research/path85b_phys/changes_ffbd.csv")
tq = T.set_index("qid")


def l4_values():
    out = {}
    for r in CH.itertuples():
        if tq.category[r.qid] != "D2":
            continue
        a, clean = EVENTS[r.event]
        t0 = float(T0.loc[clean, "t0"].median())
        fps = float(tq.fps[r.qid])
        tt = float(re.search(r"at time ([0-9.]+)\s*s", tq.question[r.qid]).group(1))
        out[r.qid] = a * (round(tt * fps) / fps - t0 - 0.5 / fps)
    s = pd.Series(out)
    assert np.allclose(s, CH.set_index("qid").new.reindex(s.index), rtol=1e-12)
    return s


CLAMP = [("person height", r"\bheight of the (?:\w+ )?(?:person|man|woman|pedestrian)\b", 1.50, 2.00),
         ("car width", r"\bwidth of the (?:\w+ )?car\b", 1.5, 2.3)]
TOM = {"m": 1.0, "meters": 1.0, "meter": 1.0, "cm": 0.01, "mm": 0.001}


def build(l2q=False, s2route=False, l6s=False, l1=False, l4=False, clamp=False):
    raw, info = raw_of(l2q, s2route, l6s)
    post, log = rules(raw)
    final = post.copy()
    stated = set(log[log.applied & log.rule.isin(STATED)].qid.astype(int))
    if l1:
        F = LN.factors("test", "qwen", post, 0.02, 0.02)
        F = F[(F.id.map(tq.category) == "S3") & ~F.id.isin(stated) & (F.factor != 1)]
        final.loc[F.id.to_numpy()] = final.loc[F.id.to_numpy()].to_numpy() * F.factor.to_numpy()
        info["l1_rows"] = len(F)
    if l4:
        s = l4_values()
        final.loc[s.index] = s.to_numpy()
        info["l4_rows"] = len(s)
    if clamp:
        hits = {}
        for q in final.index:
            ql, pl = tq.question[q].lower(), str(tq.prior[q]).lower()
            u = str(tq.target_unit[q]).lower().strip()
            if "toy" in ql or "toy" in pl or q in stated or u not in TOM:
                continue
            for nm, rx, lo, hi in CLAMP:
                if re.search(rx, ql):
                    v = final[q] * TOM[u]
                    if np.isfinite(v) and v > 0 and not lo <= v <= hi:
                        final[q] = min(max(v, lo), hi) / TOM[u]
                        hits[q] = nm
        info["clamp"] = hits
    return raw, post, final, stated, info


def diff(a, b):
    return ~np.isclose(a.to_numpy(float), b.reindex(a.index).to_numpy(float), rtol=1e-9, equal_nan=True)


if __name__ == "__main__":
    B1 = pd.read_csv(ROOT / "submissions/trackB_cand_B1.csv").set_index("id").parsed_value.reindex(qids)
    V3F = pd.read_csv(ROOT / "submissions/trackB_v3_catmedian_famrules.csv").set_index("id").parsed_value.reindex(qids)
    raw0, post0, base, stated0, _ = build()
    print("base (v3 sets + rules) vs uploaded v3: rows differing", int(diff(base, V3F).sum()))
    raw, post, fin, stated, info = build(True, True, True, True, True, True)
    print("info:", {k: (v if k != "clamp" else f"{len(v)} {pd.Series(v).value_counts().to_dict()}") for k, v in info.items()})
    d = diff(fin, B1)
    print("INDEPENDENT B1 vs submissions/trackB_cand_B1.csv: rows differing", int(d.sum()),
          "max rel diff", float(np.nanmax(np.abs(fin.to_numpy() / B1.to_numpy() - 1))))
    if A.out:
        fin.rename("parsed_value").rename_axis("id").to_csv(A.out)
    if A.audit:
        files = sorted({str(Path(p).resolve()) for p in OPENED if not p.startswith("/proc") and Path(p).is_file()})
        data = [f for f in files if not re.search(r"/(\.venv|site-packages|lib/python[0-9.]+|__pycache__)/|\.pyc?$|/usr/", f)]
        Path(A.out + ".files.txt" if A.out else "/dev/null").write_text("\n".join(data))
        print("audit: data files opened", len(data), "| subprocesses", PROCS)
