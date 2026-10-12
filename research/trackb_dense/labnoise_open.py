"""Lab label-noise emulation (research/labnoise) on OPEN-MODEL tracks (Track B).

research/labnoise used Claude's tracks; here the 3D tracks come from Qwen3-VL's grounding boxes (or the SAM 2
tracks) re-solved with the fixed lab camera (f = 722 px at 1280 px, depth_info as range, qp.geometry), and the
noise parameters are re-fitted on the TEST speed priors measured on those same open tracks (inputs, not labels).

    .venv/bin/python research/trackb_dense/labnoise_open.py tracks val|test [--src qwen|cv]
    .venv/bin/python research/trackb_dense/labnoise_open.py fit [--src qwen]
    .venv/bin/python research/trackb_dense/labnoise_open.py factors val|test [--src qwen] [--sz 0.02]

factors writes out/<split>/labnoise_<src>.csv: id, factor (1 = unchanged), kind, cls, sin_psi, for lab motion
targets (speed / path length / displacement; accelerations and near-static objects untouched; emulate.row_model).
The factor multiplies whatever Track B answer the row has (evaluated in evaluate_labnoise below).
"""
from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "research" / "labnoise"))
from tbcommon import CACHE, OUT, questions  # noqa: E402
from qp import geometry as G  # noqa: E402
from solve import annotations  # noqa: E402


def build_tracks(split: str, src: str) -> dict:
    df = questions(split)
    df = df[df.video_source == "lab"]
    anns, paths, meta = annotations(split, src, df)
    fix = {"f": None}
    cap: dict = {}
    orig_map, orig_measure = G._map_f, G._measure

    def capture(*args, **kw):
        a, va, role = args[1], args[3], args[7]
        try:
            if a is not None and a.rows and va.rng is not None and va.f is not None and abs(va.f - fix["f"]) < 1e-6:
                t, uv = a.points()
                if len(t):
                    cap[role] = dict(t=np.asarray(t, float), uv=np.asarray(uv, float), P=va.pos(t, uv),
                                     rng=np.asarray(va.rng(t), float), name=a.name, f=va.f, c=np.asarray(va.c))
        except Exception as e:  # noqa: BLE001
            cap[role + "_err"] = repr(e)
        return orig_measure(*args, **kw)

    G._map_f = lambda fn, value, width, f_cam: fix["f"]
    G._measure = capture
    out = {}
    try:
        for r in df.itertuples():
            a = anns.get(int(r.qid))
            if a is None:
                continue
            fps, (W, H), _ = meta[int(r.qid)]
            fix["f"] = 722.0 * W / 1280
            cap.clear()
            ans = G.solve(a.spec, a.tracks, (W, H), fps, camera_fov_deg=84.0)
            out[int(r.qid)] = dict(video=r.video_id, category=r.category, question=r.question, prior=r.prior,
                                   spec=a.spec, image_size=(W, H), fps=fps, cap=dict(cap), value=ans.value,
                                   flags=list(ans.flags))
    finally:
        G._map_f, G._measure = orig_map, orig_measure
    CACHE.mkdir(parents=True, exist_ok=True)
    pickle.dump(out, open(CACHE / f"labtracks_{split}_{src}.pkl", "wb"))
    print("saved", len(out), "lab questions;", sum("prior" in v["cap"] for v in out.values()), "with a prior 3D track;",
          sum("target" in v["cap"] for v in out.values()), "with a target 3D track")
    return out


def load_tracks(split, src):
    return pickle.load(open(CACHE / f"labtracks_{split}_{src}.pkl", "rb"))


