import cv2, sys, os
out='/home/user/quantiphy-challenge/research/next/labaudit/0014/frames'
os.makedirs(out,exist_ok=True)
for s in ['','s','x']:
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/captured_0014{s}.mp4')
    i=0
    while True:
        ok,f=c.read()
        if not ok: break
        cv2.imwrite(f'{out}/r{s or "o"}_{i:02d}.png',f)
        i+=1
    print(s,i)
