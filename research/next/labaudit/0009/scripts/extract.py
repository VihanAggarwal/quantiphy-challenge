import cv2, os, sys
base='/home/user/quantiphy-challenge/research/next/labaudit/0009/frames'
for s in ['','s','x']:
    c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0009%s.mp4'%s)
    i=0
    while True:
        ok,f=c.read()
        if not ok: break
        cv2.imwrite(os.path.join(base,'r%s_f%02d.png'%(s or 'o',i)),f)
        i+=1
    print(s,i)
