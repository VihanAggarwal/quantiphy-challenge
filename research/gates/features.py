"""Input-time gate signals for every test row (no labels, no API).

    ANTHROPIC_API_KEY="" ANTHROPIC_BASE_URL="http://127.0.0.1:9" QP_LEDGER=<scratch> \
        .venv/bin/python research/gates/features.py

From run a's records (Claude's own pixel tracks, no refinement / dense tracking):
  geo_ro       geometry replayed with refine off, dense off (the D2 configuration of the submission); lab rows
               with the lab camera FOV, like run_claude.build_results
  geo_ro_flags qp.geometry flags of that solve
  u_t, u_p     relative uncertainty of the target / prior measurement from its pixel track (RESULT.md)
  u_geo        sqrt(u_t^2 + u_p^2), unknown terms = 0, capped at 1
3D non-lab: per-run geometry, sensitivity, FOV, method, flags from research/simfov/out/replay.csv.
Writes research/gates/out/features.csv."""
from __future__ import annotations

import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
import qp.geometry as G  # noqa: E402
import run_claude as rc  # noqa: E402
from qp import combine  # noqa: E402
from qp.data import load_split  # noqa: E402
from qp.spec import RoleTrack  # noqa: E402

OUT = ROOT / "research/gates/out"


def _role_obj(tracks, role):
    best = None
    for tr in tracks or []:
        tr = RoleTrack.from_dict(tr) if isinstance(tr, dict) else tr
        if str(tr.role).strip().lower() != role:
            continue
        o = G._Obj(tr, set())
        if o.rows and (best is None or len(o.rows) > len(best.rows)):
            best = o
    return best


def rel_unc(q, obj, fps) -> float:
    """Relative standard error of quantity q measured on obj's pixel track (nan = unknown)."""
    if obj is None or q is None:
        return math.nan
    kind = q.kind
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            if kind in ("size", "other"):
                t, mid, L = obj.lengths(q.dimension, box=True)
                if len(L) < 3 or L.mean() <= 0:
                    return math.nan
                return float(np.std(L, ddof=1) / np.mean(L))
            if kind in ("distance", "camera_distance"):
                return math.nan
            t, P = obj.points()
            if len(np.unique(t)) < 4:
                return math.nan
            time = G._num(q.time, inf_ok=True)
            win = G._window(q)
            if time is not None and math.isfinite(time):
                t0 = float(np.clip(time, t.min(), t.max()))
            else:
                t0 = None
            if kind == "speed":
                if t0 is not None and not win:
                    f = G._local(t, P, t0, G.SPEED_HALF_WIN)
                    v = float(np.linalg.norm(f[1]))
                    return min(1.0, f[4] * f[6][1] / v) if v > 0 else 1.0
                sel = (t >= win[0] - 1e-9) & (t <= win[1] + 1e-9) if win else np.ones(len(t), bool)
                if sel.sum() < 4:
                    sel = np.ones(len(t), bool)
                ts, Ps = t[sel], P[sel]
                f = G._local(ts, Ps, float((ts[0] + ts[-1]) / 2), math.inf, max_deg=2)
                disp = float(np.linalg.norm(Ps[-1] - Ps[0]))
                path = float(np.linalg.norm(np.diff(Ps, axis=0), axis=1).sum())
                return min(1.0, math.sqrt(2) * f[4] / max(disp, path / 2, 1e-9))
            if kind == "acceleration":
                if t0 is not None and not win:
                    for half in (math.inf, 2 * G.ACC_HALF_WIN, G.ACC_HALF_WIN):
                        f = G._local(t, P, t0, half, max_deg=4)
                        if f[3] < 4:
                            break
                else:
                    sel = (t >= win[0] - 1e-9) & (t <= win[1] + 1e-9) if win else np.ones(len(t), bool)
                    if sel.sum() < 4:
                        sel = np.ones(len(t), bool)
                    ts = t[sel]
                    f = G._local(ts, P[sel], float((ts[0] + ts[-1]) / 2), math.inf, max_deg=2)
                if f[3] < 2:
                    return math.nan
                a = float(np.linalg.norm(f[2]))
                return min(1.0, f[4] * f[6][2] / a) if a > 0 else 1.0
            if kind in ("displacement", "path_length"):
                f = G._local(t, P, float((t[0] + t[-1]) / 2), math.inf, max_deg=3)
                disp = float(np.linalg.norm(P[-1] - P[0]))
                return min(1.0, math.sqrt(2) * f[4] / disp) if disp > 0 else 1.0
        except Exception:  # noqa: BLE001
            return math.nan
    return math.nan


def main():
    df = load_split("test")
    records = rc.load_records(ROOT / "runs/test_v1_high_854/test/records")
    anns = rc.annotations(df, records, refine_priors=False, dense="off")
    recs = rc.prepare_records(df, records)
    rows = []
    for r in df.itertuples():
        a = anns.get(int(r.qid))
        if a is None:
            rows.append(dict(qid=int(r.qid)))
            continue
        rec = recs[r.video_id]
        size, fps = tuple(rec["meta"]["image_size"]), float(rec["meta"]["fps"])
        seen = float(rec["meta"].get("scale") or 1.0)
        src = str(r.video_source or "")
        fov = rc.LAB_FOV_DEG if src in combine.CAMERA_SOURCES and a.spec.is_3d else None
        ans = G.solve(a.spec, a.tracks, size, fps, seen_scale=seen, **({"camera_fov_deg": fov} if fov else {}))
        ta, pa = _role_obj(a.tracks, "target"), _role_obj(a.tracks, "prior")
        u_t, u_p = rel_unc(a.spec.target, ta, fps), rel_unc(a.spec.prior, pa, fps)
        if G._is_gravity(a.spec.prior) and pa is None:
            pa_alt = ta
            u_p = rel_unc(a.spec.prior, pa_alt, fps)
        u_geo = min(1.0, math.sqrt(np.nan_to_num(u_t) ** 2 + np.nan_to_num(u_p) ** 2))
        rows.append(dict(qid=int(r.qid), geo_ro=ans.value, geo_ro_method=ans.method,
                         geo_ro_flags=";".join(ans.flags), dir_rec=a.direct_answer, conf=a.confidence,
                         tkind=a.spec.target.kind, pkind=a.spec.prior.kind if a.spec.prior else None,
                         n_t=len(ta.rows) if ta else 0, n_p=len(pa.rows) if pa else 0,
                         u_t=u_t, u_p=u_p, u_geo=u_geo))
    f = pd.DataFrame(rows).set_index("qid")
    # 3D non-lab per-run geometry diagnostics (simfov replay, f solved from the prior)
    rp = pd.read_csv(ROOT / "research/simfov/out/replay.csv")
    key = {"test_v1_high_854": "a", "test_3dnl_v1_high_b": "b", "test_3dnl_v2_high": "c"}
    for run, k in key.items():
        x = rp[rp.run == run].set_index("qid")
        for c in ("geo_old", "sens_old", "fov_old", "method_old", "flags_old", "direct"):
            f[f"{c}_{k}"] = x[c].reindex(f.index)
    f.to_csv(OUT / "features.csv")
    print(f"wrote {OUT / 'features.csv'}: {len(f)} rows")


if __name__ == "__main__":
    main()
