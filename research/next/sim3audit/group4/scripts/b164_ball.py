# 0164: ball apparent size (blue mask, ellipse fit) per frame; range under the prior (D=0.21) for f=2395 and f needed for depth 9.391
import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0164.mp4')
i=0
while True:
    ok,f=cap.read()
    if not ok: break
    if i in (8,10,12,14,16,20,24):
        hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
        m=((hsv[...,0]>100)&(hsv[...,0]<135)&(hsv[...,1]>90)&(hsv[...,2]>25)).astype(np.uint8)
        m[:500]=0
        m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        k=1+np.argmax(st[1:,4]); mk=(lab==k).astype(np.uint8)
        cs,_=cv2.findContours(mk,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        c=max(cs,key=len)
        (cx,cy),(a,b),ang=cv2.fitEllipse(c)
        x,y,w,h=cv2.boundingRect(c)
        # shadow/contact at bottom may bias; report width (horizontal) mainly
        u=cx-960; v=cy-540
        for fpx in (2395,):
            r=np.hypot(u,v); cth=fpx/np.sqrt(fpx**2+r**2)
            R=0.21*fpx/(min(a,b)*cth)
        print(f'frame {i}: centre ({cx:.1f},{cy:.1f}) ellipse axes {min(a,b):.1f}/{max(a,b):.1f} bbox {w}x{h}  R(f=2395)={R:.2f} m')
    i+=1
