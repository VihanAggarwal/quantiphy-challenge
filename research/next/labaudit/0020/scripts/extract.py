import cv2, os
base='/home/user/quantiphy-challenge/data/QuantiPhy/'
out='/home/user/quantiphy-challenge/research/next/labaudit/0020/frames/'
for v in ['captured_0020','captured_0020s','captured_0020x']:
    c=cv2.VideoCapture(base+v+'.mp4'); i=0
    while True:
        ok,f=c.read()
        if not ok: break
        cv2.imwrite(out+f'{v[9:]}_f{i:02d}.png',f); i+=1
    print(v,i)
