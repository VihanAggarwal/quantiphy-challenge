import cv2, numpy as np, sys
from common import load
tag=sys.argv[1]; a,b=int(sys.argv[2]),int(sys.argv[3]); x0,y0,x1,y1=map(int,sys.argv[4:8]); out=sys.argv[8]
smin=int(sys.argv[9]) if len(sys.argv)>9 else 110
fr=load(tag); ims=[]
def toymask(f):
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV).astype(int)
    m=(hsv[...,0]>=6)&(hsv[...,0]<=24)&(hsv[...,1]>smin)&(hsv[...,2]<215)&(hsv[...,2]>40)
    return m
for i in range(a,b+1):
    f=fr[i]; m=toymask(f)
    v=f[y0:y1,x0:x1].copy(); mm=m[y0:y1,x0:x1]
    v[mm]=(0.5*v[mm]+0.5*np.array([255,0,255])).astype(np.uint8)
    cv2.putText(v,str(i),(3,18),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2); ims.append(v)
cols=min(len(ims),6)
while len(ims)%cols: ims.append(np.zeros_like(ims[0]))
cv2.imwrite(out,np.vstack([np.hstack(ims[i:i+cols]) for i in range(0,len(ims),cols)]))
