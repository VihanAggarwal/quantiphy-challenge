# Eagle silhouette extents in 0023/0025 (same camera). Seeded at frame 24 (471,373); windowed tracking; mast excluded.
import cv2, numpy as np, pandas as pd, sys
vid=sys.argv[1]; thr=float(sys.argv[2])
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4'); fr=[]
while True:
    ok,img=cap.read()
    if not ok: break
    fr.append(img)
fr=np.array(fr); bg=np.median(fr,axis=0).astype(np.float32)
def measure(i,pred):
    f=fr[i].astype(np.float32); d=np.ascontiguousarray((bg-f).mean(axis=2))   # eagle darker than cliff/sky
    x0,y0=int(pred[0]-40),int(pred[1]-40)
    sub=d[max(y0,0):y0+80,max(x0,0):x0+80]
    if sub.shape[0]<10 or sub.shape[1]<10: return None
    m=np.ascontiguousarray((sub>thr).astype(np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    best=None
    for k in range(1,n):
        x,y,w,h,a=st[k]
        if a<15: continue
        if w<=8 and h>30: continue
        dist=np.hypot(cen[k][0]+max(x0,0)-pred[0],cen[k][1]+max(y0,0)-pred[1])
        if dist>30: continue
        if best is None or a>best[1]: best=(k,a)
    if best is None: return None
    k=best[0]; x,y,w,h,a=st[k]
    ys,xs=np.nonzero(lab==k); xs=xs+max(x0,0); ys=ys+max(y0,0)
    pts=np.ascontiguousarray(np.c_[xs,ys].astype(np.float32)); hull=cv2.convexHull(pts)[:,0,:] if len(pts)>=3 else pts
    D=np.sqrt(((hull[:,None,:]-hull[None,:,:])**2).sum(-1)); a1,a2=np.unravel_index(D.argmax(),D.shape)
    return dict(frame=i,cx=xs.mean(),cy=ys.mean(),area=a,w=w,h=h,feret=D.max(),fdx=abs(hull[a2,0]-hull[a1,0]),fdy=abs(hull[a2,1]-hull[a1,1]))
rows={}
pos=np.array([471.0,373.0]); vel=np.array([10.5,0])
r=measure(24,pos); rows[24]=r
for direction in (1,-1):
    pos=np.array([rows[24]['cx'],rows[24]['cy']]); v=np.array([10.5*direction,0.0])
    i=24
    while 0<=i+direction<len(fr):
        i+=direction; pred=pos+v
        r=measure(i,pred)
        if r is None: pos=pred; continue
        newp=np.array([r['cx'],r['cy']]); v=0.7*v+0.3*(newp-pos); v[1]*=0.5; pos=newp; rows[i]=r
df=pd.DataFrame([rows[k] for k in sorted(rows)])
df.to_csv(f'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p1/{vid}_eagle.csv',index=False)
print(df.round(1).to_string())
