import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
Y0=1020
F=frames('simulation_0240',Y0,1070)[:49].astype(float)
bg=np.median(F,axis=0)
res=[]
for k in range(49):
    xc=614.6+6.2*k+3
    x0=int(xc-45); x1=int(xc+42)
    f=F[k,:,x0:x1]; b=bg[:,x0:x1]
    D=np.abs(f-b).sum(axis=2)
    D=cv2.GaussianBlur(D,(3,3),0)
    rows=slice(1028-Y0,1058-Y0)
    prof=np.percentile(D[rows],85,axis=0)
    lo=np.median(np.r_[prof[:6],prof[-6:]]); hi=np.percentile(prof,85)
    thr=lo+0.5*(hi-lo)
    on=np.nonzero(prof>thr)[0]
    # largest contiguous run containing center-ish
    runs=np.split(on,np.nonzero(np.diff(on)>3)[0]+1)
    run=max(runs,key=len)
    a,bb=run.min(),run.max()
    def cross(i,j):
        v1,v2=prof[i],prof[j]
        return i+(thr-v1)/(v2-v1)*(j-i)
    L=cross(a-1,a) if a>0 else a; R=cross(bb,bb+1) if bb+1<len(prof) else bb
    res.append((k,x0+L,x0+R,R-L,lo,hi))
res=np.array(res)
np.set_printoptions(suppress=True,precision=1,linewidth=150)
print(res)
print('median len',np.median(res[:,3]),'mean',res[:,3].mean(),'p75',np.percentile(res[:,3],75),'p90',np.percentile(res[:,3],90))
print('left slope',np.polyfit(res[:,0],res[:,1],1),'right slope',np.polyfit(res[:,0],res[:,2],1))
