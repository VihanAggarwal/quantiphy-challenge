# Route C: constant-velocity (or const-accel) 3D straight-line fit from image centres only, scale from ToF anchor
import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/remeasure_work/scripts')
from geom import *
base='/home/user/quantiphy-challenge/research/next/labaudit2/0032/remeasure_work/'
R0=137.3
def proj(P): return np.c_[cx+f*P[:,0]/P[:,2], cy+f*P[:,1]/P[:,2]]
def model(p,t,acc):
    u0,v0=p[0],p[1]; V=p[2:5]; A=p[5:8] if acc else np.zeros(3)
    P0=R0*ray(u0,v0)
    return P0[None,:]+t[:,None]*V[None,:]+0.5*(t**2)[:,None]*A[None,:]
def fit(t,obs,acc,p0):
    p=p0.copy(); lam=1e-3
    def r(p): return (proj(model(p,t,acc))-obs).ravel()
    for it in range(200):
        r0=r(p); J=np.zeros((len(r0),len(p)))
        for k in range(len(p)):
            dp=np.zeros(len(p)); dp[k]=1e-4*max(1,abs(p[k]))
            J[:,k]=(r(p+dp)-r0)/dp[k]
        H=J.T@J; g=J.T@r0
        step=np.linalg.solve(H+lam*np.diag(np.diag(H)),-g)
        if (r(p+step)**2).sum()<(r0**2).sum(): p=p+step; lam*=0.3
        else: lam*=10
        if np.abs(step).max()<1e-7: break
    return p, np.sqrt((r(p)**2).mean())
def capidx(j): return np.where(j>=36, j+2, j+1)
for tag,src in (('a circle','circ_a.npy'),('ax circle','circ_ax.npy'),('a blob','white_rows_0032.npy'),('ax blob','white_rows_0032x.npy')):
    C=np.load(base+src)
    sel=C[:,0]>=36
    j=C[sel,0]; obs=C[sel,1:3]
    c=capidx(j); t=(c-38)/25.0
    for acc in (False,True):
        p0=np.r_[obs[0],15.,1.,-60.]
        if acc: p0=np.r_[p0,0,0,0]
        p,rms=fit(t,obs,acc,p0)
        V=p[2:5]; A=p[5:8] if acc else np.zeros(3)
        P=model(p,np.array([0,1/25.]),acc)
        fd=np.linalg.norm(P[1]-P[0])*25
        # VP of direction
        vp=(cx+f*V[0]/V[2], cy+f*V[1]/V[2])
        # direction vs table normal: angle of V to plane
        ang=np.degrees(np.arcsin(abs(n@V)/np.linalg.norm(V)))
        print('%-10s acc=%d rms=%.2fpx  V=%s |V|=%.1f  fwd38->39=%.1f  A=%s  VP=(%.0f,%.1f)  angle to table plane %.2f deg'%(tag,acc,rms,np.round(V,1),np.linalg.norm(V),fd,np.round(A,0),vp[0],vp[1],ang))
