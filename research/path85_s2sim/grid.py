import sys, cv2, numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
for vid in sys.argv[1:]:
    cap = cv2.VideoCapture(str(ROOT / "data/QuantiPhy" / f"{vid}.mp4")); n = int(cap.get(7)); w = cap.get(3); h = cap.get(4); fps = cap.get(5)
    idx = np.linspace(0, n - 1, 8).round().astype(int)
    imgs = []
    for i in idx:
        cap.set(1, int(i)); ok, img = cap.read(); img = cv2.resize(img, (480, int(480 * h / w)))
        cv2.putText(img, f"f{i} t{i/24:.2f}", (5, 20), 0, 0.6, (0, 0, 255), 2); imgs.append(img)
    cv2.imwrite(str(Path(__file__).parent / f"frames/{vid}_grid.jpg"), np.vstack([np.hstack(imgs[k:k + 4]) for k in (0, 4)]))
    print(vid, n, w, h, fps)
