# Fall phase (t = 1.4-1.6 s): straight-line horizontal motion continued from the rolling phase, height from the image v.
# Scale: plane geometry (f, table 60.3 x 76), then rescaled so the c35 surface range equals the stated 0.738 m.
import numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0033/scripts')
from geo import *
def run(R='x',f=711,anchor=True,verbose=True):
    P=pose(f); T=load_track(R); Cp=json.load(open(BASE+'capsule_%s.json'%R))
    inv={cap(k):k for k in T}
    def mid(c): e=Cp[str(inv[c])]; return np.array(e['mid'])
    # rolling: plane positions (centre 2 cm up) for c31..c36 from capsule mids; fit straight line in table coords
    cs=np.arange(31,37); tab=[]
    for c in cs:
        u,v=mid(c); X=on_plane(u,v,P,2.0); tab.append(P['R'].T@(X-P['t']))
    tab=np.array(tab)
    A=np.vstack([cs-35,np.ones(len(cs))]).T
    bx=np.linalg.lstsq(A,tab[:,0],rcond=None)[0]; by=np.linalg.lstsq(A,tab[:,1],rcond=None)[0]
    # range at c35 on the smooth line
    X35=P['R']@np.array([bx[1],by[1],2.0])+P['t']; R35=np.linalg.norm(X35)
    k=(73.8+2.0)/R35 if anchor else 1.0
    # for c>=36: horizontal position on the line; height from v (solve along ray: point whose table x,y lie on the line)
    out={}
    for c in [35,36,38,39]:
        u,v=mid(c)
        if c==39:  # truncated streak: use the capsule start point (exposure start) and add half the c38 exposure motion
            e=Cp[str(inv[c])]; u,v=np.array(e['p0'])
        r=ray(u,v,f)
        # find s such that table-coords of s*r lie on vertical plane through rolling line: param by line time tau
        # unknowns s, tau: R^T(s r - t) = (bx0+bx1? ...) -> solve x,y equations (2 eq, 2 unknowns)
        Rt=P['R'].T; a=Rt@r; b=-Rt@P['t']
        M=np.array([[a[0],-bx[0]],[a[1],-by[0]]]); rhs=np.array([bx[1]-b[0],by[1]-b[1]])
        s,tau=np.linalg.solve(M,rhs)
        Xt=a*s+b
        out[c]=dict(tau=tau,z=Xt[2],X=s*r,rng=s)
    if verbose:
        print(R,f,'line v=(%.2f,%.2f) cm/fr |v| %.1f cm/s (scaled %.1f), R35 %.1f, k %.3f'%(bx[0],by[0],np.hypot(bx[0],by[0])*25,np.hypot(bx[0],by[0])*25*k,R35,k))
        for c in out: print('   c%d tau %.2f (line time) z_table %.1f cm range %.1f (scaled %.1f)'%(c,out[c]['tau']+35,out[c]['z'],out[c]['rng'],out[c]['rng']*k))
    return out,bx,by,k,P
if __name__=='__main__':
    for R in ['x','s']:
        for f in [711,740]:
            run(R,f)
