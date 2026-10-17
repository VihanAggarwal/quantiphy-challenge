import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
vid=sys.argv[1]; x0f,v,cy,hw,hh=map(float,sys.argv[2:7])
F=frames(vid,n=49)
res=[]
for k in range(len(F)):
    xc=x0f+v*k; xa=int(xc-hw); xb=int(xc+hw); ya=int(cy-hh); yb=int(cy+hh)
    d=(765-F[k][ya:yb,xa:xb].astype(float).sum(axis=2))
    m=(d>120).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(cv2.dilate(m,np.ones((3,3),np.uint8)))
    if n<2: continue
    # component closest to center
    i=1+np.argmin([abs(cen[j][0]-hw)+ (0 if st[j][4]>200 else 1e6) for j in range(1,n)])
    keep=(lab==i)
    dd=np.where(keep,d,0)
    prof=dd.max(axis=0)
    hi=np.percentile(prof[prof>0],90)
    out=[k]
    for fr in (0.15,0.3,0.5):
        thr=fr*hi
        on=np.nonzero(prof>thr)[0]; a,b=on.min(),on.max()
        L=a-1+(thr-prof[a-1])/(prof[a]-prof[a-1]) if a>0 else a
        R=b+(thr-prof[b])/(prof[b+1]-prof[b]) if b+1<len(prof) else b
        out.append(R-L)
    res.append(out)
A=np.array(res)
for j,fr in enumerate((0.15,0.3,0.5)):
    print(vid,'frac',fr,'median %.2f mean %.2f p90 %.2f max %.2f'%(np.median(A[:,j+1]),A[:,j+1].mean(),np.percentile(A[:,j+1],90),A[:,j+1].max()))
