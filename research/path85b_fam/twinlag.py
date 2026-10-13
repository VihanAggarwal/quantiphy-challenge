"""Frame alignment between an original simulation clip and its segmented twin when only one of them starts with a
duplicated first frame: for original frame k, which twin frame j matches best on the twin's foreground?
Test input videos only."""
import sys
from pathlib import Path
import cv2, numpy as np
ROOT = Path(__file__).resolve().parents[2]

def frames(v, n=14, w=480):
    cap = cv2.VideoCapture(str(ROOT / "data/QuantiPhy" / f"{v}.mp4")); out = []
    while len(out) < n:
        ok, f = cap.read()
        if not ok: break
        h = int(f.shape[0] * w / f.shape[1]); out.append(cv2.resize(f, (w, h)).astype(np.float32))
    tot = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); return out, tot

for a in sys.argv[1:]:
    O, no = frames(a); S, ns = frames(a + "_segmented")
    print(a, "frames orig", no, "seg", ns)
    for k in range(0, 5):
        sc = {}
        for j in range(max(0, k - 2), min(len(S), k + 3)):
            m = S[j].min(axis=2) < 235
            if m.sum() < 50: continue
            sc[j] = float(np.abs(O[k][m] - S[j][m]).mean())
        best = min(sc, key=sc.get)
        print(f"  orig {k}: best twin {best}  " + " ".join(f"{j}:{s:.1f}" for j, s in sc.items()))
