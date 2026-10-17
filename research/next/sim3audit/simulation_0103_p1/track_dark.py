# Track dark blobs in ROI (y<ymax) via median background diff. Prints comps per frame.
import cv2, numpy as np, sys, pandas as pd
vid=sys.argv[1]; out=sys.argv[2]; ymax=int(sys.argv[3]); thr=float(sys.argv[4])
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr=[]
while True:
    ok,img=cap.read()
    if not ok: break
    fr.append(img)
fr=np.array(fr)
bg=np.median(fr,axis=0).astype(np.float32)
cv2.imwrite(out.replace('.csv','_bg.png'),bg.astype(np.uint8))
rows=[]
for i,f in enumerate(fr):
    d=(bg-f.astype(np.float32)).mean(axis=2)  # darker than bg -> positive
    d[ymax:]=0
    m=(d>thr).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    comps=sorted([(st[k,4],k) for k in range(1,n)],reverse=True)
    for rank,(area,k) in enumerate(comps[:3]):
        if area<5: continue
        x,y,w,h,a=st[k]
        ys,xs=np.nonzero(lab==k); wts=d[ys,xs]
        rows.append(dict(frame=i,rank=rank,area=a,x=x,y=y,w=w,h=h,cx=cen[k][0],cy=cen[k][1],
                         wcx=(xs*wts).sum()/wts.sum(),wcy=(ys*wts).sum()/wts.sum()))
pd.DataFrame(rows).to_csv(out,index=False)
