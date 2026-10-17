import cv2,sys
# usage: fr.py video frame out [x0 y0 x1 y1] [scale]
v=sys.argv[1]; f=int(sys.argv[2]); out=sys.argv[3]
c=cv2.VideoCapture(v); c.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=c.read()
if len(sys.argv)>=8:
    x0,y0,x1,y1=map(int,sys.argv[4:8]); im=im[y0:y1,x0:x1]
s=float(sys.argv[8]) if len(sys.argv)>8 else 1.0
if s!=1.0: im=cv2.resize(im,None,fx=s,fy=s,interpolation=cv2.INTER_AREA if s<1 else cv2.INTER_CUBIC)
cv2.imwrite(out,im); print(im.shape)
