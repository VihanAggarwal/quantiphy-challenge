"""Run the prior-motion candidates (prior_motion.py) on every 2D question with a motion prior.

    .venv/bin/python research/trackb_dense/run_prior.py val|test [--workers 4]

Target tracks: Qwen's after qp.dense_track (anns_<split>_<dense tag>.pkl from solve.py --save-anns), so only the
prior's track changes. Writes out/<split>/prior_cands.csv (one row per question: each candidate's value and prior
measurement, the choice) and out/<split>/qwen_dyn.csv (solve.py format, the chosen candidate's solution; every
other question keeps the dense solution).
"""
from __future__ import annotations

import argparse
import math
import pickle
import sys
from multiprocessing import Pool
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prior_motion as PM  # noqa: E402
from tbcommon import CACHE, OUT, questions, tracks  # noqa: E402
from qp.geometry import solve  # noqa: E402
from qp.spec import RoleTrack  # noqa: E402
from solve import annotations  # noqa: E402

ARGS = {}


def job(item):
    vid, rows = item
    out = []
    for r in rows:
        q, spec, sparse, dense, cvtr, path, fps, size = r
        prior = next((t for t in sparse if t.role == "prior"), None)
        dprior = next((t for t in dense if t.role == "prior"), None)
        rec = dict(id=q, video_id=vid)
        if prior is None:
            rec["skip"] = "no_prior_track"
            out.append(rec)
            continue
        try:
            cands, info = PM.candidates(ARGS["split"], path, fps, prior, cvtr, dprior)
        except Exception as e:  # noqa: BLE001
            rec["skip"] = f"error:{type(e).__name__}:{e}"
            out.append(rec)
            continue
        rec.update({k: v for k, v in info.items() if isinstance(v, (int, float, str))})
        est = {}
        for name, (tr, ci) in cands.items():
            v, px, fl = PM.measure_prior(spec, dense, size, fps, tr)
            if name == "klt" and "halves" in ci and px:
                if not PM.halves_ok(spec, dense, size, fps, prior, ci["halves"]):
                    rec["klt_halves_fail"] = 1
                    continue
            rec[f"v_{name}"], rec[f"px_{name}"] = v, px
            if px and v:
                est[name] = px
        pick, grp = PM.choose({k: v for k, v in est.items() if k != "sparse"})
        rec["pick"], rec["group"] = pick, "+".join(grp)
        rec["value"] = rec.get(f"v_{pick}", math.nan) if pick else math.nan
        rec["_track"] = cands[pick][0] if pick else None
        out.append(rec)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("split")
    ap.add_argument("--dense-tag", default="")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--videos", default="")
    a = ap.parse_args(argv)
    ARGS["split"] = a.split
    df = questions(a.split)
    sparse, paths, meta = annotations(a.split, "qwen", df)
    dtag = a.dense_tag or ("qwen_dense" if a.split == "val" else "qwen_dense_labfov")
    dense = pickle.load(open(CACHE / f"anns_{a.split}_{dtag}.pkl", "rb"))
    cvrec = tracks(a.split, "cv")
    by = {}
    for r in df.itertuples():
        q = int(r.qid)
        if r.video_type[1] != "2" or q not in sparse or q not in dense:
            continue
        if a.videos and r.video_id not in a.videos.split(","):
            continue
        spec = sparse[q].spec
        if spec.prior.kind not in PM.MOTION:
            continue
        cv = None
        rec = cvrec.get(r.video_id)
        if rec and str(q) in rec.get("tracks", {}):
            cv = next((RoleTrack.from_dict(t) for t in rec["tracks"][str(q)] if t["role"] == "prior"), None)
        by.setdefault(r.video_id, []).append((q, dense[q].spec, sparse[q].tracks, dense[q].tracks, cv, paths[q],
                                              meta[q][0], meta[q][1]))
    items = sorted(by.items())
    print(len(items), "videos", sum(len(v) for _, v in items), "questions", flush=True)
    rows = []
    with Pool(a.workers, initializer=ARGS.update, initargs=({"split": a.split},)) as pool:
        for i, res in enumerate(pool.imap_unordered(job, items)):
            rows += res
            if i % 20 == 0:
                print(i, res[0]["video_id"] if res else "", flush=True)
    pickle.dump({r["id"]: r.pop("_track", None) for r in rows}, open(CACHE / f"prior_tracks_{a.split}.pkl", "wb"))
    for r in rows:
        r.pop("_track", None)
    R = pd.DataFrame(rows).sort_values("id")
    R.to_csv(OUT / a.split / "prior_cands.csv", index=False)
    print(R.pick.value_counts(dropna=False).to_dict())


if __name__ == "__main__":
    main()
