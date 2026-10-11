"""Candidates (c)-(e) and the radial-anchoring check, test inputs only (stated priors / family facts as exact labels).
    .venv/bin/python research/sim3d/audit_conventions.py
"""
from __future__ import annotations

import json

from audit_radial import lofo_table, radial
from common import ROOT, load_split, table, answers, parse_prior_text, np, pd


def main():
    t = table()
    a = answers(t)
    x = t.join(a)
    f = lofo_table(t, a)
    # anchoring: our speed answer within [1.00, 1.05] x |dr/dt| (the radial lower bound)
    sp = x[x.kind == "speed"].copy()
    sp["vr"] = [radial(r.depth_info, r.objs[0]) if r.objs else np.nan for r in sp.itertuples()]
    sp = sp.dropna(subset=["vr"])
    anch = sp[(sp.dmed >= 0.995 * sp.vr) & (sp.dmed <= 1.05 * sp.vr)]
    known = anch.join(f.stated, how="inner")
    print(f"(a') speed answers sitting on the radial lower bound |dr/dt| (within +5%): {len(anch)} of {len(sp)}; "
          f"with a family-stated label {len(known)}: " + ", ".join(
              f"{q} {r.video_id} ans {r.dmed:g} |dr/dt| {r.vr:.2f} stated {r.stated:g}" for q, r in known.iterrows()))
    # (c) accelerations
    ac = x[x.kind == "acceleration"]
    print(f"(c) acceleration questions: S3 {int((ac.category == 'S3').sum())}, D3 {int((ac.category == 'D3').sum())}; "
          f"objects: {ac.objs.map(lambda o: o[0] if o else '').value_counts().to_dict()}")
    acc_f = f[f.kind == "acceleration"]
    print(f"    stated (LOFO) accelerations: {len(acc_f)}; ratio ours/stated {acc_f.dmed.div(acc_f.stated).round(2).tolist()}")
    full = load_split("test")
    ff = [ln.strip() for p in full.prior.drop_duplicates() for ln in str(p).split("\n")
          if parse_prior_text(ln)["kind"] == "acceleration" and abs((parse_prior_text(ln)["value_si"] or 0) - 9.8) < 0.15]
    print(f"    priors stating a free-fall phase as ~9.8 m/s^2: {sorted(set(ff))}")
    # (d) sizes by dimension / object class
    sz = f[f.kind == "size"].copy()
    sz["r"] = sz.dmed / sz.stated
    sz["obj"] = sz.objs.map(lambda o: o[0] if o else "")
    print("(d) LOFO size answers (median of 3 runs) / stated, by dimension:")
    print(sz.groupby("dim").r.agg(["size", "median"]).round(3).to_string())
    per = sz[sz.obj.str.contains("person|man|human|pedestrian")]
    print(f"    person heights (label = T-pose height): n={len(per)}, median ours/stated {per.r.median():.3f} "
          f"(a walking-pose underestimate would read < 1)")
    tc = full[full.question.str.contains("length of the turning yellow car", case=False)]
    print(f"    'length of the turning yellow car' asked in {tc.video_id.nunique()} clips; stated once per scenario: "
          f"'length of the yellow car = 5.44m' (0070/0071) -> one length for a car that turns (no yaw-dependent AABB)")
    # (e) units, fps, out-of-range times
    print(f"(e) target units in 3D non-lab: {x.target_unit.value_counts().to_dict()}")
    nf = {}
    for v in x.video_id.unique():
        r = json.load(open(ROOT / f"runs/test_v1_high_854/test/records/{v}.json"))
        nf[v] = (r["meta"]["n_frames_total"], r["meta"]["fps_from_container"])
    print(f"    fps from the container (instead of the dataset): {sum(v[1] for v in nf.values())} of {len(nf)} clips")
    tq = x.qtime.where(x.qtime.notna(), x.qwin.map(lambda w: w[1] if isinstance(w, list) else np.nan))
    dur = x.video_id.map(lambda v: nf[v][0]) / x.fps
    print(f"    questions asked after the clip ends: {int((tq > dur + 1e-6).sum())} "
          f"({', '.join(map(str, x.index[tq > dur + 1e-6]))}: 'minimum distance at t=3s' in 2.75 s clips)")


if __name__ == "__main__":
    main()
