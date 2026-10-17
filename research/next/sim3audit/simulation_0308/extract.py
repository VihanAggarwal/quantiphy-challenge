import cv2, numpy as np, sys
for c in ['0304','0306','0308']:
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{c}.mp4')
    i=0
    while True:
        ok,f=cap.read()
        if not ok: break
        if i in (0,24,48,71):
            cv2.imwrite(f'frames/{c}_{i:02d}.png', cv2.resize(f,(1280,720)))
        i+=1
