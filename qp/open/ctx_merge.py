"""CPU step of RUN_PRESET "ctx": hybrid track records from the ctx outputs, then the geometry step on each.

    python -m qp.open.ctx_merge --split val_hires --root outputs/trackb_ctx/val \\
        [--cvq outputs/trackb_v1/val/cvq/annotate] [--direct-from outputs/trackb_v1/val/caw/caw.csv]

Variants (each <root>/<name>/annotate/<vid>.json + <root>/<name>/geometry.csv; specs = <root>/ta/specs, else the
rule spec; geometry with run_open_vlm.run_geometry, i.e. the CaW / direct fallback where geometry fails):
  ta     the ta tracks as the model gave them (geometry written to <root>/ta/geometry.csv)
  tacx   ta tracks; size roles take the cx extents, two-object distances the cx points (where cx has them)
  samcx  motion roles from the SAM 2 tracks prompted by the ta boxes (<root>/tasam/annotate), else ta;
         sizes / distances from cx, else ta, else SAM 2 boxes
  cvqcx  as samcx with the trackb_v1 SAM 2 tracks prompted by Qwen3-VL boxes (--cvq) for motion
A variant whose motion source is missing is skipped. Nothing here looks at labels (run_geometry prints validation
scores when the split has answers).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qp.open.ctx_annot import SIZE_KINDS, cx_tracks  # noqa: E402
from qp.open.qwen_vl import rule_spec  # noqa: E402
from qp.spec import Obs, QuestionSpec, RoleTrack  # noqa: E402

MOTION_KINDS = ("speed", "acceleration", "displacement", "path_length")
VARIANTS = ("ta", "tacx", "samcx", "cvqcx")


def _rov():
    spec = importlib.util.spec_from_file_location("run_open_vlm", ROOT / "scripts" / "run_open_vlm.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_dir(d: Path | None) -> dict[str, dict]:
    out = {}
    if d is None or not Path(d).exists():
        return out
    for p in sorted(Path(d).glob("*.json")):
        try:
            rec = json.loads(p.read_text())
        except ValueError:
            continue
        if isinstance(rec, dict) and rec.get("video_id") and not rec.get("error"):
            out[str(rec["video_id"])] = rec
    return out


def _scale_obs(o: Obs, sx: float, sy: float) -> Obs:
    xy = lambda p: [p[0] * sx, p[1] * sy]  # noqa: E731
    return Obs(t=o.t, point=xy(o.point) if o.point else None,
               extent=[xy(o.extent[0]), xy(o.extent[1])] if o.extent else None,
               box=[o.box[0] * sx, o.box[1] * sy, o.box[2] * sx, o.box[3] * sy] if o.box else None, score=o.score)


def _tracks(rec: dict | None, qid: int, size: tuple[float, float] | None = None) -> dict[str, RoleTrack]:
    """Role -> RoleTrack of one question; rescaled to `size` (W, H) when the record's meta image_size differs
    (e.g. a 480p validation record merged into full-resolution ta tracks)."""
    out = {}
    src = ((rec or {}).get("meta") or {}).get("image_size")
    sx = sy = 1.0
    if size and src and len(src) == 2 and float(src[0]) > 0 and float(src[1]) > 0:
        sx, sy = float(size[0]) / float(src[0]), float(size[1]) / float(src[1])
    for t in ((rec or {}).get("tracks") or {}).get(str(qid), []) or []:
        try:
            tr = RoleTrack.from_dict(t)
        except (KeyError, TypeError):
            continue
        if abs(sx - 1) > 1e-9 or abs(sy - 1) > 1e-9:
            tr = RoleTrack(role=tr.role, object=tr.object, obs=[_scale_obs(o, sx, sy) for o in tr.obs],
                           source=tr.source, depth_name=tr.depth_name, range_m=tr.range_m)
        if tr.obs and (tr.role not in out or len(tr.obs) > len(out[tr.role].obs)):
            out[tr.role] = tr
    return out


def _has(tr: RoleTrack | None, what: str) -> bool:
    if tr is None:
        return False
    if what == "extent":
        return any(o.extent for o in tr.obs)
    if what == "motion":
        return sum(1 for o in tr.obs if o.point or o.box) >= 3
    return any(o.point or o.box or o.extent for o in tr.obs)


def _named(tr: RoleTrack, role: str, name: str, source: str) -> RoleTrack:
    return RoleTrack(role=role, object=name or tr.object, obs=tr.obs, source=source or tr.source,
                     depth_name=tr.depth_name, range_m=tr.range_m)


def _name(spec: QuestionSpec, role: str) -> str:
    q = spec.prior if role.startswith("prior") else spec.target
    i = 1 if role.endswith("2") else 0
    return str(q.objects[i]) if len(q.objects) > i else ""


def merge_question(spec: QuestionSpec, base: dict[str, RoleTrack], motion: list[dict[str, RoleTrack]],
                   cx: dict[str, list[Obs]], use_cx: bool = True) -> list[RoleTrack]:
    """Tracks for one question. base: the ta tracks by role; motion: further track sources by role in priority
    order (SAM 2 first); cx: {role: [Obs]} from the cx stage."""
    out = []
    for role, q in (("prior", spec.prior), ("prior2", spec.prior), ("target", spec.target), ("target2", spec.target)):
        if role.endswith("2") and not (q.kind == "distance" and len(q.objects) >= 2):
            continue
        name = _name(spec, role)
        srcs = motion + [base]
        if q.kind in SIZE_KINDS:
            if use_cx and cx.get(role):
                out.append(RoleTrack(role=role, object=name, obs=cx[role], source="ctx-cx"))
                continue
            tr = base.get(role) if _has(base.get(role), "extent") else next(
                (s[role] for s in srcs if _has(s.get(role), "any")), None)
        elif q.kind == "distance":
            if use_cx and cx.get("target") and cx.get("target2") and role in ("target", "target2"):
                out.append(RoleTrack(role=role, object=name, obs=cx[role], source="ctx-cx"))
                continue
            tr = next((s[role] for s in srcs if _has(s.get(role), "any")), None)
        elif q.kind == "camera_distance":
            tr = base.get(role)
        else:   # motion
            tr = next((s[role] for s in srcs if _has(s.get(role), "motion")), None) or base.get(role)
        if tr is not None:
            out.append(_named(tr, role, name, tr.source))
    return out


def build_variant(df, specs: dict[int, QuestionSpec], ta: dict, motion: list[dict], cx: dict, use_cx: bool,
                  out_dir: Path, save_json, safe_id=lambda v: str(v)) -> int:
    """Writes <out_dir>/annotate/<vid>.json and <out_dir>/specs/<vid>.json (the specs used: ta's, else the rule
    spec); returns the number of videos written."""
    n = 0
    for vid, g in df.groupby("video_id", sort=False):
        trec = ta.get(vid)
        meta_src = trec or next((m[vid] for m in motion if vid in m), None)
        if meta_src is None:
            continue
        meta = dict(meta_src.get("meta") or {})
        fps = float(meta.get("fps") or 0.0)
        size = meta.get("image_size")
        if not fps > 0 or not size:
            continue
        cxr = cx.get(vid)
        csz = ((cxr or {}).get("meta") or {}).get("image_size")
        if cxr and csz and [int(v) for v in csz] != [int(v) for v in size]:
            print(f"  {vid}: cx image size {csz} != track image size {size}; cx rescaled")
        tracks, used = {}, {}
        for r in g.itertuples():
            q = int(r.qid)
            spec = specs.get(q) or rule_spec(r)
            used[str(q)] = {"spec": spec.to_dict(), "flags": [] if q in specs else ["rule_fallback"]}
            mot = [_tracks(m.get(vid), q, size) for m in motion]
            cxo = cx_tracks(cxr, q, fps) if use_cx else {}
            if cxo and csz and [int(v) for v in csz] != [int(v) for v in size]:
                sx, sy = float(size[0]) / float(csz[0]), float(size[1]) / float(csz[1])
                cxo = {r: [_scale_obs(o, sx, sy) for o in obs] for r, obs in cxo.items()}
            tr = merge_question(spec, _tracks(trec, q, size), mot, cxo, use_cx)
            tracks[str(q)] = [t.to_dict() for t in tr]
        save_json(out_dir / "annotate" / f"{safe_id(vid)}.json",
                  {"video_id": vid, "meta": meta, "objects": {}, "tracks": tracks})
        save_json(out_dir / "specs" / f"{safe_id(vid)}.json", {"video_id": vid, "model": "ctx_merge", "questions": used})
        n += 1
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", required=True, choices=["val", "val_hires", "test"])
    ap.add_argument("--root", required=True, help="outputs/<run>/<split folder> holding ta/, cx/, tasam/")
    ap.add_argument("--cvq", help="trackb_v1 cvq/annotate folder of the same split (Qwen-box SAM 2 tracks)")
    ap.add_argument("--direct-from", help="fallback answers (CaW csv); default <root>/ta/direct.csv")
    ap.add_argument("--variants", default=",".join(VARIANTS))
    ap.add_argument("--max-disagree", type=float, default=10.0)
    a = ap.parse_args(argv)
    rov = _rov()
    from qp.data import load_split
    df = load_split(a.split)
    eval_df = df
    df = df.drop(columns=["answer"], errors="ignore")
    root = Path(a.root)
    specs_dir = root / "ta" / "specs"
    specs = rov.specs_from(specs_dir) if specs_dir.exists() else {}
    ta, cx = load_dir(root / "ta" / "annotate"), load_dir(root / "cx")
    sam, cvq = load_dir(root / "tasam" / "annotate"), load_dir(Path(a.cvq) if a.cvq else None)
    direct = a.direct_from if a.direct_from and Path(a.direct_from).exists() else (
        str(root / "ta" / "direct.csv") if (root / "ta" / "direct.csv").exists() else None)
    print(f"ctx_merge {a.split}: specs {len(specs)}, ta {len(ta)}, cx {len(cx)}, tasam {len(sam)}, cvq {len(cvq)} "
          f"videos; fallback {direct}")
    plan = {"ta": ([], False), "tacx": ([], True), "samcx": ([sam], True), "cvqcx": ([cvq], True)}
    for name in [v for v in a.variants.split(",") if v]:
        motion, use_cx = plan[name]
        if name != "ta" and not cx:
            print(f"  {name}: skipped (no cx records)")
            continue
        if any(not m for m in motion):
            print(f"  {name}: skipped (motion source missing)")
            continue
        if not ta and name in ("ta", "tacx"):
            print(f"  {name}: skipped (no ta records)")
            continue
        out = root / name
        if name != "ta":
            n = build_variant(df, specs, ta, motion, cx, use_cx, out, rov.save_json, rov.safe_id)
            print(f"  {name}: {n} videos written")
        res = rov.run_geometry(df, out, direct, None, a.max_disagree)
        rov.report(eval_df, res, ("parsed_value", "geo_value", "direct_value"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
