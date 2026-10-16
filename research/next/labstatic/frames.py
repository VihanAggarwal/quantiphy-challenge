"""Frame extraction helpers (test inputs / validation videos only; no labels)."""
import sys, os, cv2, numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
OUT = Path('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/frames')

def vpath(vid):
    p = ROOT / 'data/QuantiPhy' / f'{vid}.mp4'
    if p.exists():
        return p
    q = list((ROOT / 'data/QuantiPhy-validation/validation_videos').glob(f'{vid}.mp4'))
    return q[0]

def read_all(vid):
    c = cv2.VideoCapture(str(vpath(vid)))
    fr = []
    while True:
        ok, f = c.read()
        if not ok: break
        fr.append(f)
    return fr

def save(vid, idxs, scale=1.0, grid=True, crop=None, tag=''):
    fr = read_all(vid)
    OUT.mkdir(parents=True, exist_ok=True)
    paths = []
    for i in idxs:
        f = fr[i].copy()
        if crop:
            x0, y0, x1, y1 = crop
            f = f[y0:y1, x0:x1]
            ox, oy = x0, y0
        else:
            ox = oy = 0
        if grid:
            h, w = f.shape[:2]
            step = 50 if not crop else 20
            for x in range(0, w, step):
                gx = x + ox
                if gx % 100 == 0 or crop:
                    cv2.line(f, (x, 0), (x, h), (0, 255, 255) if gx % 100 == 0 else (0, 128, 128), 1)
                    if gx % 100 == 0: cv2.putText(f, str(gx), (x + 2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
            for y in range(0, h, step):
                gy = y + oy
                if gy % 100 == 0 or crop:
                    cv2.line(f, (0, y), (w, y), (0, 255, 255) if gy % 100 == 0 else (0, 128, 128), 1)
                    if gy % 100 == 0: cv2.putText(f, str(gy), (2, y + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        if scale != 1.0:
            f = cv2.resize(f, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        cv2.putText(f, f'{vid} n={i}', (10, f.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        p = OUT / f'{vid}_{i:03d}{tag}.png'
        cv2.imwrite(str(p), f)
        paths.append(str(p))
    return paths

if __name__ == '__main__':
    vid = sys.argv[1]
    idxs = [int(x) for x in sys.argv[2].split(',')]
    scale = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    crop = tuple(int(x) for x in sys.argv[4].split(',')) if len(sys.argv) > 4 else None
    print('\n'.join(save(vid, idxs, scale, crop=crop)))
