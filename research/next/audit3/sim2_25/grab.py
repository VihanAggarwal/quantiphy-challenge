import cv2,sys,numpy as np
# usage: grab.py video frame out.png [scale] [x0 y0 x1 y1]
v,f,out=sys.argv[1],int(sys.argv[2]),sys.argv[3]
sc=float(sys.argv[4]) if len(sys.argv)>4 else 0.5
c=cv2.VideoCapture(v); c.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=c.read()
if len(sys.argv)>8:
    x0,y0,x1,y1=map(int,sys.argv[5:9]); im=im[y0:y1,x0:x1]
im=cv2.resize(im,None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA if sc<1 else cv2.INTER_NEAREST)
cv2.imwrite(out,im)
