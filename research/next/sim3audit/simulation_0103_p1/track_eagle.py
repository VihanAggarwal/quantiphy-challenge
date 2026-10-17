# Track eagle (dark blob) via median-background difference; outputs per-frame stats to csv
import cv2, numpy as np, sys, pandas as pd
vid=sys.argv[1]; out=sys.argv[2]
thr=float(sys.argv[3]) if len(sys.argv)>3 else 25
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr=[]
while True:
    ok,img=cap.read()
    if not ok: break
    fr.append(img)
fr=np.array(fr)
bg=np.median(fr,axis=0).astype(np.float32)
rows=[]
for i,f in enumerate(fr):
    d=np.abs(f.astype(np.float32)-bg).max(axis=2)
    m=(d>thr).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    comps=[(st[k,4],k) for k in range(1,n)]
    comps.sort(reverse=True)
    for rank,(area,k) in enumerate(comps[:4]):
        x,y,w,h,a=st[k]
        ys,xs=np.nonzero(lab==k)
        wts=d[ys,xs]
        rows.append(dict(frame=i,rank=rank,area=a,x=x,y=y,w=w,h=h,cx=cen[k][0],cy=cen[k][1],
                         wcx=(xs*wts).sum()/wts.sum(),wcy=(ys*wts).sum()/wts.sum()))
pd.DataFrame(rows).to_csv(out,index=False)
np.save(out.replace('.csv','_bg.npy'),bg.astype(np.uint8))
