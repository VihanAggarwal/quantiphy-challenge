import cv2, numpy as np, sys
from common import load
# usage: zoom.py tag frames(comma) x0 y0 x1 y1 scale out
tag=sys.argv[1]; frs=[int(s) for s in sys.argv[2].split(',')]; x0,y0,x1,y1=map(int,sys.argv[3:7]); sc=int(sys.argv[7]); out=sys.argv[8]
fr=load(tag); ims=[]
for i in frs:
    v=cv2.resize(fr[i][y0:y1,x0:x1],None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST)
    for gx in range((x0//20+1)*20,x1,20):
        c=(0,200,0) if gx%100 else (0,0,255)
        cv2.line(v,((gx-x0)*sc,0),((gx-x0)*sc,v.shape[0]),c,1)
    for gy in range((y0//20+1)*20,y1,20):
        c=(0,200,0) if gy%100 else (0,0,255)
        cv2.line(v,(0,(gy-y0)*sc),(v.shape[1],(gy-y0)*sc),c,1)
    cv2.putText(v,f'{tag}{i}',(3,20),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,0,0),2); ims.append(v)
cols=min(len(ims),int(sys.argv[9]) if len(sys.argv)>9 else 4)
while len(ims)%cols: ims.append(np.zeros_like(ims[0]))
cv2.imwrite(out,np.vstack([np.hstack(ims[i:i+cols]) for i in range(0,len(ims),cols)]))