def _fit(src: str) -> dict:
    import labmodel as LM
    import importlib.util
    spec = importlib.util.spec_from_file_location("lncommon", ROOT / "research" / "labnoise" / "common.py")
    ln = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ln)
    d = load_tracks("test", src)
    ev = []
    for q, x in sorted(d.items()):
        if x["spec"].prior.kind != "speed" or "prior" not in x["cap"] or x["spec"].prior.time is None:
            continue
        if x["video"] in ("captured_0062s", "captured_0062x"):
            continue
        c = x["cap"]["prior"]
        if len(c["t"]) < 5:
            continue
        tr, P = ln.track_real(c)
        t0 = float(ln.treal([float(x["spec"].prior.time)])[0])
        f = ln.local_fit(tr, P, t0, 0.25)
        if f is None:
            continue
        pos, vel, _ = f
        ev.append(dict(video=x["video"], event=x["video"][:13] + ("a" if "0054a" in x["video"] else "b" if "0054b" in x["video"] else ""),
                       cls=ln.obj_class(c["name"]), stated=float(x["spec"].prior.value_si), p=pos, v=vel,
                       speed=float(np.linalg.norm(vel)), sin_psi=ln.lateral_fraction(pos, vel)))
    ev = pd.DataFrame(ev).drop_duplicates("video")
    rows = []
    for e, g in ev.groupby("event"):
        g = g.sort_values("speed")
        rows.append(g.iloc[len(g) // 2])
    E = pd.DataFrame(rows).reset_index(drop=True)
    E["ball"] = E.cls.isin(["small ball", "mid ball"])
    # open-model tracks are noisier than Claude's: our own measurement error sd 0.25 (vs 0.10 there)
    sig_m = 0.25
    print(E[["event", "cls", "stated", "speed", "sin_psi"]].assign(ratio=E.stated / E.speed).round(3).to_string())

    def loglik(szb, szL):
        ll = 0.0
        for _, r in E.iterrows():
            sz = szb if r.ball else szL
            L = np.concatenate([LM.speed_labels(r.p, r.v * np.exp(e * sig_m), 2.0, sz, n=750, seed=2)
                                for e in (-1.5, -0.5, 0.5, 1.5)])
            h = 0.04
            z = (np.log(r.stated) - np.log(L)) / h
            ll += np.log(np.mean(np.exp(-0.5 * z * z)) / (h * np.sqrt(2 * np.pi)) + 1e-12)
        return float(ll)
    gb = [0.0, 0.005, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10]
    gL = [0.0, 0.01, 0.02, 0.05]
    tab = {(b, L): loglik(b, L) for b in gb for L in gL}
    best = max(tab, key=tab.get)
    prof = {b: max(tab[(b, L)] for L in gL) - tab[best] for b in gb}
    out = dict(sigma_zb=best[0], sigma_zL=best[1], n_events=len(E), profile_zb=prof)
    print("fit:", json.dumps(out, indent=1))
    json.dump(out, open(OUT / f"labnoise_fit_{src}.json", "w"), indent=1)
    return out


def factors(split: str, src: str, answers: pd.Series, sz_b: float, sz_L: float, cap: float | None = 1.6) -> pd.DataFrame:
    """Emulator factor per lab motion row for the given answers (Series by qid)."""
    import emulate as EM
    d = load_tracks(split, src)
    df = questions(split).set_index("qid")
    params = dict(EM.PARAMS, sigma_zb=sz_b, sigma_zL=sz_L)
    rows = []
    for q, x in sorted(d.items()):
        kind = EM.motion_kind(x["question"])
        if kind is None:
            continue
        A = answers.get(q, np.nan)
        m = None
        if kind != "acceleration" and np.isfinite(A) and A > 0:
            try:
                m = EM.row_model(x, A, df.loc[q, "target_unit"], params, cap=cap)
            except Exception:  # noqa: BLE001
                m = None
        f = m["factor"] if m else 1.0
        if abs(f - 1) < 0.03:
            f = 1.0
        rows.append(dict(id=q, video=x["video"], category=x["category"], kind=kind, factor=f,
                         cls=(m or {}).get("cls"), sin_psi=(m or {}).get("sin_psi")))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("split", nargs="?", default="val")
    ap.add_argument("--src", default="qwen")
    a = ap.parse_args()
    if a.cmd == "tracks":
        build_tracks(a.split, a.src)
    elif a.cmd == "fit":
        _fit(a.src)
