import cv2, sys, numpy as np
# usage: v frame x0,y0,x1,y1 out [scale] [gridstep]
v,f=sys.argv[1],int(sys.argv[2]); x0,y0,x1,y1=map(int,sys.argv[3].split(',')); out=sys.argv[4]
sc=float(sys.argv[5]) if len(sys.argv)>5 else 1.0; gs=int(sys.argv[6]) if len(sys.argv)>6 else 50
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/'+v+'.mp4'); c.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=c.read()
im=im[y0:y1,x0:x1].copy()
im=cv2.resize(im,None,fx=sc,fy=sc,interpolation=cv2.INTER_CUBIC if sc>1 else cv2.INTER_AREA)
for gx in range((x0//gs+1)*gs, x1, gs):
    X=int((gx-x0)*sc); cv2.line(im,(X,0),(X,8),(0,0,255),1); cv2.line(im,(X,im.shape[0]-8),(X,im.shape[0]),(0,0,255),1)
    if (gx//gs)%2==0: cv2.putText(im,str(gx),(X+2,20),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
for gy in range((y0//gs+1)*gs, y1, gs):
    Y=int((gy-y0)*sc); cv2.line(im,(0,Y),(8,Y),(0,0,255),1); cv2.line(im,(im.shape[1]-8,Y),(im.shape[1],Y),(0,0,255),1)
    if (gy//gs)%2==0: cv2.putText(im,str(gy),(10,Y+4),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
cv2.imwrite(out,im)
