import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
vid=sys.argv[1]; x0f,v,cy,hw,hh=map(float,sys.argv[2:7]); mode=sys.argv[7]
F=frames(vid,n=49)
bg=np.median(F,axis=0).astype(np.float32)
res={f:[] for f in (0.2,0.3,0.4,0.5)}
for k in range(49):
    xc=x0f+v*k
    xa=int(xc-hw); xb=int(xc+hw); ya=int(cy-hh); yb=int(cy+hh)
    c=F[k][ya:yb,xa:xb].astype(np.float32)
    if mode=='sat':
        s=cv2.cvtColor(F[k][ya:yb,xa:xb],cv2.COLOR_BGR2HSV)[...,1].astype(float)
    else:
        s=np.sqrt(((c-bg[ya:yb,xa:xb])**2).sum(axis=2))
    s=cv2.GaussianBlur(s,(3,3),0)
    prof=s.max(axis=0)
    lo=np.median(np.r_[prof[:5],prof[-5:]]); hi=np.percentile(prof,95)
    for fr in res:
        thr=lo+fr*(hi-lo)
        on=np.nonzero(prof>thr)[0]
        runs=np.split(on,np.nonzero(np.diff(on)>2)[0]+1); run=max(runs,key=len)
        a,b=run.min(),run.max()
        L=a-1+(thr-prof[a-1])/(prof[a]-prof[a-1]) if a>0 else a
        R=b+(thr-prof[b])/(prof[b+1]-prof[b]) if b+1<len(prof) else b
        res[fr].append(R-L)
for fr in res:
    a=np.array(res[fr]); print(vid,mode,'frac',fr,'median %.1f mean %.1f p90 %.1f'%(np.median(a),a.mean(),np.percentile(a,90)))
