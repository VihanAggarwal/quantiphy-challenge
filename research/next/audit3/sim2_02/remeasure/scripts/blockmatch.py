import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
def sub(r,i):
    return (r[i-1]-r[i+1])/(2*(r[i-1]-2*r[i]+r[i+1])) if 0<i<len(r)-1 else 0
def bm(F, box0, v, dts=(1,2,4,8,12,16,24), search=8):
    # box0 = (x0,y0,x1,y1) at frame 0 in F coords, moves with v px/frame
    x0,y0,x1,y1=box0
    out={}
    n=len(F)
    for dt in dts:
        ds=[]
        for k in range(0,n-dt):
            xa=int(round(x0+v*k)); xb=xa+(x1-x0)
            if xa<0 or xb>F.shape[2]: continue
            T=F[k][y0:y1,xa:xb]
            pred=xa+v*dt
            sa=int(pred-search); sb=int(pred+search)+(x1-x0)
            if sa<0 or sb>F.shape[2]: continue
            S=F[k+dt][y0-2:y1+2, sa:sb]
            r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED)
            iy,ix=np.unravel_index(np.argmax(r),r.shape)
            dx=sa+ix+sub(r[iy],ix)-xa
            ds.append((k,dx/dt,r[iy,ix]))
        out[dt]=np.array(ds)
    return out
