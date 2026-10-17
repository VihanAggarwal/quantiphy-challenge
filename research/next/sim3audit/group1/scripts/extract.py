import cv2, sys, os, numpy as np
vid, outdir = sys.argv[1], sys.argv[2]
frames = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else None
os.makedirs(outdir, exist_ok=True)
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
i = 0
while True:
    ok, f = c.read()
    if not ok: break
    if frames is None or i in frames:
        cv2.imwrite(f'{outdir}/{vid}_f{i:03d}.png', f)
    i += 1
print(vid, 'frames', i)
