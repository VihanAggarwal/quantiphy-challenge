"""Horizontal FOV of 3D simulation clips from MoGe-2 (Ruicheng/moge-2-vitl-normal), CPU, no API.

    HF_HOME=/home/user/.cache/hf \
        /home/user/venv-depth/bin/python -I research/simfov/fov_moge.py --out research/simfov/out/fov_moge.csv \
        [--videos simulation_0008,...] [--fracs 0.5] [--tokens 1800]

Environment (outside the repo): /home/user/venv-depth (CPU torch), MoGe-2 code from the HF Space Ruicheng/MoGe-2
(moge/), utils3d vendored from the HF Space Ruicheng/MoGe (both copied to /home/user/moge-lib).
One row per (video, frame fraction): hfov_deg = 2 atan(W / (2 fx)), fx from MoGe's focal recovery (principal
point at the centre). Resumable: rows already in --out are skipped.
"""
from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, "/home/user/moge-lib")   # MoGe-2 code + vendored utils3d (see docstring)
VIDEOS = ROOT / "data" / "QuantiPhy"


def frame(path: Path, frac: float) -> np.ndarray:
    cap = cv2.VideoCapture(str(path))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, min(n - 1, int(round(frac * (n - 1))))))
    ok, img = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(f"cannot read {path} at {frac}")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--videos", default="")
    ap.add_argument("--fracs", default="0.5")
    ap.add_argument("--tokens", type=int, default=1800)
    ap.add_argument("--threads", type=int, default=4)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    from moge.model.v2 import MoGeModel
    model = MoGeModel.from_pretrained("Ruicheng/moge-2-vitl-normal").eval()
    vids = [v for v in a.videos.split(",") if v] or sorted(
        p.stem for p in VIDEOS.glob("simulation_*.mp4") if not p.stem.endswith("_segmented"))
    fracs = [float(x) for x in a.fracs.split(",")]
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        d = pd.read_csv(out)
        done = {(v, round(f, 3)) for v, f in zip(d.video_id, d.frac)}
    for v in vids:
        for fr in fracs:
            if (v, round(fr, 3)) in done:
                continue
            src = VIDEOS / f"{v}.mp4"
            if not src.exists():   # only the segmented twin is in the set (white background: weak estimate)
                src = VIDEOS / f"{v}_segmented.mp4"
            img = frame(src, fr)
            H, W = img.shape[:2]
            t0 = time.time()
            x = torch.tensor(img / 255.0, dtype=torch.float32).permute(2, 0, 1)
            o = model.infer(x, num_tokens=a.tokens, force_projection=False, apply_mask=False, use_fp16=False)
            K = o["intrinsics"].cpu().numpy()          # normalised: fx in units of image width
            fx_n, fy_n = float(K[0, 0]), float(K[1, 1])
            hfov = math.degrees(2 * math.atan(0.5 / fx_n))
            depth = o["depth"].cpu().numpy()
            row = dict(video_id=v, src=src.stem, frac=fr, W=W, H=H, fx_px=fx_n * W, hfov_deg=hfov,
                       vfov_deg=math.degrees(2 * math.atan(0.5 / fy_n)),
                       depth_med_m=float(np.nanmedian(depth[np.isfinite(depth)])), secs=time.time() - t0)
            pd.DataFrame([row]).to_csv(out, mode="a", header=not out.exists(), index=False)
            print(f"{v} {fr:.2f} {W}x{H} hfov {hfov:.1f} deg  ({row['secs']:.1f}s)", flush=True)


if __name__ == "__main__":
    main()
