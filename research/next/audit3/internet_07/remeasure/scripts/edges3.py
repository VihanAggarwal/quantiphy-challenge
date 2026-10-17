# full per-row edge extraction for left and right body edges, rows 540-1050, with prediction from coarse centre
from load import load
import numpy as np, cv2, json
fr=load(gray=False)
tab=np.load('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/edges_tab.npy')
Rup={int(r[0]):r[1] for r in tab}
out={}
rows=list(range(540,1052,3))
for i in range(55,80):
    f=cv2.GaussianBlur(fr[i].astype(np.float32),(0,0),1.2)
    g=np.abs(cv2.Sobel(f,cv2.CV_32F,1,0,ksize=3)).sum(2)
    g=cv2.blur(g,(1,5))
    R0=Rup[i]; L0=R0-425
    rec=[]
    for r in rows:
        p=g[r]
        res=[]
        for x0,win in ((L0,35),(R0,30)):
            a=int(max(1,x0-win)); b=int(min(1918,x0+win))
            if b-a<8: res.append((np.nan,0)); continue
            seg=p[a:b]; k=int(np.argmax(seg))
            if k==0 or k==len(seg)-1: res.append((np.nan,0)); continue
            y0,y1,y2=seg[k-1],seg[k],seg[k+1]; d=0.5*(y0-y2)/(y0-2*y1+y2)
            res.append((float(a+k+d),float(y1)))
        rec.append((r,res[0][0],res[0][1],res[1][0],res[1][1]))
    out[i]=rec
json.dump(out,open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/edges3.json','w'))
# overlay
ims=[]
for i in (62,66,70,74,78):
    im=fr[i].copy()
    for r,xl,sl,xr,sr in out[i]:
        if xl==xl: cv2.circle(im,(int(round(xl)),r),2,(0,0,255) if sl>40 else (0,255,255),-1)
        if xr==xr: cv2.circle(im,(int(round(xr)),r),2,(255,0,0) if sr>40 else (0,255,0),-1)
    R0=int(Rup[i]); x0=max(0,R0-560); 
    crop=im[480:1080,x0:x0+700]
    if crop.shape[1]<700: crop=np.hstack([crop,np.zeros((600,700-crop.shape[1],3),np.uint8)])
    ims.append(cv2.resize(crop,(350,300)))
cv2.imwrite('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/ov_edges.png',np.hstack(ims))
