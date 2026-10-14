"""Track B failure diagnosis on validation (159 q, 24 clips): which failure dominates?

    .venv/bin/python research/trackb_next/diagnose.py [--boot 2000]

Inputs: the open-weight Colab run trackb_v1 (/tmp/claude-0/tb3/x/trackb_v1/val: Qwen3-VL-32B specs / grounding
tracks / direct answers, Code-as-World (CaW) direct, SAM 2 tracks cv / cvq, Qwen3.5-27B and Gemma-4-31B direct).
Validation labels are read only to score.

DIAGNOSTIC-ONLY reference (never enters any Track B answer): the cached Track A Claude annotation of the same
validation questions (runs/val_hr_v1_high, specs + pixel tracks). It is used as a yardstick in a 2 x 2 swap through the
SAME solver (qp.geometry.solve): {Qwen spec, Claude spec} x {Qwen tracks, Claude tracks}. The swap tells how much of
the Track B geometry loss is the question spec and how much the pixel tracks, i.e. which open component the next GPU
run must replace. Track objects are renamed to the spec's object names per role so the solver's name matching does
not decide the result.

Sections printed:
 1. members per category (MRA, gross-miss rate > 2x, coverage) and per question kind;
 2. the 2 x 2 spec/track swap (geometry alone, missing = 0, and with the CaW fallback as in production);
 3. per-row attribution of the Qwen-geometry loss (spec-limited / track-limited / both / neither);
 4. grounding error classes for Qwen vs Claude tracks (wrong object, extent off, motion off) per role.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import warnings
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "research" / "trackb_dense"))
warnings.filterwarnings("ignore")

from qp.claude_annotate import load_annotations, with_depth_info  # noqa: E402
from qp.geometry import solve  # noqa: E402
from qp.mra import item_scores  # noqa: E402
from qp.spec import Obs, QuestionSpec, RoleTrack  # noqa: E402
from tbcommon import RUN, base_preds, load_dir, questions  # noqa: E402

CATS = ("S2", "D2", "S3", "D3")
CLAUDE_RUN = ROOT / "runs" / "val_hr_v1_high" / "val_hires"


def src_of(v: str) -> str:
    return "seg" if v.endswith("_segmented") else ("lab" if v.startswith("captured") else v.split("_")[0])


def items(pred, gt) -> np.ndarray:
    s = item_scores(np.asarray(pred, float), np.asarray(gt, float))
    return np.nan_to_num(np.asarray(s, float), nan=0.0)


def macro(it: np.ndarray, cat: np.ndarray) -> dict:
    per = {c: float(it[cat == c].mean()) for c in CATS}
    return dict(MRA=float(np.mean(list(per.values()))), **per)


def fmt(d: dict) -> str:
    return " ".join(f"{k} {v:.3f}" for k, v in d.items())


def gross(pred, gt) -> float:
    p, g = np.asarray(pred, float), np.asarray(gt, float)
    r = np.abs(np.log(p / g))
    return float(np.mean(np.where(np.isfinite(r), r > math.log(2), True)))


# ----------------------------------------------------------------------------- swap

def renamed(tracks: list[RoleTrack], spec: QuestionSpec) -> list[RoleTrack]:
    """Tracks whose object names are the spec's names for their role (role matching, not name matching)."""
    out = []
    for t in tracks:
        q = spec.prior if t.role.startswith("prior") else spec.target
        i = 1 if t.role.endswith("2") else 0
        name = q.objects[i] if len(q.objects) > i and str(q.objects[i]).strip() else t.object
        out.append(RoleTrack(role=t.role, object=str(name), obs=t.obs, source=t.source,
                             depth_name=t.depth_name, range_m=t.range_m))
    return out


def scaled(tracks: list[RoleTrack], sx: float, sy: float, strip: str = "") -> list[RoleTrack]:
    """Tracks mapped to another image size; strip="extent" drops extents/points (boxes only)."""
    out = []
    for t in tracks:
        obs = []
        for o in t.obs:
            box = [o.box[0] * sx, o.box[1] * sy, o.box[2] * sx, o.box[3] * sy] if o.box else None
            pt = [o.point[0] * sx, o.point[1] * sy] if o.point else None
            ext = [[e[0] * sx, e[1] * sy] for e in o.extent] if o.extent else None
            if strip == "extent":
                ext = None
                pt = pt if box is None else None
            if box or pt or ext:
                obs.append(Obs(t=o.t, point=pt, extent=ext, box=box, score=o.score))
        out.append(RoleTrack(role=t.role, object=t.object, obs=obs, source=t.source, depth_name=t.depth_name,
                             range_m=t.range_m))
    return out


