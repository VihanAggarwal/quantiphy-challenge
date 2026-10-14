"""Horizontal FOV of 3D simulation clips from Apple Depth Pro's FOV head (apple/DepthPro), CPU, no API.
Mirrors research/simfov/fov_moge.py and writes the same columns, so research/simfov/fov_check.py, replay.py and
evaluate.py can read the output unchanged.

    /home/user/venv-depth/bin/python -I research/depthpro/fov_depthpro.py --out research/depthpro/out/fov_depthpro.csv \
        [--videos simulation_0008,...] [--fracs 0.5] [--threads 4]

Environment (outside the repo): /home/user/venv-depth (CPU torch, timm), Depth Pro source cloned from
github.com/apple/ml-depth-pro to /home/user/.cache/depthpro/src, weights apple/DepthPro (depth_pro.pt) from Hugging
Face in /home/user/.cache/depthpro/checkpoints. pillow_heif (only used by depth_pro.utils to open HEIF files) is
stubbed. The model runs as in DepthPro.infer: RGB in [-1, 1], bilinear resize to 1536x1536 (non-square frames are
squashed, as upstream does), encoder + decoder + FOV head (the depth head is skipped: the FOV head reads only the
decoder's low-resolution features). Upstream's convention: fov_deg is the HORIZONTAL FOV of the input frame,
f_px = 0.5 W / tan(fov / 2). One row per (video, frame fraction); resumable (rows already in --out are skipped).
"""
from __future__ import annotations

import argparse
import math
import sys
import time
import types
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[2]
VIDEOS = ROOT / "data" / "QuantiPhy"
DP = Path("/home/user/.cache/depthpro")
sys.path.insert(0, str(DP / "src" / "src"))
sys.modules.setdefault("pillow_heif", types.SimpleNamespace(register_heif_opener=lambda: None))


def frame(path: Path, frac: float) -> np.ndarray:
    cap = cv2.VideoCapture(str(path))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, min(n - 1, int(round(frac * (n - 1))))))
    ok, img = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(f"cannot read {path} at {frac}")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def load_model():
    from depth_pro.depth_pro import DEFAULT_MONODEPTH_CONFIG_DICT, create_model_and_transforms
    cfg = DEFAULT_MONODEPTH_CONFIG_DICT
    cfg.checkpoint_uri = str(DP / "checkpoints" / "depth_pro.pt")
    model, _ = create_model_and_transforms(config=cfg, device=torch.device("cpu"), precision=torch.float32)
    return model.eval()


@torch.no_grad()
def fov_deg(model, img: np.ndarray) -> float:
    x = torch.tensor(img, dtype=torch.float32).permute(2, 0, 1)[None] / 255.0
    x = (x - 0.5) / 0.5
    s = model.img_size
    x = torch.nn.functional.interpolate(x, size=(s, s), mode="bilinear", align_corners=False)
    enc = model.encoder(x)
    _, features_0 = model.decoder(enc)
    return float(model.fov.forward(x, features_0).squeeze())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--videos", default="")
    ap.add_argument("--fracs", default="0.5")
    ap.add_argument("--threads", type=int, default=4)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    model = load_model()
    vids = [v for v in a.videos.split(",") if v] or sorted(
        p.stem for p in VIDEOS.glob("simulation_*.mp4") if not p.stem.endswith("_segmented"))
    fracs = [float(x) for x in a.fracs.split(",")]
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        d = pd.read_csv(out)
        done = {(v, round(f, 3)) for v, f in zip(d.video_id, d.frac)}
    for fr in fracs:            # all clips at the first fraction before any clip gets a second frame
        for v in vids:
            if (v, round(fr, 3)) in done:
                continue
            src = VIDEOS / f"{v}.mp4"
            if not src.exists():   # only the segmented twin is in the set (white background: weak estimate)
                src = VIDEOS / f"{v}_segmented.mp4"
            img = frame(src, fr)
            H, W = img.shape[:2]
            t0 = time.time()
            h = fov_deg(model, img)
            f_px = 0.5 * W / math.tan(math.radians(h) / 2)
            row = dict(video_id=v, src=src.stem, frac=fr, W=W, H=H, fx_px=f_px, hfov_deg=h,
                       vfov_deg=math.degrees(2 * math.atan(H / (2 * f_px))), depth_med_m=math.nan,
                       secs=time.time() - t0)
            pd.DataFrame([row]).to_csv(out, mode="a", header=not out.exists(), index=False)
            print(f"{v} {fr:.2f} {W}x{H} hfov {h:.1f} deg  ({row['secs']:.1f}s)", flush=True)


if __name__ == "__main__":
    main()
