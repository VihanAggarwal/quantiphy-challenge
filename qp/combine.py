"""Answer selection: Claude's direct answer vs the geometry answer, within one run and across runs.

Pure functions shared by scripts/run_claude.py (one run) and scripts/combine_runs.py (several run
CSVs with columns id, parsed_value, geo_value, direct_value, method, flags). Inputs per question:
the geometry value (None if unsolvable), the direct answer, the run's flags ("geo:<flag>" from
qp.geometry plus "geo_rejected_implausible" when the geometry answer blew up), whether the video
is 3D, its video_source and the geometry method.

Rules (RULES; DEFAULT_RULE = assumed_src). The rules were designed after seeing all 24 val videos, so
leave-one-video-out CV over them (it picks assumed_src in every fold) is weak evidence. The non-lab 3D
routing rests on 6 low-resolution val videos (direct beat geometry on 5 of 6 in every cached run; video
bootstrap assumed_src - geo +0.03, 90% CI +0.01..+0.05): re-check it per video on any new val run.
The PRIOR_SIDE_FLAGS exemption is one video's evidence (captured_0013), kept for its reasoning.
  geo          geometry unless rejected as implausible or > MAX_DISAGREE x off the direct answer
  assumed      geo, but a 3D geometry answer that rests on an assumed range or focal length
               (ASSUMED_FLAGS: no depth_info entry for the target / prior, default focal, no depth
               info at all; also the annotator's own range estimates until a run validates them) -> direct;
               with a known camera the prior-side ones (PRIOR_SIDE_FLAGS) do not count
  assumed_src  assumed, and 3D questions of videos without a known camera (video_source not in
               CAMERA_SOURCES) -> direct: there f comes from one prior alone
  3d_direct    every 3D question -> direct (camera_distance, a depth lookup, keeps geometry)
Every rule falls back to geometry when the direct answer is missing, and to direct when geometry is.

Across runs, each run's selected value is combined by the median in log space (combine_values).
"""

from __future__ import annotations

import math
from collections.abc import Iterable

GEO_MAX_SI = {"L": 1e4, "V": 1e3, "A": 1e3}   # m, m/s, m/s^2: a geometry answer beyond this is a blow-up
MAX_DISAGREE = 10.0          # geometry this many times off the direct answer: use the direct one
DISAGREE_FLAG = 3.0          # ... and flag (diagnostic only) beyond this ratio
CAMERA_SOURCES = ("lab",)    # video sources whose camera is known (qp.geometry camera prior)
ASSUMED_FLAGS = frozenset({
    "target_depth_from_prior", "target_depth_scene_median", "target2_depth_from_target", "target_depth_from_target2",
    "prior_depth_assumed_scene_median", "default_focal",
    "target_depth_claude_estimate", "target2_depth_claude_estimate", "prior_depth_claude_estimate",
    "3d_without_depth",  # a 3D question solved with one image-plane scale (no depth_info at all)
})
# Assumptions on the prior side enter the answer only through the focal length: with a known camera
# (CAMERA_SOURCES; qp.geometry's camera prior pins f) they do not make the geometry an assumption.
PRIOR_SIDE_FLAGS = frozenset({"default_focal", "prior_depth_assumed_scene_median"})
RULES = ("geo", "assumed", "assumed_src", "3d_direct")
DEFAULT_RULE = "assumed_src"
# flags choose() writes; recomputed (never read back) when a run CSV is re-evaluated
_OWN = ("geo_direct_disagree", "geo_rejected_disagree", "geo_rejected_assumed_depth",
        "geo_3d_no_camera", "geo_3d_direct_preferred")


def valid(v) -> bool:
    try:
        return v is not None and math.isfinite(float(v)) and float(v) > 0
    except (TypeError, ValueError):
        return False


def split_flags(flags) -> list[str]:
    if flags is None or (isinstance(flags, float) and math.isnan(flags)):
        return []
    if isinstance(flags, str):
        return [f for f in flags.split(";") if f]
    return [str(f) for f in flags]


