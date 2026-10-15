"""Independent re-derivation of Track B probe B2route and candidate B1clamp (verifier; does NOT import build_b1.py or
build_b2.py).

Re-implements the B2 recipe from its written definition (B2_BUILD.md) on the shared base (harness.Data member table +
qp.postprocess preset "trackb", which reproduces the uploaded v3; build_v5.l6s_values for L6s, as B1_verify did):
  raw    unrouted categories: v3 set with L2' (qwen_geo -> qwen_fov) in S3/D3.
         routed categories: every row the category fallback set, then each cell of routing_base8_min25_k2.csv its
         listed set; L2' substitution applied inside routed / fallback sets of S3/D3 unless l2q_route=False; a row
         with no finite member value -> fallback set -> the B1 (v3 + L2') set.
  l6s    D2 rows of build_v5.l6s_values override.
  rules  preset "trackb" on the test table.
  l1     S3 lab rows not set by a stated rule x labnoise factor on the post-rule values.
  l4     recomputed from fps, question time, stated acceleration and fall_t0.csv (asserted == changes_ffbd.csv new).
  clamp  b1: guard_tb regexes. wide: my own token parser for "width of the <0-4 modifier words> car" (written from
         the B2_BUILD.md spec, not from build_b2's regex).
  keep   categories not kept take a reference file's values.

    .venv/bin/python <this> [--scramble-val] [--audit] [--outdir dir]
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


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scramble-val", action="store_true")
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--outdir", default="")
    A = ap.parse_args()
else:
    A = argparse.Namespace(scramble_val=False, audit=False, outdir="")
if A.audit:
    sys.addaudithook(hook)

for p in (ROOT, ROOT / "research/trackb_dense", ROOT / "research/trackb_v5"):
    sys.path.insert(0, str(p))
import qp.data as QD  # noqa: E402

if A.scramble_val:
    _orig = QD.load_validation

    def _scr(*a, **k):
        df = _orig(*a, **k).copy()
        df["answer"] = np.random.default_rng(321).uniform(0.01, 100, len(df))
        return df
    QD.load_validation = _scr
    import tbcommon as _tbc  # noqa: E402
    _tbc.load_validation = _scr

from qp import postprocess as pp  # noqa: E402
import tbcommon as TBC  # noqa: E402
from harness import Data  # noqa: E402
import labnoise_open as LN  # noqa: E402
from build_v5 import l6s_values  # noqa: E402

D = Data()
if A.scramble_val:
    _true = _orig().answer.to_numpy(float)
    assert len(_true) == len(D.lab) and np.mean(np.isclose(D.lab.to_numpy(), _true)) < 0.01, "scramble did not take effect"
    print("scramble-val: validation labels replaced in harness.Data (", int(np.isclose(D.lab.to_numpy(), _true).sum()),
          "of", len(_true), "equal the true labels )")
T = D.test.reset_index(drop=True)
qids = T.qid.to_numpy()
cat = T.category.to_numpy()
tq = T.set_index("qid")
RUN = TBC.RUN
PLD = ROOT / "research/r86/intel_tb_pseudolabel"


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
# qwen_fov must equal qwen_geo off lab (L2' is the lab re-solve of the same track)
lab = T.video_source.astype(str).str.startswith("lab").to_numpy()
_d = ~np.isclose(M["qwen_fov"], M["qwen_geo"], rtol=1e-9, equal_nan=True)
assert not (_d & ~lab).any(), "qwen_fov differs from qwen_geo off lab"


def lmed(ms):
    L = np.log(np.vstack([M[m] for m in ms]))
    L[~np.isfinite(L)] = np.nan
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return np.exp(np.nanmedian(L, 0))


V3 = {"S2": ["caw", "cv_geo", "qwen_direct"], "D2": ["caw", "cv_geo", "qwen_direct", "qwen_geo"],
      "S3": ["cv_geo", "qwen_geo", "qwen_direct"], "D3": ["caw", "qwen_geo", "qwen_direct"]}
CATS = ("S2", "D2", "S3", "D3")


def kind(u):  # pseudo_tb.py definition
    u = str(u).lower()
    return "A" if ("s^2" in u or "s2" in u or "s²" in u) else ("V" if "/s" in u or "per s" in u else "L")


CELL = (T.category + "|" + T.video_source.astype(str).str.split("_").str[0] + "|" + T.target_unit.map(kind)).to_numpy()
RT = pd.read_csv(PLD / "routing_base8_min25_k2.csv")
FB = json.load(open(PLD / "fallback_category_sets.json"))


def sw(ms, c, on):
    return [("qwen_fov" if (on and c in ("S3", "D3") and m == "qwen_geo") else m) for m in ms]


def raw_of(route=(), l2q=True, l2q_route=True, l6s=True):
    raw = np.full(len(T), np.nan)
    prov = np.empty(len(T), dtype=object)
    for c, ms in V3.items():
        ms = sw(ms, c, l2q)
        raw[cat == c] = lmed(ms)[cat == c]
        prov[cat == c] = "b1set:" + "+".join(ms)
    b1set = raw.copy()
    info = {}
    for c in route:
        inc = cat == c
        fb = sw(FB[c], c, l2q and l2q_route)
        v = np.where(inc, lmed(fb), np.nan)
        pv = np.where(inc, "fallback:" + "+".join(fb), None).astype(object)
        routed = np.zeros(len(T), bool)
        for r in RT.itertuples():
            if not r.cell.startswith(c + "|"):
                continue
            m = CELL == r.cell
            ms = sw(r.members.split("+"), c, l2q and l2q_route)
            v[m] = lmed(ms)[m]
            pv[m] = f"cell:{r.cell}:" + "+".join(ms)
            routed |= m
            info[r.cell] = int(m.sum())
        bad = inc & ~(np.isfinite(v) & (v > 0))
        info[f"{c}_empty_routed"] = int(bad.sum())
        v[bad] = lmed(fb)[bad]
        bad2 = inc & ~(np.isfinite(v) & (v > 0))
        info[f"{c}_to_b1set"] = int(bad2.sum())
        v[bad2] = b1set[bad2]
        info[f"{c}_fallback_rows"] = int((inc & ~routed).sum())
        raw = np.where(inc, v, raw)
        prov = np.where(inc, pv, prov)
    if l6s:
        s = l6s_values(D)
        pos = pd.Series(np.arange(len(T)), index=qids)
        s = s[pd.Series(s.index).map(pd.Series(cat, index=qids)).to_numpy() == "D2"]
        ix = pos[s.index].to_numpy()
        raw[ix] = s.to_numpy()
        prov[ix] = np.array([f"l6s|{p}" for p in prov[ix]], dtype=object)
        info["l6s_rows"] = int(len(s))
    return pd.Series(raw, index=qids), pd.Series(prov, index=qids), info


PR = pp.PRESETS["trackb"]
STATED = ("facts", "motionfam", "freefall", "labfacts")


def rules(raw):
    return pp.apply_rules(raw, D.test, rules=PR["rules"], speed_guard=PR["speed_guard"], options=PR["options"])


EVENTS = {"magnifier": (9.8, ["simulation_0203", "simulation_0204"]), "typewriter": (9.8, ["simulation_0207"]),
          "droplet": (9.7, ["simulation_0199", "simulation_0200"])}
T0 = pd.read_csv(ROOT / "research/path85b_phys/fall_t0.csv").set_index("video_id")
CH = pd.read_csv(ROOT / "research/path85b_phys/changes_ffbd.csv")


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


PH = r"\bheight of the (?:\w+ )?(?:person|man|woman|pedestrian)\b"
CAR1 = r"\bwidth of the (?:\w+ )?car\b"
STOP = {"the", "a", "an", "that", "which", "where", "of"}
PARTS = {"park", "door", "window", "wheel", "tire", "tyre", "seat", "roof", "lane", "mirror", "light", "bumper", "hood",
         "trunk", "space", "spot"}
TOM = {"m": 1.0, "meters": 1.0, "meter": 1.0, "cm": 0.01, "mm": 0.001}


def car_wide(ql):
    """My reading of the spec: 'width of the' + 0-4 modifier words (no determiner / relative pronoun / 'of') + 'car'
    as the head noun (not "car's", not a car part / car park)."""
    if re.search(CAR1, ql):
        return True
    for m in re.finditer(r"\bwidth of the ", ql):
        toks = ql[m.end():].split(" ")
        for k in range(min(5, len(toks))):
            w = toks[k]
            core = w.rstrip("?.,!;:)")
            if core == "car":                       # head noun reached
                nxt = toks[k + 1].rstrip("?.,!;:)") if (k + 1 < len(toks) and core == w) else ""
                if nxt in PARTS or (nxt.endswith("s") and nxt[:-1] in PARTS):
                    break                           # car park / car door ...
                return True
            if k == 4 or core != w or core in STOP or not re.fullmatch(r"[\w'-]+", core):
                break                               # phrase ended / determiner / too many modifiers
    return False


def build(route=("S2",), clamp="b1", l2q_route=True, l6s=True, l1=True, l4=True, do_clamp=True):
    raw, prov, info = raw_of(route, True, l2q_route, l6s)
    post, log = rules(raw)
    final = post.copy()
    stated = set(log[log.applied & log.rule.isin(STATED)].qid.astype(int))
    l1f = pd.Series(dtype=float)
    if l1:
        F = LN.factors("test", "qwen", post, 0.02, 0.02)
        F = F[(F.id.map(tq.category) == "S3") & ~F.id.isin(stated) & (F.factor != 1)]
        final.loc[F.id.to_numpy()] = final.loc[F.id.to_numpy()].to_numpy() * F.factor.to_numpy()
        l1f = pd.Series(F.factor.to_numpy(), index=F.id.to_numpy())
    l4v = pd.Series(dtype=float)
    if l4:
        l4v = l4_values()
        final.loc[l4v.index] = l4v.to_numpy()
    hits = {}
    if do_clamp:
        for q in final.index:
            ql, pl = tq.question[q].lower(), str(tq.prior[q]).lower()
            u = str(tq.target_unit[q]).lower().strip()
            if "toy" in ql or "toy" in pl or q in stated or u not in TOM:
                continue
            for nm, test, lo, hi in (("person height", lambda s: re.search(PH, s) is not None, 1.50, 2.00),
                                     ("car width", (lambda s: re.search(CAR1, s) is not None) if clamp == "b1" else car_wide,
                                      1.5, 2.3)):
                if test(ql):
                    v = final[q] * TOM[u]
                    if np.isfinite(v) and v > 0 and not lo <= v <= hi:
                        final[q] = min(max(v, lo), hi) / TOM[u]
                        hits[q] = nm
    return dict(raw=raw, prov=prov, post=post, final=final, log=log, stated=stated, l1=l1f, l4=l4v, clamp=hits,
                info=info)


def keep(final, keep_cats, ref):
    r = pd.read_csv(ref).set_index("id").parsed_value
    out = final.copy()
    rev = [q for q in final.index if tq.category[q] not in keep_cats]
    out.loc[rev] = r.reindex(rev).to_numpy()
    return out


def diff(a, b):
    return pd.Series(~np.isclose(a.to_numpy(float), b.reindex(a.index).to_numpy(float), rtol=1e-9, equal_nan=True),
                     index=a.index)


def sub(path):
    return pd.read_csv(path).set_index("id").parsed_value.reindex(qids)


if __name__ == "__main__":
    SUB = ROOT / "submissions"
    B1 = sub(SUB / "trackB_cand_B1.csv")
    B2 = sub(SUB / "trackB_probe_B2route.csv")
    B1C = sub(SUB / "trackB_cand_B1clamp.csv")
    V3F = sub(SUB / "trackB_v3_catmedian_famrules.csv")
    # base: v3 sets, no components
    r0, _, i0 = raw_of((), l2q=False, l6s=False)
    p0, _ = rules(r0)
    print("base (v3 sets + rules) vs uploaded v3: rows differing", int(diff(p0, V3F).sum()))
    out = {}
    for name, kw, ref in (("B1", dict(route=("S2",), clamp="b1"), B1),
                          ("B2route", dict(route=("S2", "D2", "S3", "D3"), clamp="b1"), B2),
                          ("B1clamp", dict(route=("S2",), clamp="wide"), B1C)):
        R = build(**kw)
        d = diff(R["final"], ref)
        mx = float(np.nanmax(np.abs(R["final"].to_numpy() / ref.to_numpy() - 1)))
        print(f"INDEPENDENT {name} vs submitted file: rows differing {int(d.sum())} / {len(d)}, max rel diff {mx:.2e}")
        print(f"   info {R['info']}")
        print(f"   l6s {R['info'].get('l6s_rows')} l1 {len(R['l1'])} l4 {len(R['l4'])} clamp {len(R['clamp'])} "
              f"{pd.Series(R['clamp'], dtype=object).value_counts().to_dict()} stated {len(R['stated'])}")
        out[name] = R
        if A.outdir:
            R["final"].rename("parsed_value").rename_axis("id").to_csv(Path(A.outdir) / f"indep_{name}.csv")
    if A.audit:
        files = sorted({str(Path(p).resolve()) for p in OPENED if not p.startswith("/proc") and Path(p).is_file()})
        data = [f for f in files if not re.search(r"/(\.venv|site-packages|lib/python[0-9.]+|__pycache__)/|\.pyc?$|/usr/", f)]
        if A.outdir:
            (Path(A.outdir) / "indep_files_opened.txt").write_text("\n".join(data))
        bydir = pd.Series([str(Path(f).parent) for f in data]).value_counts().sort_index()
        print("audit: data files opened", len(data), "| subprocesses", PROCS)
        print(bydir.to_string())
        closed = re.compile(r"trackA|combo|claude|opus|sonnet|gpt|openai|gemini|gem31|argon|_sol|sol_|muse|fable|astra|"
                            r"runs/test_|runs/val_", re.I)
        print("closed-model / Track A files among them:", [f for f in data if closed.search(f.replace(str(ROOT), "").replace("/tmp/claude-0/", "/tmp/"))] or "none")
