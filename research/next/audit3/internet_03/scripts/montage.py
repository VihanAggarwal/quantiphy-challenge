import cv2, sys, numpy as np
path, out, frames, w = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(',')], int(sys.argv[4])
c = cv2.VideoCapture(path)
imgs = []
for f in frames:
    c.set(cv2.CAP_PROP_POS_FRAMES, f)
    ok, im = c.read()
    if not ok: print('fail', f); continue
    h = int(im.shape[0] * w / im.shape[1])
    im = cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA)
    cv2.putText(im, str(f), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
    imgs.append(im)
cols = int(sys.argv[5]) if len(sys.argv) > 5 else 3
rows = []
for i in range(0, len(imgs), cols):
    r = imgs[i:i+cols]
    while len(r) < cols: r.append(np.zeros_like(imgs[0]))
    rows.append(np.hstack(r))
cv2.imwrite(out, np.vstack(rows))
