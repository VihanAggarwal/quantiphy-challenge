import cv2, sys
p, outpref = sys.argv[1], sys.argv[2]
idxs = [int(x) for x in sys.argv[3].split(',')]
scale = float(sys.argv[4]) if len(sys.argv)>4 else 0.5
cap = cv2.VideoCapture(p)
n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); print('frames',n, cap.get(cv2.CAP_PROP_FPS), cap.get(3), cap.get(4))
i=0
while True:
    ok, f = cap.read()
    if not ok: break
    if i in idxs:
        s = cv2.resize(f, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        cv2.imwrite(f'{outpref}_{i:03d}.png', s)
    i+=1
