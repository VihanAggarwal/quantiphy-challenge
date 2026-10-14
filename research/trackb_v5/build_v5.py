"""Build Track B v5 submissions (open-weight outputs + model-free code + test inputs only).

    .venv/bin/python research/trackb_v5/build_v5.py --out submissions/trackB_cand_v5.csv [--no-l2q] [--no-l1] [--l6s] [--l4]

Pipeline on the TEST question table:
 1. per-category log-median of the v3 members (S2 caw+cv_geo+qwen_direct, D2 caw+cv_geo+qwen_direct+qwen_geo,
    S3 cv_geo+qwen_geo+qwen_direct, D3 caw+qwen_geo+qwen_direct); L2': in S3/D3 qwen_geo -> qwen_fov (the Qwen-track
    geometry re-solved with the fixed lab camera, 722 px at 1280 px; differs from qwen_geo on 3D lab rows only).
    L6s (optional, post-hoc): 2D rows of simulation clips with a frame-aligned segmented twin -> the twin-mask
    snapped cvq geometry alone (research/trackb_v5/seg_snap.py; CaW fallback).
 2. qp.postprocess preset "trackb".
 3. L1: S3 lab motion rows (speed / path length / displacement) without a stated value x the lab label-noise emulator
    factor (research/trackb_dense/labnoise_open.py; Qwen 3D tracks, sigma_z 2 cm fitted on the test lab speed priors).
 4. L4 (optional): free-fall speed rows of the simulation drop events -> a*(t_k - t0 - 1/(2 fps)) (research/path85b_phys,
    t0 from model-free background-subtraction tracks).
 5. scripts/make_submission.py.
"""
import argparse
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
from harness import CATS, V3, Data  # noqa: E402
import labnoise_open as LN  # noqa: E402
from tbcommon import specs as load_specs, with_fallback  # noqa: E402

STATED = ["facts", "motionfam", "freefall", "labfacts"]


def l6s_values(D):
    R = pd.read_csv(HERE / "out_test_cvq_seg.csv")
    R = R[R.video_id.str.startswith("simulation")].set_index("id")
    sp = load_specs("test")
    kinds = pd.Series({q: sp[q].target.kind for q in R.index if q in sp})
    caw = pd.Series(D.P["test"]["caw"].to_numpy(), index=D.test.qid)
    v = with_fallback(R.geo_value, R.geo_si, kinds, caw.reindex(R.index)).dropna()
    # only rows answered by the snapped geometry itself (rows where it fell back to CaW keep the member median)
    return v[~np.isclose(v, caw.reindex(v.index), rtol=1e-9) & np.isclose(v, R.geo_value.reindex(v.index), rtol=1e-9)]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-l2q", action="store_true")
    ap.add_argument("--no-l1", action="store_true")
    ap.add_argument("--l6s", action="store_true")
    ap.add_argument("--l4", action="store_true")
    a = ap.parse_args(argv)
    D = Data()
    sets = V3 if a.no_l2q else {c: [("qwen_fov" if m == "qwen_geo" and c in ("S3", "D3") else m) for m in v]
                                 for c, v in V3.items()}
    raw = D.raw(sets, "test")
    if a.l6s:
        v = l6s_values(D)
        raw.loc[v.index] = v.to_numpy()
    post, log = D.rules(raw, df=D.test)
    final = post.copy()
    if not a.no_l1:
        stated = set(log[log.applied & log.rule.isin(STATED)].qid.astype(int))
        F = LN.factors("test", "qwen", post, 0.02, 0.02)
        cat = D.test.set_index("qid").category
        F = F[(F.id.map(cat) == "S3") & ~F.id.isin(stated) & (F.factor != 1)]
        final.loc[F.id] = final.loc[F.id].to_numpy() * F.factor.to_numpy()
        print(f"L1: {len(F)} S3 lab motion rows x factor (median {F.factor.median():.3f})")
    if a.l4:
        C = pd.read_csv(ROOT / "research/path85b_phys/changes_ffbd.csv")
        final.loc[C.qid] = C.new.to_numpy()
        print(f"L4: {len(C)} free-fall speed rows set to the backward-difference value")
    assert final.notna().all() and np.isfinite(final).all() and (final > 0).all()
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": D.test.qid, "parsed_value": final.reindex(D.test.qid).to_numpy()}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, a.out], check=True)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
