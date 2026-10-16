import cv2, sys, os
base='/home/user/quantiphy-challenge/data/QuantiPhy/captured_0030'
out='/home/user/quantiphy-challenge/research/next/labaudit/0030/frames'
for s in ['','s','x']:
    c=cv2.VideoCapture(base+s+'.mp4'); i=0
    while True:
        ok,f=c.read()
        if not ok: break
        cv2.imwrite(f'{out}/{s or "o"}_{i:02d}.png',f); i+=1
    print(s,i)
