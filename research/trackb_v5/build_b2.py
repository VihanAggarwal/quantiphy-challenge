"""Track B probe B2route (pseudo-label routing extended to D2/S3/D3 on top of B1) and candidate B1clamp (B1 with the
car-width clamp widened to any "width of the ... car" phrase).

    .venv/bin/python research/trackb_v5/build_b2.py --out submissions/trackB_probe_B2route.csv \
        [--route S2,D2,S3,D3] [--clamp b1|wide] [--no-l2q-route] [--keep S2,D2,S3,D3] \
        [--rows research/trackb_v5/B2_rows.csv] [--decompose] [--val]
    .venv/bin/python research/trackb_v5/build_b2.py --out submissions/trackB_cand_B1clamp.csv --route S2 --clamp wide

`--route S2 --clamp b1` rebuilds submissions/trackB_cand_B1.csv exactly (asserted with --decompose). This file does not
modify or re-define any B1 component: it imports them from build_b1.py and only generalises the S2 routing to a list
of categories and the clamp regex.

Track B inputs only (as B1): open-weight member outputs, model-free code and the test inputs. The routing table and
the category fallback sets hold member NAMES only; they were selected at development time by agreement with Track A
pseudo-labels (research/r86/intel_tb_pseudolabel/dump.py; FAQ section 09, disclosed). No Track A value is read.

Pipeline (B1 order; the only change is that the per-category member set of every routed category comes from the
routing table):
  raw    routed categories: per-cell log-median set from routing_base8_min25_k2.csv (cell = category|source|unit
         kind; min 25 fit rows, 1-2 members), other rows of the category the category fallback set
         (fallback_category_sets.json); a routed row with no finite member value -> the fallback set -> the B1 set.
         Unrouted categories: the B1 set (v3 set, with L2' in S3/D3).
         L2' (l2q) is a member substitution (qwen_geo -> qwen_fov in S3/D3: the same Qwen track re-solved with the
         fixed lab camera; it differs from qwen_geo on lab rows only). It is applied inside whatever S3/D3 set is in
         force, routed sets included (--no-l2q-route: routed sets verbatim).
  l6s    D2 rows with a valid snapped twin-mask cvq geometry -> that value (overrides the routed median, as it
         overrode the v3 median in B1).
  rules  qp.postprocess preset "trackb" on the whole test table (pool rule spill-over logged).
  l1     S3 lab motion rows not set by a stated-fact rule x the lab label-noise emulator factor, computed on the
         post-rule answers of this build.
  l4     D2 free-fall speed rows -> a*(t_k - t0 - 1/(2 fps)).
  clamp  car width -> [1.5, 2.3] m, person height -> [1.50, 2.00] m; "toy" and stated rows skipped.
         b1: the B1 regexes. wide: the car-width regex also accepts up to 4 modifier words between "the" and "car"
         (no determiner / relative pronoun / "of" among them, not "car's", not "car park/door/..."), a superset of B1.
  keep   categories not in --keep take the values of --keep-ref (default: the B1 file) row by row.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "research" / "trackb_dense"))
import build_b1 as B  # noqa: E402
from build_b1 import CATS, LN, PLD, STATED, TO_M, V3, VAL_OFFSET, V3_FILE, Data, cells, changed, fmt, lmed  # noqa: E402
from tbcommon import RUN, read_csv  # noqa: E402

B1_FILE = ROOT / "submissions/trackB_cand_B1.csv"
COMPS = ("l2q", "route", "l6s", "l1", "l4", "clamp")
PH_RX = B.CLAMP[0][1]
CAR_B1 = B.CLAMP[1][1]
CAR_NEW = (r"\bwidth of the (?:(?!(?:the|a|an|that|which|where|of)\b)[\w'-]+ ){0,4}car\b(?!['’]s\b)"
           r"(?! (?:park|door|window|wheel|tire|tyre|seat|roof|lane|mirror|light|bumper|hood|trunk|space|spot)s?\b)")
CLAMPS = {"b1": [("person height", PH_RX, 1.50, 2.00), ("car width", CAR_B1, 1.5, 2.3)],
          "wide": [("person height", PH_RX, 1.50, 2.00), ("car width", f"(?:{CAR_B1})|(?:{CAR_NEW})", 1.5, 2.3)]}


def routing(cats):
    R = pd.read_csv(PLD / "routing_base8_min25_k2.csv")
    cs = {r.cell: r.members.split("+") for r in R.itertuples() if r.cell.split("|")[0] in cats}
    fb = json.load(open(PLD / "fallback_category_sets.json"))
    return cs, {c: fb[c] for c in cats}


def swap(ms, cat, on):
    return [("qwen_fov" if m == "qwen_geo" and cat in ("S3", "D3") and on else m) for m in ms]


def raw_split(D, split, comps, route_cats, l2q_route, info):
    """Raw (pre-rule) answers and a per-row provenance label."""
    frame = D.test if split == "test" else D.val
    l2q = "l2q" in comps
    sets = {c: swap(v, c, l2q) for c, v in V3.items()}
    raw = D.raw(sets, split)
    b1set = raw.to_numpy().copy()
    prov = np.array([f"set:{c}:{'+'.join(sets[c])}" for c in frame.category], dtype=object)
    if "route" in comps and route_cats:
        cs, fb = routing(route_cats)
        cell = cells(frame).to_numpy()
        val = raw.to_numpy().copy()
        stats = {}
        for c in route_cats:
            inc = (frame.category == c).to_numpy()
            ms = swap(fb[c], c, l2q and l2q_route)
            val[inc] = lmed(D, split, ms, inc)
            prov[inc] = f"fallback:{c}:{'+'.join(ms)}"
            nroute = {}
            for k, ms in cs.items():
                if k.split("|")[0] != c:
                    continue
                m = cell == k
                ms = swap(ms, c, l2q and l2q_route)
                val[m] = lmed(D, split, ms, m)
                prov[m] = f"cell:{k}:{'+'.join(ms)}"
                nroute[k] = int(m.sum())
            bad = inc & ~(np.isfinite(val) & (val > 0))
            nfb = int(bad.sum())
            msf = swap(fb[c], c, l2q and l2q_route)
            val[bad] = lmed(D, split, msf, bad)
            prov[bad] = f"fallback(nan):{c}:{'+'.join(msf)}"
            bad2 = inc & ~(np.isfinite(val) & (val > 0))
            val[bad2] = b1set[bad2]
            prov[bad2] = np.array([f"b1set(nan):{p}" for p in prov[bad2]], dtype=object)
            stats[c] = dict(routed_rows=nroute, fallback_rows=int(inc.sum() - sum(nroute.values())),
                            nan_to_fallback=nfb, nan_to_b1set=int(bad2.sum()))
        raw = pd.Series(val, index=raw.index)
        info[f"route_{split}"] = stats
    if "l6s" in comps:
        v = B.l6s_split(D, split)
        cat = frame.set_index("qid").category
        v = v[v.index.map(cat) == "D2"]
        raw.loc[v.index] = v.to_numpy()
        pos = pd.Series(np.arange(len(frame)), index=frame.qid.to_numpy())
        for q in v.index:
            prov[pos[q]] = f"l6s(over {prov[pos[q]]})"
        info[f"l6s_{split}"] = int(len(v))
    return raw, pd.Series(prov, index=raw.index)


def clamp(frame, pred, protected, mode):
    f = frame.set_index("qid")
    q, u, p = f.question.str.lower(), f.target_unit.astype(str).str.lower().str.strip(), f.prior.astype(str).str.lower()
    out, hit = pred.copy(), {}
    notoy = ~q.str.contains("toy") & ~p.str.contains("toy")
    for nm, rx, lo, hi in CLAMPS[mode]:
        msk = q.str.contains(rx, regex=True) & u.isin(list(TO_M)) & notoy & ~f.index.isin(list(protected))
        for i in f.index[msk]:
            if i not in out.index:
                continue
            k = TO_M[u[i]]
            v = float(out[i]) * k
            if np.isfinite(v) and v > 0 and not (lo <= v <= hi):
                out[i] = float(np.clip(v, lo, hi)) / k
                hit[i] = nm
    return out, hit


def build(D, comps, route_cats, table="test", clamp_mode="b1", l2q_route=True):
    """Final answers + stage values. table='combined': validation rows in the test table (scoring only)."""
    comps, info = set(comps), {}
    rt, pt = raw_split(D, "test", comps, route_cats, l2q_route, info)
    if table == "test":
        raw, prov, df = rt, pt, D.test
    else:
        rv, pv = raw_split(D, "val", comps, route_cats, l2q_route, info)
        keep = D.test.qid[~D.dup]
        vix = D.val.qid.to_numpy() + VAL_OFFSET
        raw = pd.concat([rt.reindex(keep), pd.Series(rv.to_numpy(), index=vix)])
        prov = pd.concat([pt.reindex(keep), pd.Series(pv.to_numpy(), index=vix)])
        df = D.df
    post, log = D.rules(raw, df=df)
    final = post.copy()
    stated = set(log[log.applied & log.rule.isin(STATED)].qid.astype(int))
    st = dict(l1=pd.Series(dtype=float), l4=pd.Series(dtype=float), clamp={})
    if "l1" in comps:
        cat = df.set_index("qid").category
        frames = []
        for split, off in (("test", 0), ("val", VAL_OFFSET)) if table == "combined" else (("test", 0),):
            A = pd.Series({q - off: v for q, v in post.items() if (q >= VAL_OFFSET) == (off > 0)})
            F = LN.factors(split, "qwen", A, 0.02, 0.02)
            F["qid"] = F.id + off
            frames.append(F)
        F = pd.concat(frames)
        F = F[F.qid.isin(cat.index) & (F.qid.map(cat) == "S3") & ~F.qid.isin(stated) & (F.factor != 1)]
        final.loc[F.qid] = final.loc[F.qid].to_numpy() * F.factor.to_numpy()
        st["l1"] = pd.Series(F.factor.to_numpy(), index=F.qid.to_numpy())
        info["l1"] = int((F.qid < VAL_OFFSET).sum())
    if "l4" in comps:
        C = pd.read_csv(ROOT / "research/path85b_phys/changes_ffbd.csv")
        cat = D.test.set_index("qid").category
        C = C[(C.qid.map(cat) == "D2") & C.qid.isin(final.index)]
        final.loc[C.qid] = C.new.to_numpy()
        st["l4"] = pd.Series(C.new.to_numpy(), index=C.qid.to_numpy())
        info["l4"] = int(len(C))
    if "clamp" in comps:
        final, hit = clamp(df, final, stated, clamp_mode)
        st["clamp"] = hit
        info["clamp"] = hit
    return dict(raw=raw, prov=prov, post=post, final=final, log=log, info=info, stated=stated, **st)


def keep_cats(D, final, keep, ref=B1_FILE):
    r = pd.read_csv(ref).set_index("id").parsed_value
    cat = D.test.set_index("qid").category
    rev = final.index[~final.index.map(cat).isin(keep)]
    out = final.copy()
    out.loc[rev] = r.reindex(rev).to_numpy()
    return out


def winner(q, R, ref_raw):
    """Which component set row q's final value in build R (last step that changed it)."""
    lg = R["log"]
    applied = lg[(lg.qid == q) & lg.applied]
    if q in R["clamp"]:
        return "clamp:" + R["clamp"][q]
    if q in R["l4"].index:
        return "l4"
    if q in R["stated"]:
        return "stated:" + "+".join(applied.rule[applied.rule.isin(STATED)].unique())
    w = R["prov"][q]
    if len(applied):
        w = "rule:" + "+".join(applied.rule.unique()) + f" (raw {w})"
    if q in R["l1"].index:
        w = f"l1 x{R['l1'][q]:.3f} on " + w
    return w


