"""L1 lab label-noise emulator (S3 lab motion), L2 fixed lab camera members, L3 twin/render pooling.

    .venv/bin/python research/trackb_v5/levers_a.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "trackb_dense"))
from harness import CATS, V3, VAL_OFFSET, Data, fmt, src_of  # noqa: E402
import labnoise_open as LN  # noqa: E402
from qp import postprocess as pp  # noqa: E402

FOV = {"qwen_geo": "qwen_fov", "cv_geo": "cv_fov", "cvq_geo": "cvq_fov"}
STATED = ["facts", "motionfam", "freefall", "labfacts"]


def labnoise(D, post, log, df, sz_b=0.02, sz_l=0.02, cats=("S3",)):
    stated = set(log[log.applied & log.rule.isin(STATED)].qid.astype(int))
    out = post.copy()
    frames = []
    for split, off in (("test", 0), ("val", VAL_OFFSET)):
        A = pd.Series({q - off: v for q, v in post.items() if (q >= VAL_OFFSET) == (off > 0)})
        F = LN.factors(split, "qwen", A, sz_b, sz_l)
        F["qid"] = F.id + off
        frames.append(F)
    F = pd.concat(frames)
    cat = df.set_index("qid").category
    F = F[F.qid.isin(cat.index) & F.qid.map(cat).isin(cats) & ~F.qid.isin(stated) & (F.factor != 1)]
    out.loc[F.qid] = out.loc[F.qid].to_numpy() * F.factor.to_numpy()
    return out, F


def changed_rows(D, a, b, cat=None):
    q = a.index[(~np.isclose(a, b.reindex(a.index), rtol=1e-9, equal_nan=True))]
    q = q[q < VAL_OFFSET]
    t = D.test.set_index("qid").category
    return pd.Series(t.reindex(q).to_numpy()).value_counts().to_dict()


def affected_val(D, a, b):
    ia, ib = D.items(a), D.items(b)
    m = ~np.isclose(a.reindex(D.lab.index), b.reindex(D.lab.index), rtol=1e-9, equal_nan=True)
    return int(m.sum()), float((ib[m] - ia[m]).sum())


if __name__ == "__main__":
    D = Data()
    pred = D.combined(V3)
    post, log = D.rules(pred)
    print("BASE v3+rules", fmt(D.score(post)))
    # ---------------- L1
    for szb, szl in [(0.02, 0.02)]:
        l1, F = labnoise(D, post, log, D.df, szb, szl)
        n, s = affected_val(D, post, l1)
        print(f"L1 labnoise sz {szb}/{szl}:", fmt(D.score(l1)), "| boot", fmt(D.boot(post, l1)),
              f"| val rows {n} item sum {s:+.2f} | test rows {changed_rows(D, post, l1)}",
              f"| test factor median {F[F.qid < VAL_OFFSET].factor.median():.3f}")
        print(F[F.qid < VAL_OFFSET].groupby(["cls", "kind"]).factor.agg(["size", "median"]).round(3).to_string())
    # ---------------- L2
    v3f = {c: [FOV.get(m, m) for m in v] for c, v in V3.items()}
    pf = D.combined(v3f)
    postf, logf = D.rules(pf)
    n, s = affected_val(D, post, postf)
    print("L2 fov:", fmt(D.score(postf)), "| boot", fmt(D.boot(post, postf)), f"| val rows {n} item sum {s:+.2f}",
          f"| test rows {changed_rows(D, post, postf)}")
    # ---------------- L3 twin / render pooling on top of the base rules
    ctx = pp._Ctx(pp._questions(D.df, None), pp.FrameCache(pp.DEFAULT_CACHE))
    stated = set(log[log.applied & log.rule.isin(STATED)].qid.astype(int))
    l3 = post.copy(); lg = []
    pp._pool_rule(l3, ctx, stated, lg, unit="clip", scope="base")
    n, s = affected_val(D, post, l3)
    print("L3 twin/render pool:", fmt(D.score(l3)), "| boot", fmt(D.boot(post, l3)), f"| val rows {n} item sum {s:+.2f}",
          f"| test rows {changed_rows(D, post, l3)}")
    lg = pd.DataFrame(lg)
    if len(lg):
        lg["src"] = lg.qid.map(dict(zip(D.df.qid, D.df.video_id))).map(src_of)
        print(lg.groupby("src").size().to_dict())
    pd.to_pickle(dict(post=post, log=log, l1=l1, F=F, postf=postf, l3=l3), HERE / "cache_levers_a.pkl")


def l2_qwen_only(D, post):
    """L2': fixed lab camera only for the Qwen-track member (the source passing the label-free check)."""
    s = {c: [("qwen_fov" if m == "qwen_geo" else m) for m in v] for c, v in V3.items()}
    p, lg = D.rules(D.combined(s))
    return p, lg
