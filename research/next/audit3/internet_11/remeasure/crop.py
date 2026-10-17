import cv2, sys
p,fi,x0,y0,x1,y1,out=sys.argv[1],int(sys.argv[2]),*map(int,sys.argv[3:7]),sys.argv[7]
sc=float(sys.argv[8]) if len(sys.argv)>8 else 1.0
c=cv2.VideoCapture(p); c.set(cv2.CAP_PROP_POS_FRAMES,fi); ok,f=c.read()
cr=f[y0:y1,x0:x1]
if sc!=1: cr=cv2.resize(cr,None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST)
# grid every 50px
import numpy as np
for gx in range((x0//50+1)*50,x1,50):
    X=int((gx-x0)*sc); cr[0:10,X]=(0,255,255)
for gy in range((y0//50+1)*50,y1,50):
    Y=int((gy-y0)*sc); cr[Y,0:10]=(0,255,255)
cv2.imwrite(out,cr)