def setup():
    D = Data()
    D.add_method("cv_geo_only", read_csv(RUN / "test/cv/cv_geometry.csv", D.test.qid),
                 read_csv(RUN / "val/cv/cv_geometry.csv", D.val.qid))
    return D


def write_sub(D, final, out):
    assert final.notna().all() and np.isfinite(final).all() and (final > 0).all()
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": D.test.qid, "parsed_value": final.reindex(D.test.qid).to_numpy()}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, out], check=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--route", default="S2,D2,S3,D3")
    ap.add_argument("--clamp", default="b1", choices=sorted(CLAMPS))
    ap.add_argument("--no-l2q-route", action="store_true")
    ap.add_argument("--keep", default=",".join(CATS))
    ap.add_argument("--keep-ref", default=str(B1_FILE), help="file whose values the categories not in --keep take")
    ap.add_argument("--comps", default=",".join(COMPS))
    ap.add_argument("--rows", default="")
    ap.add_argument("--decompose", action="store_true")
    ap.add_argument("--val", action="store_true")
    a = ap.parse_args(argv)
    route = [c for c in a.route.split(",") if c]
    keep = [c for c in a.keep.split(",") if c]
    comps = [c for c in a.comps.split(",") if c]
    assert set(comps) <= set(COMPS) and set(route) <= set(CATS), (comps, route)
    l2r = not a.no_l2q_route
    D = setup()
    R = build(D, comps, route, clamp_mode=a.clamp, l2q_route=l2r)
    for k, v in R["info"].items():
        print(k, v if k != "clamp" else f"{len(v)} rows {pd.Series(v, dtype=object).value_counts().to_dict()}")
    final = keep_cats(D, R["final"], keep, a.keep_ref)
    write_sub(D, final, a.out)
    print("wrote", a.out)

    t = D.test.set_index("qid")
    scored = pd.Series(~D.dup, index=D.test.qid)
    b1 = pd.read_csv(B1_FILE).set_index("id").parsed_value.reindex(t.index)
    v3 = pd.read_csv(V3_FILE).set_index("id").parsed_value.reindex(t.index)
    out = pd.read_csv(a.out).set_index("id").parsed_value.reindex(t.index)

    def per_cat(mask):
        m = mask.reindex(t.index).fillna(False).astype(bool)
        return {c: f"{int((m & (t.category == c)).sum())}/{int((m & scored & (t.category == c)).sum())}" for c in CATS}

    print("vs B1, rows changed per category (all/scored):", per_cat(changed(out, b1)))
    print("vs v3, rows changed per category (all/scored):", per_cat(changed(out, v3)))
    if not a.decompose:
        return
    # reproduction: route S2 + B1 clamp == the B1 file
    R1 = build(D, list(COMPS), ["S2"])
    assert not changed(R1["final"].reindex(t.index), b1).any(), "route S2 + clamp b1 must reproduce B1"
    print("rebuild of B1 (route S2, clamp b1) == submissions/trackB_cand_B1.csv: OK")
    raw_b1 = R1["raw"].reindex(t.index)
    rows = pd.DataFrame({"video_id": t.video_id, "category": t.category, "scored": scored.reindex(t.index),
                         "cell": cells(D.test).set_axis(D.test.qid).reindex(t.index), "b1": b1, "new": out})
    rows["changed"] = changed(out, b1)
    rows["raw_changed"] = changed(R["raw"].reindex(t.index), raw_b1)
    rows["spill"] = rows.changed & ~rows.raw_changed
    rows["b1_raw_source"] = R1["prov"].reindex(t.index)
    rows["new_raw_source"] = R["prov"].reindex(t.index)
    rows["b1_winner"] = [winner(q, R1, raw_b1) for q in t.index]
    rows["new_winner"] = [winner(q, R, raw_b1) for q in t.index]
    new_route = [c for c in route if c != "S2"]
    att = {q: [] for q in t.index}
    if new_route:
        print("\nper routed category | B1 + this category alone vs B1 (all/scored) | its spill-over (raw unchanged, final "
              "changed) outside / inside the category | leave-one-out share of the build (all/scored)")
        for c in new_route:
            Ra = build(D, comps, ["S2", c], clamp_mode=a.clamp, l2q_route=l2r)
            fa = Ra["final"].reindex(t.index)
            ch1 = changed(fa, b1)
            sp = ch1 & ~changed(Ra["raw"].reindex(t.index), raw_b1)
            Rl = build(D, comps, [x for x in route if x != c], clamp_mode=a.clamp, l2q_route=l2r)
            fl = keep_cats(D, Rl["final"], keep, a.keep_ref).reindex(t.index)
            loo = changed(out, fl)
            for q in loo.index[loo]:
                att[q].append(f"route_{c}")
            rows[f"spill_from_{c}"] = sp & (t.category != c)
            print(f"route_{c} | {per_cat(ch1)} | out {per_cat(sp & (t.category != c))} in {per_cat(sp & (t.category == c))}"
                  f" | {per_cat(loo)}")
    if a.clamp != "b1":
        Rb = build(D, comps, route, clamp_mode="b1", l2q_route=l2r)
        loo = changed(out, keep_cats(D, Rb["final"], keep, a.keep_ref).reindex(t.index))
        for q in loo.index[loo]:
            att[q].append("clamp_wide")
        print(f"clamp wide vs b1 | {per_cat(loo)}")
    rows["attribution"] = pd.Series({q: "+".join(v) for q, v in att.items()})
    print("\nchanged rows vs B1: winning component of the new value (top), by category:")
    ch = rows[rows.changed]
    w = ch.new_winner.str.replace(r"x[0-9.]+ ", "", regex=True).str.replace(r":[A-Za-z0-9_+]+\)", ")", regex=True)
    w = w.str.replace(r"(cell:[A-Z0-9]+\|[a-z]+\|[ALV]):[a-z0-9_+]+", r"\1", regex=True)
    w = w.str.replace(r"(fallback(?:\(nan\))?:[A-Z0-9]+):[a-z0-9_+]+", r"\1", regex=True)
    print(pd.crosstab(w, ch.category).to_string())
    if a.rows:
        rows[rows.changed | rows.filter(like="spill").any(axis=1)].to_csv(a.rows)
        print("wrote", a.rows)
    if a.val:
        print("\nvalidation (combined table; labels read only here, for scoring):")
        base = build(D, comps, ["S2"], "combined")["final"]
        print("  B1      ", fmt(D.score(base)))
        variants = [(f"+route_{c}", ["S2", c], a.clamp, l2r, comps) for c in new_route]
        variants += [("BUILD", route, a.clamp, l2r, comps)]
        if new_route and "l2q" in comps:
            variants += [("BUILD, routed sets verbatim (no L2' in routed sets)", route, a.clamp, False, comps)]
        if new_route and "l6s" in comps:
            variants += [("BUILD, routing wins over L6s (no l6s)", route, a.clamp, l2r, [x for x in comps if x != "l6s"])]
        for nm, rc, cm, l2, cp in variants:
            fc = build(D, cp, rc, "combined", clamp_mode=cm, l2q_route=l2)["final"]
            print(f"  {nm:8s}", fmt(D.score(fc)), "| boot vs B1", fmt(D.boot(base, fc)))


if __name__ == "__main__":
    main()
