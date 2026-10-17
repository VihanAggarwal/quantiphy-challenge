import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
def halfmax_extent(score, axis_rows):
    # score: 2D map (rows x cols), object high, bg low. returns subpixel left/right half-max crossing of column-max profile
    prof=score[axis_rows[0]:axis_rows[1]].max(axis=0).astype(float)
    lo=np.median(np.r_[prof[:5],prof[-5:]]); hi=np.percentile(prof,95)
    thr=(lo+hi)/2
    on=np.nonzero(prof>thr)[0]
    runs=np.split(on,np.nonzero(np.diff(on)>2)[0]+1); run=max(runs,key=len)
    a,b=run.min(),run.max()
    L=a-1+(thr-prof[a-1])/(prof[a]-prof[a-1]) if a>0 else a
    R=b+(thr-prof[b])/(prof[b+1]-prof[b]) if b+1<len(prof) else b
    return L,R
vid=sys.argv[1]; x0f,v,cy,hw,hh=map(float,sys.argv[2:7])
F=frames(vid,n=49)
L=[]
for k in range(49):
    xc=x0f+v*k
    xa=int(xc-hw); xb=int(xc+hw); ya=int(cy-hh); yb=int(cy+hh)
    c=F[k][ya:yb,xa:xb]
    hsv=cv2.cvtColor(c,cv2.COLOR_BGR2HSV).astype(float)
    s=cv2.GaussianBlur(hsv[...,1],(3,3),0)
    # use rows where object present
    rows=np.nonzero((s>60).sum(axis=1)>3)[0]
    if len(rows)==0: continue
    l,r=halfmax_extent(s,(rows.min(),rows.max()+1))
    L.append((k,xa+l,xa+r,r-l))
L=np.array(L)
np.set_printoptions(suppress=True,precision=1,linewidth=160)
print(L[::4])
print('len median %.2f mean %.2f p75 %.2f p90 %.2f max %.2f'%(np.median(L[:,3]),L[:,3].mean(),np.percentile(L[:,3],75),np.percentile(L[:,3],90),L[:,3].max()))