def geo_flags(flags) -> set[str]:
    """qp.geometry's flags among a run's flags (prefix "geo:" stripped)."""
    return {f[4:] for f in split_flags(flags) if f.startswith("geo:")}


def choose(geo, direct, flags, is_3d: bool, video_source: str = "", method: str = "",
           rule: str = DEFAULT_RULE) -> tuple[float, str, list[str]]:
    """(value, how, flags added) for one question. `method` is the geometry method (e.g.
    "3d_focal_from_prior", "depth_direct"; a run CSV's "geometry:<method>" also works)."""
    if rule not in RULES:
        raise ValueError(f"unknown rule {rule!r} (expected one of {RULES})")
    fl = split_flags(flags)
    gflags, added = geo_flags(fl), []
    use_geo = valid(geo) and "geo_rejected_implausible" not in fl
    have_direct = valid(direct)
    if use_geo and have_direct:
        ratio = max(geo / direct, direct / geo)
        if ratio > DISAGREE_FLAG:
            added.append("geo_direct_disagree")
        if ratio > MAX_DISAGREE:
            added.append("geo_rejected_disagree")
            use_geo = False
    lookup = str(method or "").split(":")[-1] == "depth_direct"
    if use_geo and have_direct and is_3d and not lookup and rule != "geo":
        if rule == "3d_direct":
            added.append("geo_3d_direct_preferred")
            use_geo = False
        elif gflags & (ASSUMED_FLAGS - (PRIOR_SIDE_FLAGS if str(video_source or "") in CAMERA_SOURCES else set())):
            added.append("geo_rejected_assumed_depth")
            use_geo = False
        elif rule == "assumed_src" and str(video_source or "") not in CAMERA_SOURCES:
            added.append("geo_3d_no_camera")
            use_geo = False
    if use_geo:
        m = str(method or "").split(":")[-1]
        return float(geo), (f"geometry:{m}" if m and m != "geometry" else "geometry"), added
    if have_direct:
        return float(direct), "direct", added
    return math.nan, "none", added


