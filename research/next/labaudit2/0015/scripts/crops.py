import cv2, numpy as np, sys
from common import load
tag=sys.argv[1]; a,b=int(sys.argv[2]),int(sys.argv[3]); x0,y0,x1,y1=map(int,sys.argv[4:8]); out=sys.argv[8]
fr=load(tag); ims=[]
for i in range(a,b+1):
    v=fr[i][y0:y1,x0:x1].copy()
    cv2.putText(v,str(i),(3,18),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2); ims.append(v)
n=len(ims); cols=min(n,6)
while len(ims)%cols: ims.append(np.zeros_like(ims[0]))
m=np.vstack([np.hstack(ims[i:i+cols]) for i in range(0,len(ims),cols)])
cv2.imwrite(out,m)
print(m.shape, len(fr))
