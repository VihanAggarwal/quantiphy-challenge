import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
Y0=1020
F=frames('simulation_0240',Y0,1070)[:49].astype(float)
res=[]
for k in range(49):
    xc=614.6+6.2*k+5
    x0=int(xc-50); x1=int(xc+45)
    f=F[k,:,x0:x1]
    B,G,R=f[...,0],f[...,1],f[...,2]
    s=R-G   # tan positive, grass negative
    # rows of body: find rows where many columns have s>20
    rows=np.nonzero((s>20).sum(axis=1)>15)[0]
    if len(rows)==0: continue
    # use top body rows (avoid dark grass/occluded legs): from the min row to min+? use all rows with strong signal
    prof=np.percentile(s[rows],90,axis=0)   # per column, high percentile over body rows
    prof=cv2.GaussianBlur(prof.reshape(1,-1),(1,1),0).ravel()
    hi=np.percentile(prof,90); lo=np.median(np.r_[prof[:8],prof[-8:]])
    thr=(hi+lo)/2
    on=np.nonzero(prof>thr)[0]
    a,b=on.min(),on.max()
    # subpixel crossing
    def cross(i,j):
        v1,v2=prof[i],prof[j]
        return i+(thr-v1)/(v2-v1)*(j-i) if v2!=v1 else i
    L=cross(a-1,a); Rr=cross(b,b+1)
    res.append((k,x0+L,x0+Rr,Rr-L,hi,lo,Y0+rows.min(),Y0+rows.max()))
res=np.array(res)
np.set_printoptions(suppress=True,precision=1,linewidth=150)
print(res)
print('median len',np.median(res[:,3]),'mean',res[:,3].mean(),'p75',np.percentile(res[:,3],75),'p90',np.percentile(res[:,3],90))
print('left slope',np.polyfit(res[:,0],res[:,1],1),'right slope',np.polyfit(res[:,0],res[:,2],1))
