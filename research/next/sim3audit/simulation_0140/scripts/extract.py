import cv2, sys, os
v, out = sys.argv[1], sys.argv[2]
idx = [int(x) for x in sys.argv[3].split(',')]
c = cv2.VideoCapture(v)
n = int(c.get(7))
os.makedirs(out, exist_ok=True)
for i in range(n):
    ok, f = c.read()
    if not ok: break
    if i in idx:
        cv2.imwrite(f'{out}/f{i:03d}.png', f)