def geo(spec, tracks, size, fps):
    if spec is None or not tracks:
        return math.nan, ["missing"]
    a = solve(spec, tracks, tuple(size), float(fps))
    return (a.value if a.value is not None else math.nan), a.flags


# ----------------------------------------------------------------------------- grounding classes

def _centre(o) -> np.ndarray | None:
    if o.box:
        return np.array([(o.box[0] + o.box[2]) / 2, (o.box[1] + o.box[3]) / 2], float)
    if o.point:
        return np.array(o.point, float)
    if o.extent:
        return np.mean(np.array(o.extent, float), 0)
    return None


def _size(o) -> float | None:
    if o.box:
        return float(math.hypot(o.box[2] - o.box[0], o.box[3] - o.box[1]))
    return None


def _ext(o) -> float | None:
    if o.extent:
        (x1, y1), (x2, y2) = o.extent
        return float(math.hypot(x2 - x1, y2 - y1))
    return None


def compare_tracks(tq: RoleTrack, sq, tc: RoleTrack, sc, fps: float) -> dict:
    """Qwen track tq (image size sq) vs Claude track tc (image size sc), normalised by image width."""
    def norm(track, size):
        W = float(size[0])
        return [(o.t, _centre(o), _size(o), _ext(o)) for o in track.obs], W
    Q, Wq = norm(tq, sq)
    C, Wc = norm(tc, sc)
    tol = 1.5 / fps
    d_rel, ratios, sizes = [], [], []
    cq = [(t, c / Wq) for t, c, _, _ in Q if c is not None]
    cc = [(t, c / Wc, (s / Wc) if s else None, (e / Wc) if e else None) for t, c, s, e in C if c is not None]
    for t, c, s, e in cc:
        near = [x for x in cq if abs(x[0] - t) <= tol]
        if not near:
            continue
        qc = min(near, key=lambda x: abs(x[0] - t))[1]
        qobs = min((o for o in Q if o[1] is not None), key=lambda o: abs(o[0] - t))
        scale = s or e or ((qobs[2] / Wq) if qobs[2] else None)
        if scale:
            d_rel.append(float(np.linalg.norm(qc - c)) / scale)
            sizes.append(scale)
    # extent comparison: median Qwen extent (or box side) vs median Claude extent
    qe = [e / Wq for _, _, _, e in Q if e]
    ce = [e / Wc for _, _, _, e in C if e]
    ext_ratio = float(np.median(qe) / np.median(ce)) if qe and ce else math.nan
    # motion: displacement over the common time span
    def path(track_pts):
        track_pts = sorted(track_pts, key=lambda x: x[0])
        return track_pts
    pc = path(cc)
    pq = path(cq)
    mot_ratio = math.nan
    if len(pc) >= 2 and len(pq) >= 2:
        t0, t1 = max(pc[0][0], pq[0][0]), min(pc[-1][0], pq[-1][0])
        if t1 - t0 > 0.2:
            def disp(pts):
                a = min(pts, key=lambda x: abs(x[0] - t0))[1]
                b = min(pts, key=lambda x: abs(x[0] - t1))[1]
                return float(np.linalg.norm(b - a))
            dc, dq = disp(cc), disp(cq)
            if dc > 0.02:   # the object moved > 2% of the width in Claude's track
                mot_ratio = dq / dc
    return {"centre_rel": float(np.median(d_rel)) if d_rel else math.nan, "n": len(d_rel),
            "ext_ratio": ext_ratio, "mot_ratio": mot_ratio}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "diag_rows.csv"))
    a = ap.parse_args(argv)
    val = questions("val")
    val["src"] = val.video_id.map(src_of)
    gt, cat = val.answer.to_numpy(float), val.category.to_numpy()
    P = base_preds("val", val.qid)
    P = {m: p.reindex(val.qid).to_numpy(float) for m, p in P.items()}
    for name, sub in (("qwen_geo_raw", "qwen"), ("cv_geo_raw", "cv"), ("cvq_geo_raw", "cvq")):
        d = pd.read_csv(RUN / "val" / sub / "geometry.csv").set_index("id")
        P[name] = d.geo_value.reindex(val.qid).to_numpy(float)

    # Track A reference (diagnostic only)
    ca = pd.read_csv(ROOT / "runs" / "val_hr_v1_high" / "val_hires.csv").set_index("id")
    ref_geo = ca.geo_value.reindex(val.qid).to_numpy(float)
    ref_dir = ca.direct_value.reindex(val.qid).to_numpy(float)
    ref_final = ca.parsed_value.reindex(val.qid).to_numpy(float)

    print("== 1. members on validation (item MRA per category; gross = share > 2x off or missing)")
    rows = []
    for m in ["qwen_direct", "caw", "qwen35", "gemma4", "qwen_geo", "cv_geo", "cvq_geo",
              "qwen_geo_raw", "cv_geo_raw", "cvq_geo_raw"]:
        it = items(P[m], gt)
        d = macro(it, cat)
        cov = float(np.isfinite(P[m]).mean())
        g = {c: gross(P[m][cat == c], gt[cat == c]) for c in CATS}
        rows.append(dict(method=m, **d, cov=cov, **{f"gross_{c}": g[c] for c in CATS}))
    for m, arr in (("[ref] claude_geo_raw", ref_geo), ("[ref] claude_direct", ref_dir), ("[ref] trackA_val", ref_final)):
        it = items(arr, gt)
        d = macro(it, cat)
        g = {c: gross(arr[cat == c], gt[cat == c]) for c in CATS}
        rows.append(dict(method=m, **d, cov=float(np.isfinite(arr).mean()), **{f"gross_{c}": g[c] for c in CATS}))
    T = pd.DataFrame(rows).set_index("method")
    print(T.round(3).to_string())

    print("\n== 1b. per question kind (tk) x member, item mean (n)")
    kinds = val.tk.to_numpy()
    tab = {}
    for m in ["caw", "qwen_direct", "qwen35", "gemma4", "qwen_geo_raw", "cvq_geo_raw"]:
        it = items(P[m], gt)
        tab[m] = {f"{c}/{k}": it[(cat == c) & (kinds == k)].mean() for c in CATS for k in ("size", "distance", "speed", "accel")
                  if ((cat == c) & (kinds == k)).any()}
    it = items(ref_geo, gt)
    tab["[ref] claude_geo_raw"] = {f"{c}/{k}": it[(cat == c) & (kinds == k)].mean() for c in CATS
                                   for k in ("size", "distance", "speed", "accel") if ((cat == c) & (kinds == k)).any()}
    K = pd.DataFrame(tab)
    K["n"] = [int(((cat == ck.split('/')[0]) & (kinds == ck.split('/')[1])).sum()) for ck in K.index]
    print(K.round(3).to_string())

    # ---------------------------------------------------------------- 2. the swap
    qspecs = {int(q): QuestionSpec.from_dict(v["spec"]) for rec in load_dir(RUN / "val" / "qwen" / "specs").values()
              for q, v in rec.get("questions", {}).items()}
    qrecs = load_dir(RUN / "val" / "qwen" / "annotate")
    crecs_raw = {p.stem: json.loads(p.read_text()) for p in sorted((CLAUDE_RUN / "records").glob("*.json"))}
    depth_texts = dict(zip(val.qid.astype(int), val.depth_info.fillna("")))
    crecs = {k: with_depth_info(r, depth_texts) for k, r in crecs_raw.items()}
    cann = load_annotations(crecs)
    cmeta = {r["video_id"]: r["meta"] for r in crecs.values()}
    out = []
    for i, r in enumerate(val.itertuples()):
        q = int(r.qid)
        qrec = qrecs.get(r.video_id)
        qs = qspecs.get(q)
        qt = [RoleTrack.from_dict(t) for t in (qrec or {}).get("tracks", {}).get(str(q), [])]
        qsize, fps = (qrec["meta"]["image_size"], qrec["meta"]["fps"]) if qrec else ((854, 480), r.fps)
        ann = cann.get(q)
        cs = ann.spec if ann else None
        ct = ann.tracks if ann else []
        csize = cmeta[r.video_id]["image_size"] if r.video_id in cmeta else qsize
        QQ, fqq = geo(qs, qt, qsize, fps)
        QC, fqc = geo(qs, renamed(ct, qs) if qs else [], csize, fps)
        CQ, fcq = geo(cs, renamed(qt, cs) if cs else [], qsize, fps)
        CC, fcc = geo(cs, ct, csize, fps)
        # role mixes on the Qwen spec, in Qwen pixel coordinates (Claude tracks rescaled)
        mix = {}
        if qs is not None and ct:
            sx, sy = qsize[0] / csize[0], qsize[1] / csize[1]
            cq = scaled(renamed(ct, qs), sx, sy)
            pri = lambda ts: [t for t in ts if t.role.startswith("prior")]  # noqa: E731
            tar = lambda ts: [t for t in ts if t.role.startswith("target")]  # noqa: E731
            mix["PcTq"] = geo(qs, pri(cq) + tar(qt), qsize, fps)[0]     # Claude prior track, Qwen target track
            mix["PqTc"] = geo(qs, pri(qt) + tar(cq), qsize, fps)[0]     # Qwen prior track, Claude target track
            mix["Cbox"] = geo(qs, scaled(cq, 1, 1, "extent"), qsize, fps)[0]   # Claude tracks, boxes only
            mix["Qbox"] = geo(qs, scaled(qt, 1, 1, "extent"), qsize, fps)[0]   # Qwen tracks, boxes only
        row = dict(qid=q, video_id=r.video_id, category=r.category, src=r.src, tk=r.tk, pk=r.pk, y=r.answer,
                   QQ=QQ, QC=QC, CQ=CQ, CC=CC, caw=P["caw"][i], qwen_geo_csv=P["qwen_geo_raw"][i],
                   flags_QQ=";".join(fqq), flags_QC=";".join(fqc), **mix)
        # spec agreement
        if qs is not None and cs is not None:
            row.update(spec_tkind=qs.target.kind == cs.target.kind, spec_pkind=qs.prior.kind == cs.prior.kind,
                       spec_pval=bool(qs.prior.value_si and cs.prior.value_si
                                      and abs(qs.prior.value_si / cs.prior.value_si - 1) < 0.01),
                       spec_ttime=(qs.target.time is None) == (cs.target.time is None) and (
                           qs.target.time is None or abs(qs.target.time - cs.target.time) <= 0.1),
                       spec_unit=str(qs.target.unit) == str(cs.target.unit))
        # grounding classes per role
        cby = {t.role: t for t in ct if t.obs}
        for t in qt:
            if t.role in ("prior", "target") and t.role in cby and t.obs:
                c = compare_tracks(t, qsize, cby[t.role], csize, float(fps))
                row.update({f"{t.role}_{k}": v for k, v in c.items()})
        out.append(row)
    D = pd.DataFrame(out)
    D.to_csv(a.out, index=False)
    print(f"\nrecomputed QQ vs Colab qwen geo_value: equal on "
          f"{int(np.isclose(D.QQ, D.qwen_geo_csv, rtol=1e-6, equal_nan=True).sum())}/{len(D)} rows")

    print("\n== 2. spec x track swap through qp.geometry.solve (geometry only, missing = 0)")
    g = D.y.to_numpy(float)
    c = D.category.to_numpy()
    res = {}
    for k in ("QQ", "QC", "CQ", "CC"):
        it = items(D[k], g)
        res[k] = dict(**macro(it, c), cov=float(np.isfinite(D[k]).mean()))
        fb = np.where(np.isfinite(D[k]), D[k], D.caw)
        res[k + "+cawfb"] = dict(**macro(items(fb, g), c), cov=float(np.isfinite(fb).mean()))
    print(pd.DataFrame(res).T.round(3).to_string())
    print("  QQ = Qwen spec + Qwen tracks (Track B today); QC = Qwen spec + Claude tracks; CQ = Claude spec + Qwen "
          "tracks; CC = Claude spec + Claude tracks (Track A geometry). Claude rows are a diagnostic yardstick only.")

    print("\n== 2a. role mixes on the Qwen spec (geometry + CaW fallback): which track matters")
    res = {}
    for k in ("QQ", "PcTq", "PqTc", "QC", "Qbox", "Cbox"):
        fb = np.where(np.isfinite(D[k]), D[k], D.caw)
        res[k] = dict(**macro(items(fb, g), c), geo_cov=float(np.isfinite(D[k]).mean()))
    print(pd.DataFrame(res).T.round(3).to_string())
    print("  PcTq = Claude prior track + Qwen target track; PqTc = Qwen prior + Claude target; Qbox / Cbox = boxes only "
          "(extent endpoints and points dropped)")

    print("\n== 2b. by subset (src), geometry+CaW fallback item means")
    for k in ("QQ", "QC", "CQ", "CC"):
        D[f"it_{k}"] = items(np.where(np.isfinite(D[k]), D[k], D.caw), g)
    D["it_caw"] = items(D.caw, g)
    print(D.groupby(["category", "src"])[["it_caw", "it_QQ", "it_QC", "it_CQ", "it_CC"]].agg("mean").round(3)
          .join(D.groupby(["category", "src"]).size().rename("n")).to_string())

    print("\n== 3. per-row attribution of the QQ loss (geometry+CaW fallback; a component 'limits' a row when "
          "swapping it in gains >= .2)")
    tr_lim = (D.it_QC - D.it_QQ) >= 0.2
    sp_lim = (D.it_CQ - D.it_QQ) >= 0.2
    both = (D.it_CC - D.it_QQ) >= 0.2
    lab = np.select([tr_lim & ~sp_lim, sp_lim & ~tr_lim, tr_lim & sp_lim, both & ~tr_lim & ~sp_lim],
                    ["tracks", "spec", "tracks&spec", "joint(spec+tracks needed)"], "neither")
    D["limit"] = lab
    loss = (1 - D.it_QQ)
    gain_cc = (D.it_CC - D.it_QQ)
    A = D.assign(loss=loss, gain_cc=gain_cc, gain_qc=D.it_QC - D.it_QQ, gain_cq=D.it_CQ - D.it_QQ) \
        .groupby(["category", "limit"])[["loss", "gain_qc", "gain_cq", "gain_cc"]].sum().round(2)
    A["n"] = D.groupby(["category", "limit"]).size()
    print(A.to_string())

    print("\n== 3b. spec agreement Qwen vs Claude (share of rows)")
    sp = [k for k in D.columns if k.startswith("spec_")]
    print(D.groupby("category")[sp].mean().round(3).to_string())

    print("\n== 4. grounding classes (Qwen vs Claude tracks; centre_rel = centre distance / object size)")
    for role in ("prior", "target"):
        col = f"{role}_centre_rel"
        if col not in D:
            continue
        s = D[col]
        wrong = s > 1.0
        er = D.get(f"{role}_ext_ratio")
        mr = D.get(f"{role}_mot_ratio")
        print(f"  {role}: compared {int(s.notna().sum())} rows; wrong object (centre off > 1 object size) "
              f"{int(wrong.sum())} ({wrong[s.notna()].mean():.0%}); median centre_rel {s.median():.2f}")
        if er is not None and er.notna().any():
            le = np.abs(np.log(er.dropna()))
            print(f"    extent ratio Qwen/Claude: n {len(le)}, median |log| {le.median():.3f}, "
                  f"> 15% off {np.mean(le > math.log(1.15)):.0%}, > 50% off {np.mean(le > math.log(1.5)):.0%}")
        if mr is not None and mr.notna().any():
            lm = np.abs(np.log(mr.dropna().clip(lower=1e-3)))
            print(f"    motion displacement ratio Qwen/Claude: n {len(lm)}, median |log| {lm.median():.3f}, "
                  f"> 15% off {np.mean(lm > math.log(1.15)):.0%}, > 50% off {np.mean(lm > math.log(1.5)):.0%}")
    # loss in rows where a role is wrong object
    D["wrong_any"] = (D.get("prior_centre_rel", pd.Series(np.nan, index=D.index)) > 1.0) | \
                     (D.get("target_centre_rel", pd.Series(np.nan, index=D.index)) > 1.0)
    print("\n  QQ(+fb) loss and QC gain by wrong-object flag:")
    print(D.assign(loss=loss, gain_qc=D.it_QC - D.it_QQ).groupby(["category", "wrong_any"])[["loss", "gain_qc"]]
          .agg(["sum", "count"]).round(2).to_string())
    print("\n  flags of QQ failures (no geometry value):")
    print(Counter(f for fl, v in zip(D.flags_QQ, D.QQ) if not np.isfinite(v) for f in str(fl).split(";")).most_common(12))


if __name__ == "__main__":
    main()
