import cv2, sys, os
vid, frames, out = sys.argv[1], [int(x) for x in sys.argv[2].split(',')], sys.argv[3]
cap = cv2.VideoCapture(vid)
n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); print(vid, n, cap.get(cv2.CAP_PROP_FPS), cap.get(3), cap.get(4))
i = 0
while True:
    ok, f = cap.read()
    if not ok: break
    if i in frames:
        cv2.imwrite(os.path.join(out, f"{os.path.basename(vid)[:-4]}_f{i:03d}.png"), f)
    i += 1
