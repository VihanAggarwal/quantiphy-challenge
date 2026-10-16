import cv2, numpy as np, sys
from extract import load
tag=sys.argv[1]; a=int(sys.argv[2]); b=int(sys.argv[3]); step=int(sys.argv[4]) if len(sys.argv)>4 else 1
x0,x1,y0,y1=[int(v) for v in (sys.argv[5:9] if len(sys.argv)>8 else (200,560,60,680))]
fr=load(tag)
ims=[]
for i in range(a,b+1,step):
    c=fr[i][y0:y1,x0:x1].copy()
    cv2.putText(c,str(i),(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
    ims.append(c)
n=len(ims); cols=min(n,8)
while len(ims)%cols: ims.append(np.zeros_like(ims[0]))
m=np.vstack([np.hstack(ims[i:i+cols]) for i in range(0,len(ims),cols)])
cv2.imwrite(f'crops_{tag}_{a}_{b}.jpg',m,[cv2.IMWRITE_JPEG_QUALITY,90])
print(m.shape)
