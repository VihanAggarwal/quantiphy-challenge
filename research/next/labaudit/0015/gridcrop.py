import cv2, numpy as np, sys
from extract import load
tag=sys.argv[1]; frames=[int(a) for a in sys.argv[2].split(',')]
x0,x1,y0,y1=[int(v) for v in sys.argv[3].split(',')]; sc=float(sys.argv[4]); out=sys.argv[5]
fr=load(tag); ims=[]
for i in frames:
    c=fr[i][y0:y1,x0:x1].copy()
    c=cv2.resize(c,None,fx=sc,fy=sc,interpolation=cv2.INTER_CUBIC)
    for gx in range((x0//20+1)*20,x1,20):
        X=int((gx-x0)*sc); cv2.line(c,(X,0),(X,c.shape[0]),(0,255,0) if gx%100 else (0,0,255),1)
        if gx%100==0: cv2.putText(c,str(gx),(X+2,12),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
    for gy in range((y0//20+1)*20,y1,20):
        Y=int((gy-y0)*sc); cv2.line(c,(0,Y),(c.shape[1],Y),(0,255,0) if gy%100 else (0,0,255),1)
        if gy%100==0: cv2.putText(c,str(gy),(2,Y-2),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
    cv2.putText(c,f'{tag}{i}',(5,c.shape[0]-8),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,0,0),2)
    ims.append(c)
cols=int(sys.argv[6]) if len(sys.argv)>6 else len(ims)
while len(ims)%cols: ims.append(np.zeros_like(ims[0]))
m=np.vstack([np.hstack(ims[i:i+cols]) for i in range(0,len(ims),cols)])
cv2.imwrite(out,m,[cv2.IMWRITE_JPEG_QUALITY,92]); print(m.shape)