def combine_values(values: Iterable) -> float:
    """Median in log space of the valid values (the geometric mean of the middle two for an even
    count); NaN if none is valid."""
    logs = sorted(math.log(float(v)) for v in values if valid(v))
    if not logs:
        return math.nan
    n = len(logs)
    mid = logs[n // 2] if n % 2 else (logs[n // 2 - 1] + logs[n // 2]) / 2
    return math.exp(mid)


def own_flags_removed(flags) -> list[str]:
    """A run's flags without the ones choose() derives (so a CSV can be re-evaluated)."""
    return [f for f in split_flags(flags) if f not in _OWN]


# --------------------------------------------------------------------------- tables (run CSVs)

def _geo_method(r) -> str:
    """The geometry method of a run-table row: its geo_method column, else from "geometry:<m>"."""
    gm = getattr(r, "geo_method", None)
    if isinstance(gm, str) and gm:
        return gm
    m = str(getattr(r, "method", "") or "")
    return m.split(":", 1)[1] if m.startswith("geometry:") else ""


def select_table(run, meta, rule: str = DEFAULT_RULE):
    """Re-select one run's answers with `rule`. run: DataFrame with id, geo_value, direct_value,
    method, flags (and geo_method when the run wrote it); meta: DataFrame with qid, video_type,
    video_source. Returns the table with parsed_value / method / flags re-derived (questions missing
    from `meta` are dropped)."""
    import pandas as pd

    info = meta.set_index("qid")[["video_type", "video_source"]]
    rows = []
    for r in run.itertuples():
        if int(r.id) not in info.index:
            continue
        vt, src = info.loc[int(r.id)]
        geo = r.geo_value if valid(r.geo_value) else None
        direct = r.direct_value if valid(r.direct_value) else None
        flags = own_flags_removed(r.flags)
        gm = _geo_method(r)
        if geo is None and direct is None:  # unanswered (missing record): keep its row as it is
            rows.append({"id": int(r.id), "parsed_value": math.nan, "geo_value": math.nan,
                         "direct_value": math.nan, "method": r.method, "flags": ";".join(flags), "geo_method": gm})
            continue
        value, how, added = choose(geo, direct, flags, str(vt)[1:2] == "3", str(src or ""), gm, rule)
        rows.append({"id": int(r.id), "parsed_value": value, "geo_value": geo if geo is not None else math.nan,
                     "direct_value": direct if direct is not None else math.nan, "method": how,
                     "flags": ";".join(sorted(set(flags + added))), "geo_method": gm})
    return pd.DataFrame(rows, columns=["id", "parsed_value", "geo_value", "direct_value", "method", "flags",
                                       "geo_method"])


def combine_tables(selected: list):
    """Several runs' selected tables -> one: per id, combine_values of the runs' parsed_value (and
    of their geo / direct values, for reference); `n_runs` counts the runs with a valid answer."""
    import pandas as pd

    ids = list(dict.fromkeys(i for t in selected for i in t["id"]))
    idx = [t.set_index("id") for t in selected]
    rows = []
    for i in ids:
        got = [t.loc[i] for t in idx if i in t.index]
        vals = [g.parsed_value for g in got]
        rows.append({"id": int(i), "parsed_value": combine_values(vals),
                     "geo_value": combine_values(g.geo_value for g in got),
                     "direct_value": combine_values(g.direct_value for g in got),
                     "method": "|".join(str(g.method) for g in got),
                     "flags": f"runs={sum(valid(v) for v in vals)}/{len(selected)}",
                     "n_runs": sum(valid(v) for v in vals)})
    return pd.DataFrame(rows, columns=["id", "parsed_value", "geo_value", "direct_value", "method", "flags", "n_runs"])


def lovo_cv(runs: list, meta, rules=RULES, combined: bool = False) -> dict:
    """Leave-one-video-out CV of the rule choice. runs: run tables (id, geo_value, direct_value,
    method, flags); meta: qp.data table with answers. For each held-out video the rule with the
    best mean MRA over the runs (combined=False: each run selected on its own; True: the runs
    combined by combine_tables) on the other videos is applied to it. Returns {"per_run": [CV MRA
    per run (or one value if combined)], "per_category": [...], "chosen": {video: rule},
    "in_sample": {rule: mean MRA}}."""
    import numpy as np
    from .mra import score

    m = meta[["qid", "video_id", "category", "answer"]]
    sel = {rule: [select_table(r, meta, rule) for r in runs] for rule in rules}
    if combined:
        sel = {rule: [combine_tables(ts)] for rule, ts in sel.items()}
    merged = {rule: [m.merge(t, left_on="qid", right_on="id", how="left") for t in ts] for rule, ts in sel.items()}

    def macro(sc: dict) -> float:  # the official macro MRA; categories present when one is absent
        return sc["mra"] if math.isfinite(sc["mra"]) else float(np.mean(list(sc["per_category"].values())))

    def mra(frames, keep):
        return float(np.mean([macro(score(f[keep(f)], "parsed_value")) for f in frames]))

    videos = list(dict.fromkeys(m["video_id"]))
    chosen, held = {}, {}
    for v in videos:
        best = max(rules, key=lambda rule: (mra(merged[rule], lambda f: f["video_id"] != v), -rules.index(rule)))
        chosen[v] = best
        for k, f in enumerate(merged[best]):
            held.setdefault(k, []).append(f[f["video_id"] == v])
    import pandas as pd
    out = [pd.concat(held[k]) for k in sorted(held)]
    scores = [score(f, "parsed_value") for f in out]
    return {"per_run": [macro(s) for s in scores], "per_category": [s["per_category"] for s in scores],
            "chosen": chosen, "in_sample": {rule: mra(merged[rule], lambda f: f["video_id"] == f["video_id"])
                                            for rule in rules}}
