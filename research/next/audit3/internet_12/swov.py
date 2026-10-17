import cv2, numpy as np
p='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0037.mp4'
cap=cv2.VideoCapture(p); tiles=[]
R=np.loadtxt('sw_track.txt')
for f,x0 in [(0,700),(50,1150),(125,1700)]:
    cap.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=cap.read()
    c=im[700:1250,x0:x0+1000].copy()
    roi=c.astype(np.int16); v=roi.max(2)
    hair=(v<70)&(roi[...,2]>=roi[...,1]-5)
    skin=(roi[...,2]>roi[...,1]+15)&(roi[...,2]>roi[...,0]+25)&(roi[...,2]>110)
    o=c.copy(); o[hair]=(0,0,255); o[skin]=(0,255,0)
    c=np.hstack([c,o]); c=cv2.resize(c,None,fx=0.45,fy=0.45,interpolation=cv2.INTER_AREA)
    for k,(cx,cy) in enumerate([(R[f,3],R[f,4]),(R[f,6],R[f,7])]):
        X=int((cx-x0)*0.45); Y=int((cy-700)*0.45)
        cv2.circle(c,(X,Y),6,(255,0,255) if k==0 else (255,255,0),2)
    for gx in range((x0//100+1)*100,x0+1000,100):
        X=int((gx-x0)*0.45); cv2.line(c,(X,0),(X,15),(0,255,255),1); cv2.putText(c,str(gx),(X+2,12),0,0.35,(0,255,255),1)
    cv2.putText(c,'f%d'%f,(5,c.shape[0]-6),0,0.6,(0,0,255),2)
    tiles.append(c)
cv2.imwrite('swov.png',np.vstack(tiles))
