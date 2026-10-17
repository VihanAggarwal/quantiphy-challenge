import cv2, numpy as np
p='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0039.mp4'
cap=cv2.VideoCapture(p); i=0
while True:
    ok,im=cap.read()
    if not ok: break
    if i in (0,25,50,71):
        hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV).astype(np.int16)
        h,s,v=hsv[...,0],hsv[...,1],hsv[...,2]
        red=((h<10)|(h>170))&(s>90)&(v>60)
        res=[]
        for y0 in (500,1500,2500,3300):
            band=red[y0:y0+300]
            xs=np.nonzero(band)[1]
            L=xs[xs<1080]; R=xs[xs>=1080]
            res.append((y0+150,np.median(L) if len(L) else np.nan,np.median(R) if len(R) else np.nan))
        print(i,' '.join('y%d: %.0f-%.0f sep %.0f'%(y,a,b,b-a) for y,a,b in res))
    i+=1
