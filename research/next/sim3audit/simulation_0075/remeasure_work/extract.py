import cv2, sys, os
vid, frames = sys.argv[1], [int(x) for x in sys.argv[2].split(',')]
cap = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); print(vid, n, cap.get(cv2.CAP_PROP_FPS), cap.get(3), cap.get(4))
i=0
while True:
    ok, f = cap.read()
    if not ok: break
    if i in frames:
        cv2.imwrite(f'fr/{vid}_{i:03d}.png', f)
        h,w = f.shape[:2]
        cv2.imwrite(f'fr/{vid}_{i:03d}_s.png', cv2.resize(f,(w//2,h//2)))
    i+=1
