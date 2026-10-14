"""Paid pilot (hard cap $5): v1 pipeline request + a convention block on world-axis bounding-box sizes, yaw and
origin depth, on the 6 validation 3D non-lab videos (52 questions). Kill test pre-registered in RESULT.md.

Same request as runs/val_hr_v1_high (claude-opus-5-5, effort high, 16 uniform + asked-time frames up to 32,
max side 2576, prompt v1); the only change is CONVENTION appended to the system prompt. Streaming, sync.

    .venv/bin/python research/aabb/run_pilot.py            # run (skips clips already in out/), then score
    .venv/bin/python research/aabb/run_pilot.py --dry      # build requests, print token estimates, no API call
    .venv/bin/python research/aabb/run_pilot.py --score    # score only
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from qp import budget  # noqa: E402
from qp import claude_annotate as ca  # noqa: E402
from qp.data import load_split  # noqa: E402
from qp.mra import item_scores  # noqa: E402

OUT = Path(__file__).parent / "out"
RUN = "aabb_pilot"
CAP_USD = 5.00

CONVENTION = """

Label conventions of the Blender simulation videos (this video is one; its ground truth and its prior were \
computed by script from the 3D scene):
- A size (length, width, height, diameter, wingspan, ...) is an extent of the object's bounding box aligned with \
the WORLD axes (two horizontal ground-plane axes and the vertical axis), enclosing the whole mesh (wheels, \
mirrors, masts, wings, raised limbs included). It is not the visible silhouette in one image and not an extent \
along the image axes.
- height = the full vertical extent of the object, lowest to highest point.
- length and width = the two horizontal extents of that world-aligned box. For an object whose own length is L \
and own width W, yawed by an angle a relative to the world axes, they are L|cos a| + W|sin a| and \
W|cos a| + L|sin a|; they equal L and W when the object is square to the world axes (a = 0). The world axes \
usually run along the scene's roads, lanes, piers, walls, floor tiles and other layout lines. Estimate a from the \
frames and apply this before answering. A prior size follows the same convention.
- The depth info distances are Euclidean (straight-line) ranges from the camera to the object's ORIGIN, its \
pivot point (roughly the centre of its body or base; a person's pelvis; a vehicle's rig root), not to the \
nearest visible surface. Use that range as the object's distance when converting its pixel extents and \
motion to metres."""


def val_rows() -> pd.DataFrame:
    v = load_split("val_hires")
    return v[(v.video_type.str[1] == "3") & (v.video_source != "lab")]


def my_spent() -> float:
    return sum(float(e.get("usd") or 0) for e in budget.entries() if e.get("type") == "usage" and e.get("run") == RUN)


def build(rows: pd.DataFrame) -> tuple[dict, dict]:
    params, meta = ca.build_request(rows, n_uniform=16, max_frames=32, effort="high", prompt_version="v1",
                                    max_side=2576)
    params["system"][0]["text"] = params["system"][0]["text"] + CONVENTION
    meta["convention"] = "aabb_v1"
    return params, meta


def run(dry: bool) -> None:
    v = val_rows()
    OUT.mkdir(parents=True, exist_ok=True)
    order = v.groupby("video_id").size().sort_values(ascending=False).index  # largest first
    client = None
    if not dry:
        import run_claude as rc
        rc.load_env()
        import anthropic
        client = anthropic.Anthropic(max_retries=5)
    for vid in order:
        rows = v[v.video_id == vid]
        f = OUT / f"{vid}.json"
        if f.exists():
            continue
        params, meta = build(rows)
        est_in = ca.estimate_input_tokens(params)
        worst = budget.estimate_usd(est_in * 1.15 + 2000, params["max_tokens"], ca.MODEL)
        print(f"{vid}: {len(rows)} q, {len(meta['frames'])} frames, est input {est_in} tok, "
              f"max_tokens {params['max_tokens']}, worst ${worst:.2f}; spent on this run so far ${my_spent():.3f}",
              flush=True)
        if dry:
            continue
        if my_spent() + worst > CAP_USD:
            print(f"  STOP: ${my_spent():.2f} + worst ${worst:.2f} would exceed the ${CAP_USD:.2f} cap", flush=True)
            break
        with budget.reserve(worst):
            with client.messages.stream(**params) as st:
                r = st.get_final_message()
            usd = budget.price(r.usage, ca.MODEL)
            budget.record(RUN, ca.MODEL, "sync", r.id, r.usage, usd=usd)
        text = ca.response_text(r)
        anns = ca.to_annotations(ca.parse_json(text) or {}, meta)
        direct = {int(q): a.direct_answer for q, a in anns.items()}
        f.write_text(json.dumps({"video": vid, "usd": usd, "usage": budget.usage_dict(r.usage),
                                 "stop_reason": r.stop_reason, "direct": direct, "meta": meta, "text": text}))
        print(f"  {r.usage.input_tokens} in / {r.usage.output_tokens} out, ${usd:.3f}, {len(direct)} answers, "
              f"stop {r.stop_reason}", flush=True)


def score() -> None:
    v = val_rows().set_index("qid")
    gt = v.answer.astype(float)
    vid = v.video_id.str.replace("_segmented", "", regex=False)

    def d(p):
        return pd.to_numeric(pd.read_csv(p).set_index("id").direct_value, errors="coerce").reindex(gt.index)

    base = d(ROOT / "runs/val_hr_v1_high/val_hires.csv")
    r2, r3 = d(ROOT / "runs/val_hr_v2_high/val_hires.csv"), d(ROOT / "runs/val_opus_high/val.csv")
    new = {}
    for f in OUT.glob("*.json"):
        new.update({int(k): x for k, x in json.loads(f.read_text())["direct"].items() if x is not None})
    aabb = pd.Series(new, dtype=float).reindex(gt.index)
    print(f"answered by the aabb run: {int(aabb.notna().sum())}/{len(gt)} (missing -> scored 0)")

    def med(*s):
        with np.errstate(all="ignore"):
            return np.exp(np.log(pd.concat(s, axis=1).where(lambda x: x > 0)).median(axis=1, skipna=True))

    def sc(s):
        return pd.Series(np.nan_to_num(item_scores(s.to_numpy(float), gt.to_numpy()), nan=0.0), index=gt.index)

    S = pd.DataFrame({"base_hr_v1": sc(base), "aabb": sc(aabb), "hr_v2": sc(r2), "opus": sc(r3),
                      "3run_v1_v2_opus": sc(med(base, r2, r3)), "3run_aabb_v2_opus": sc(med(aabb, r2, r3)),
                      "4run_with_aabb": sc(med(base, r2, r3, aabb))})
    from step1_bias import dim_word
    q = v.question
    size = (q.map(dim_word) != "other") & ~q.str.contains(r"distance|above the|clear height", case=False)
    S["group"] = np.where(size, "size", "other")
    print(S.drop(columns="group").mean().round(4).to_string())
    print("by group (size rows / other rows):")
    print(S.groupby("group").mean().round(4).to_string())
    rng = np.random.default_rng(0)

    def report(a, b, label):
        dd = S[a] - S[b]
        byclip = dd.groupby(vid).mean()
        clips = byclip.index.to_numpy()
        bs = [np.mean(np.concatenate([dd[vid == c].to_numpy() for c in rng.choice(clips, len(clips))]))
              for _ in range(4000)]
        changed = byclip[byclip.abs() > 1e-9]
        print(f"{label}: delta {dd.mean():+.4f}  clip-bootstrap 90% [{np.percentile(bs, 5):+.4f}, "
              f"{np.percentile(bs, 95):+.4f}]  clips better {int((changed > 0).sum())}/{len(changed)} changed "
              f"(of {len(byclip)})")
        print("   per clip:", byclip.round(3).to_dict())
        return dd, changed

    dd, changed = report("aabb", "base_hr_v1", "aabb - base_hr_v1 (KILL TEST)")
    ok = dd.mean() >= 0.015 and (changed > 0).sum() > len(changed) / 2
    print("KILL TEST:", "PASS" if ok else "FAIL")
    report("3run_aabb_v2_opus", "3run_v1_v2_opus", "3-run median, aabb replaces v1")
    report("4run_with_aabb", "3run_v1_v2_opus", "4-run median with aabb")
    # mechanism: log-ratio shift by dimension on size rows
    dims = q[size].map(dim_word)
    lr_new = np.log(aabb[size] / gt[size])
    lr_old = np.log(base[size] / gt[size])
    m = pd.DataFrame({"dim": dims, "lr_base": lr_old, "lr_aabb": lr_new, "sc_base": S.base_hr_v1[size],
                      "sc_aabb": S.aabb[size]})
    m["shift"] = m.lr_aabb - m.lr_base
    m["dimg"] = np.where(m.dim.isin(["length", "width"]), "length/width", np.where(m.dim == "height", "height",
                                                                                     "other"))
    print("size rows: mean log(pred/gt) and its shift (aabb - base_hr_v1) by dimension group:")
    print(m.groupby("dimg")[["lr_base", "lr_aabb", "shift", "sc_base", "sc_aabb"]].agg(["mean", "count"])
          .round(3).to_string())
    m["video"] = v.video_id[size]
    m["q"] = q[size].str[:70]
    m["base"], m["new"], m["gt"] = base[size], aabb[size], gt[size]
    pd.set_option("display.width", 250)
    print(m.sort_values(["video", "dimg"])[["video", "q", "gt", "base", "new", "shift", "sc_base", "sc_aabb"]]
          .round(3).to_string(index=False))
    o = ~size
    mo = pd.DataFrame({"video": v.video_id[o], "q": q[o].str[:60], "gt": gt[o], "base": base[o], "new": aabb[o],
                       "sc_base": S.base_hr_v1[o], "sc_aabb": S.aabb[o]})
    print("other rows:")
    print(mo.round(3).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--score", action="store_true")
    a = ap.parse_args()
    sys.path.insert(0, str(Path(__file__).parent))
    if not a.score:
        run(a.dry)
    if not a.dry:
        score()
