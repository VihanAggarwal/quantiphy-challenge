import cv2, numpy as np, sys
# usage: crop.py tag frames x0 y0 x1 y1 scale out
tag=sys.argv[1]; frs=[int(a) for a in sys.argv[2].split(',')]
x0,y0,x1,y1=map(int,sys.argv[3:7]); sc=float(sys.argv[7]); out=sys.argv[8]
D='/home/user/quantiphy-challenge/research/next/labaudit/0024/'
ims=[]
for f in frs:
    im=cv2.imread(D+f'frames/{tag}{f:02d}.png')[y0:y1,x0:x1]
    im=cv2.resize(im,None,fx=sc,fy=sc,interpolation=cv2.INTER_CUBIC)
    cv2.putText(im,f'{tag}{f}',(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,255),2)
    # grid ticks every 20px original
    for gx in range((x0//20+1)*20,x1,20):
        X=int((gx-x0)*sc); cv2.line(im,(X,0),(X,8 if gx%100 else 20),(0,0,255),1)
        if gx%100==0: cv2.putText(im,str(gx),(X+2,40),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),1)
    for gy in range((y0//20+1)*20,y1,20):
        Y=int((gy-y0)*sc); cv2.line(im,(0,Y),(8 if gy%100 else 20,Y),(0,0,255),1)
        if gy%100==0: cv2.putText(im,str(gy),(22,Y+5),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),1)
    ims.append(im)
cv2.imwrite(D+out,np.vstack(ims) if len(ims)>1 else ims[0])
