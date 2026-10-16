import cv2, os, sys
base='/home/user/quantiphy-challenge/data/QuantiPhy/'
out='/home/user/quantiphy-challenge/research/next/labaudit/0053/frames'
for s in ['','s','x']:
    c=cv2.VideoCapture(base+f'captured_0053{s}.mp4')
    n=0
    while True:
        ok,f=c.read()
        if not ok: break
        cv2.imwrite(f'{out}/{s or "o"}_{n:02d}.png',f); n+=1
    print(s,n)
