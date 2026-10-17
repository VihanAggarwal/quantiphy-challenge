import cv2, numpy as np, sys
sys.path.insert(0,'.')
from uniq import load, dup_mask
name=sys.argv[1]; sx,sy=float(sys.argv[2]),float(sys.argv[3]); win=int(sys.argv[4])
keep=dup_mask(name) if (len(sys.argv)<6 or sys.argv[5]!='nodedup') else None
fr=load(name,seg=True,gray=False)
if keep is not None: fr=[fr[i] for i in keep]
print('frames',len(fr))
out=[]
for i,f in enumerate(fr):
    H,W=f.shape[:2]
    x0,x1=int(max(0,sx-win)),int(min(W,sx+win)); y0,y1=int(max(0,sy-win)),int(min(H,sy+win))
    roi=f[y0:y1,x0:x1].astype(int)
    m=(np.abs(roi-255).max(axis=2)>40).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    best=None
    for k in range(1,n):
        if st[k,4]<15: continue
        d=np.hypot(cen[k,0]+x0-sx,cen[k,1]+y0-sy)
        if best is None or d<best[0]: best=(d,k)
    k=best[1]; ys,xs=np.nonzero(lab==k)
    cx,cy=cen[k,0]+x0,cen[k,1]+y0
    # feet: mean x of bottom 3 rows
    yb=ys.max(); fx=xs[ys>=yb-2].mean()+x0
    out.append((i,cx,cy,xs.min()+x0,xs.max()+x0,ys.min()+y0,ys.max()+y0,fx,st[k,4]))
    sx,sy=cx,cy
a=np.array(out); np.save(f'p2_{name}.npy',a)
t=a[:,0]
for col,lab in [(1,'cx'),(2,'cy'),(6,'ybot'),(5,'ytop'),(7,'footx')]:
    p=np.polyfit(t,a[:,col],1); print(lab,'slope px/frame',round(p[0],4))
h=a[:,6]-a[:,5]+1; w=a[:,4]-a[:,3]+1
print('height median',np.median(h),'p10',np.percentile(h,10),'p90',np.percentile(h,90),'width median',np.median(w))
