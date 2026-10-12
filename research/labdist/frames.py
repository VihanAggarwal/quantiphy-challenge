"""Contact sheet of chosen frames of a test clip (label-free visual check)."""
import sys
import cv2
import numpy as np

def sheet(video, frames, out, width=640, annotate=True):
    c = cv2.VideoCapture(video)
    imgs = []
    for f in frames:
        c.set(cv2.CAP_PROP_POS_FRAMES, f)
        ok, im = c.read()
        if not ok:
            continue
        h, w = im.shape[:2]
        im = cv2.resize(im, (width, int(h * width / w)))
        if annotate:
            cv2.putText(im, f"f{f} t={f/24:.2f}", (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        imgs.append(im)
    rows = [np.hstack(imgs[i:i + 2]) if len(imgs[i:i + 2]) == 2 else np.hstack([imgs[i], np.zeros_like(imgs[i])]) for i in range(0, len(imgs), 2)]
    cv2.imwrite(out, np.vstack(rows))

if __name__ == "__main__":
    sheet(sys.argv[1], [int(x) for x in sys.argv[2].split(",")], sys.argv[3])
