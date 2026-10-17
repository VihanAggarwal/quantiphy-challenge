import cv2, numpy as np, sys
# usage: name seedx seedy (in native px) [win]
name=sys.argv[1]; sx,sy=float(sys.argv[2]),float(sys.argv[3]); win=int(sys.argv[4]) if len(sys.argv)>4 else 60
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{name}_segmented.mp4')
fps=c.get(cv2.CAP_PROP_FPS)
i=0; out=[]
while True:
    ok,f=c.read()
    if not ok: break
    H,W=f.shape[:2]
    x0,x1=int(max(0,sx-win)),int(min(W,sx+win)); y0,y1=int(max(0,sy-win)),int(min(H,sy+win))
    roi=f[y0:y1,x0:x1].astype(int)
    m=(np.abs(roi-255).max(axis=2)>40).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n>1:
        # pick component closest to seed with area>20
        best=None
        for k in range(1,n):
            if st[k,4]<15: continue
            d=np.hypot(cen[k,0]+x0-sx,cen[k,1]+y0-sy)
            if best is None or d<best[0]: best=(d,k)
        if best:
            k=best[1]
            # merge components within the bbox neighbourhood of k
            cx,cy=cen[k,0]+x0,cen[k,1]+y0
            ys,xs=np.nonzero(lab==k)
            out.append((i,cx,cy,xs.min()+x0,xs.max()+x0,ys.min()+y0,ys.max()+y0,st[k,4]))
            sx,sy=cx,cy
    i+=1
a=np.array(out)
np.save(f'trk_{name}.npy',a)
print('fps',fps,'frames',i,'tracked',len(a))
for r in a[::5]: print(' '.join(f'{v:.1f}' for v in r))
