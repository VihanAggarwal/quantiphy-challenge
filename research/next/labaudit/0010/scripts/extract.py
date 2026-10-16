import cv2, os, sys
base='/home/user/quantiphy-challenge/data/QuantiPhy/captured_0010%s.mp4'
out='/home/user/quantiphy-challenge/research/next/labaudit/0010/frames'
for s in ['','s','X']:
    c=cv2.VideoCapture(base%s); i=0
    while True:
        ok,f=c.read()
        if not ok: break
        cv2.imwrite(f'{out}/f{s or "o"}_{i:02d}.png',f); i+=1
    print(s,i)
