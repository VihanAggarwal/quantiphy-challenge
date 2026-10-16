import cv2, sys, os
base='/home/user/quantiphy-challenge/data/QuantiPhy/'
for suf in ['','s','x']:
    cap=cv2.VideoCapture(base+f'captured_0023{suf}.mp4')
    print(suf, cap.get(cv2.CAP_PROP_FPS), cap.get(cv2.CAP_PROP_FRAME_COUNT), cap.get(3), cap.get(4))
    i=0
    while True:
        ok,fr=cap.read()
        if not ok: break
        cv2.imwrite(f'frames/{suf or "o"}{i:02d}.png',fr); i+=1
    print('frames',i)
