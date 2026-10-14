"""CPU dry run of RUN_PRESET "ctx" with a MOCK model (no GPU, no API): proves the run cannot crash on the real
validation videos and that every coordinate transform is right.

    .venv/bin/python research/trackb_next/dry_run.py [--mode replay|garbage] [--out DIR] [--videos a,b]

mode "replay" (default): the mock answers each ta request with the cached Track A annotation of the same video
(runs/val_hr_v1_high: spec + tracks + answer, converted from Claude's image pixels to the 0-1000 grid the open model
is asked for) inside "<think>...</think>```json```", and each cx request with that annotation's extent / points of
the role on the nearest annotated frame (mapped into the crop's grid for zoom requests). Passing the run through
run_ctx -> ctx_merge -> run_open_vlm geometry must then reproduce the Claude-track geometry of
research/trackb_next/diagnose.py (QC/CC, ~.72-.73 macro on validation): an end-to-end check of grid -> sent pixels ->
original pixels, frame / time mapping, the cx zoom crop mapping and the merge. THIS IS A TEST OF OUR CODE ONLY:
nothing it produces is a Track B answer (Track B uses open-weight outputs only).
mode "garbage": the mock returns truncated thinking, prose, malformed JSON and None (backend failure) at random;
the run must finish, cache nothing for failed generations, and leave the records loadable.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

from qp.claude_annotate import load_annotations, with_depth_info  # noqa: E402
from qp.data import load_split  # noqa: E402
from qp.mra import item_scores  # noqa: E402
from qp.open import ctx_annot as C  # noqa: E402
from qp.open import ctx_merge, run_ctx  # noqa: E402

CLAUDE = ROOT / "runs" / "val_hr_v1_high" / "val_hires" / "records"
CATS = ("S2", "D2", "S3", "D3")


class ReplayModel:
    """Mock backend: Track A val annotations as if the open model had produced them."""

    def __init__(self):
        self.recs = {p.stem: json.loads(p.read_text()) for p in sorted(CLAUDE.glob("*.json"))}
        val = load_split("val_hires")
        dt = dict(zip(val.qid.astype(int), val.depth_info.fillna("")))
        self.anns = load_annotations({k: with_depth_info(r, dt) for k, r in self.recs.items()})
        self.calls = {"ta": 0, "cx": 0, "zoom": 0}

    def _grid(self, v, meta):
        W, H = meta["image_size"]
        s = float(meta.get("scale", 1.0) or 1.0)
        return [round(x / s / (W if i % 2 == 0 else H) * 1000.0, 2) for i, x in enumerate(v)]

    def ta_reply(self, vid: str) -> str:
        rec = self.recs.get(vid)
        if rec is None:
            return "<think>no idea</think>{}"
        meta = rec["meta"]
        qs = []
        for q in rec["parsed"]["questions"]:
            tracks = []
            for t in q.get("tracks") or []:
                obs = []
                for o in t.get("obs") or []:
                    obs.append({"frame": o.get("frame"),
                                "point": self._grid(o["point"], meta) if o.get("point") else None,
                                "extent": [self._grid(o["extent"][0], meta), self._grid(o["extent"][1], meta)]
                                if o.get("extent") else None,
                                "box": self._grid(o["box"], meta) if o.get("box") else None})
                tracks.append({"role": t.get("role"), "object": t.get("object"), "obs": obs})
            s = q["spec"]
            qs.append({"qid": q["qid"], "target": s["target"], "prior": s["prior"], "tracks": tracks,
                       "answer": q.get("direct_answer"), "confidence": q.get("confidence")})
        return "<think>replaying a cached annotation</think>\n```json\n" + json.dumps({"questions": qs}) + "\n```"

    def cx_reply(self, tag: dict) -> str:
        ann = self.anns.get(int(tag["qid"]))
        if ann is None:
            return "[]"
        fps = float(self.recs[tag["video_id"]]["meta"]["fps"])
        t0 = tag["frame"] / fps
        want = ("target", "target2") if tag["role"] == "distance" else (tag["role"],)
        pts = []
        for role in want:
            tr = next((t for t in ann.tracks if t.role == role and t.obs), None)
            if tr is None:
                return "[]"
            if tag["role"] == "distance":
                o = min((o for o in tr.obs if o.point or o.box), key=lambda o: abs(o.t - t0), default=None)
                if o is None:
                    return "[]"
                pts.append(o.point or [(o.box[0] + o.box[2]) / 2, (o.box[1] + o.box[3]) / 2])
            else:
                o = min((o for o in tr.obs if o.extent), key=lambda o: abs(o.t - t0), default=None)
                if o is None:
                    return "[]"
                pts += [o.extent[0], o.extent[1]]
        x0, y0, x1, y1 = tag["box"]
        g = [[(p[0] - x0) / (x1 - x0) * 1000.0, (p[1] - y0) / (y1 - y0) * 1000.0] for p in pts]
        return json.dumps([{"point_2d": [round(v, 2) for v in g[0]], "label": "end 1"},
                           {"point_2d": [round(v, 2) for v in g[1]], "label": "end 2"}])

    def generate(self, reqs):
        out = []
        for r in reqs:
            if r.messages and r.messages[0].get("role") == "system" and r.messages[0]["content"] == C.TA_SYSTEM:
                self.calls["ta"] += 1
                text = r.messages[1]["content"][0]["text"]
                out.append(self.ta_reply(re.match(r"Video (\S+?):", text).group(1)))
            else:
                self.calls["zoom" if (r.tag or {}).get("zoom") else "cx"] += 1
                out.append(self.cx_reply(r.tag))
        return out


class GarbageModel:
    def __init__(self, seed=0):
        self.rng = random.Random(seed)
        self.calls = 0

    def generate(self, reqs):
        self.calls += len(reqs)
        choices = [None, "", "<think>I need to think about this for a long time and then", "Sure! The answer is 5.",
                   '```json\n{"questions": [{"qid": "x", "tracks": 7}]}', '{"questions": [{"qid": 1, "target": 3}]}',
                   '[{"point_2d": [10, 20]}]', '[{"point_2d": [10, 20]}, {"point_2d": [1e9, -5]}]', "[]",
                   '{"questions": []}']
        return [self.rng.choice(choices) for _ in reqs]


def score(csv: Path, val: pd.DataFrame) -> dict:
    d = pd.read_csv(csv).set_index("id").parsed_value.reindex(val.qid).to_numpy(float)
    it = np.nan_to_num(np.asarray(item_scores(d, val.answer.to_numpy(float)), float))
    per = {c: float(it[(val.category == c).to_numpy()].mean()) for c in CATS}
    return {"MRA": float(np.mean(list(per.values()))), **per}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="replay", choices=["replay", "garbage"])
    ap.add_argument("--out", default="/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ctx_dry")
    ap.add_argument("--videos", default="")
    ap.add_argument("--caw", default="/tmp/claude-0/tb3/x/trackb_v1/val/caw/caw.csv")
    ap.add_argument("--cvq", default="/tmp/claude-0/tb3/x/trackb_v1/val/cvq/annotate")
    a = ap.parse_args(argv)
    out = Path(a.out) / a.mode
    shutil.rmtree(out, ignore_errors=True)
    model = ReplayModel() if a.mode == "replay" else GarbageModel()
    vids = ["--videos", a.videos] if a.videos else []
    rc = run_ctx.main(["--split", "val_hires", "--out", str(out), "--task", "ta,cx", "--ta-chunk", "6", "--cx-chunk", "4"] + vids,
                      backend=model)
    print("run_ctx exit", rc, "calls", model.calls)
    if a.mode == "garbage":   # a second pass must pick up exactly the uncached videos and still not crash
        rc2 = run_ctx.main(["--split", "val_hires", "--out", str(out), "--task", "ta,cx", "--ta-chunk", "6", "--cx-chunk", "4"] + vids,
                           backend=model)
        print("second pass exit", rc2)
    ctx_merge.main(["--split", "val_hires", "--root", str(out), "--direct-from", a.caw, "--cvq", a.cvq])
    val = load_split("val_hires")
    if a.videos:
        val = val[val.video_id.isin(a.videos.split(","))]
    rows = {}
    for name in ("ta", "tacx", "cvqcx"):
        p = out / name / "geometry.csv"
        if p.exists():
            rows[name] = score(p, val)
    if (out / "ta" / "direct.csv").exists():
        rows["ta_direct"] = score(out / "ta" / "direct.csv", val)
    print(pd.DataFrame(rows).T.round(3).to_string())
    return rows




def sam_dry_run(out_root: str, videos: str, caw: str) -> None:
    """The SAM 2 stage of the preset on the replay output with the test-suite fakes (colour-threshold 'SAM 2'):
    run_cv.py --qwen-boxes <ta/annotate> must read the ta records, then run_open_vlm geometry and ctx_merge samcx."""
    import importlib.util
    sys.path.insert(0, str(ROOT / "tests"))
    from qp.open import cv_track as cv
    from test_cv_track import FakeDetector, FakeSegmenter
    out = Path(out_root) / "replay"
    spec = importlib.util.spec_from_file_location("run_cv", ROOT / "scripts" / "run_cv.py")
    run_cv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_cv)
    argv = ["--split", "val_hires", "--specs", str(out / "ta" / "specs"), "--qwen-boxes", str(out / "ta" / "annotate"),
            "--out", str(out / "tasam" / "annotate"), "--solve", "--videos", videos, "--max-frames", "60"]
    run_cv.main(argv, tracker=cv.CVTracker(FakeDetector(), FakeSegmenter(), prompt="qwen", max_frames=60))
    rov = ctx_merge._rov()
    rov.main(["--split", "val_hires", "--task", "geometry", "--name", "dry", "--out", str(out / "tasam"),
              "--specs-from", str(out / "ta" / "specs"), "--direct-from", caw, "--videos", videos])
    ctx_merge.main(["--split", "val_hires", "--root", str(out), "--direct-from", caw, "--variants", "samcx"])
    rec = json.loads(next((out / "samcx" / "annotate").glob("*.json")).read_text())
    srcs = {t["source"] for ts in rec["tracks"].values() for t in ts}
    print("samcx track sources:", srcs)


if __name__ == "__main__":
    if "--sam" in sys.argv:
        sys.argv.remove("--sam")
        sam_dry_run("/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ctx_dry",
                    "simulation_0089,internet_0019", "/tmp/claude-0/tb3/x/trackb_v1/val/caw/caw.csv")
    else:
        main()
