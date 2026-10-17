import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/remeasure_work/scripts')
from geom import *
base='/home/user/quantiphy-challenge/research/next/labaudit2/0032/remeasure_work/'
Rs_anchor=135.3; r_ball=2.0
def capidx(j): return np.where(j>=36, j+2, j+1)   # c(j)=round(j*25/24): 35->36, 36->38
for tag in ('a','ax'):
    C=np.load(base+'circ_%s.npy'%tag)
    sel=C[:,0]>=36
    j=C[sel,0]; u=C[sel,1]; v=C[sel,2]; rp=C[sel,3]
    c=capidx(j).astype(float); t=c/25.0
    # Route A: plane, h calibrated with anchor at video 36 (cap 38)
    d36=ray(u[0],v[0]); hc=(Rs_anchor+r_ball)*(n@d36)    # centre-plane distance
    PA=np.array([on_plane(a,b,hc) for a,b in zip(u,v)])
    # Route B: size; smooth 1/r linearly in time? use 1/r_px ~ range; fit range vs t quadratically
    Rsz=(Rs_anchor+r_ball)*rp[0]/rp      # anchored at first frame (noisy)
    # better: anchor via fit: range = k / r ; k fixed by matching fitted range at t0 to anchor
    pr=np.polyfit(t,1/rp,2); rfit=1/np.polyval(pr,t)
    Rsz2=(Rs_anchor+r_ball)*rfit[0]/rfit
    PB=np.array([R*ray(a,b) for R,a,b in zip(Rsz2,u,v)])
    print('== %s   h_centre=%.2f (h=%.2f)'%(tag,hc,hc+r_ball))
    print(' frame  cap   R_plane  R_size(raw)  R_size(fit)')
    for k in range(len(j)):
        print('  %2d  %2d  %6.1f  %6.1f  %6.1f'%(j[k],c[k],np.linalg.norm(PA[k]),Rsz[k],Rsz2[k]))
    for name,P in (('plane',PA),('size',PB)):
        # quadratic fit in t
        T=t-t[0]
        A=np.c_[np.ones_like(T),T,T**2]
        co,_,_,_=np.linalg.lstsq(A,P,rcond=None)
        res=P-A@co
        sp=lambda tt: np.linalg.norm(co[1]+2*co[2]*tt)
        # label style forward diff on fitted positions
        def fd(c0):
            t0=(c0-c[0])/25; t1=(c0+1-c[0])/25
            p0=co[0]+co[1]*t0+co[2]*t0**2; p1=co[0]+co[1]*t1+co[2]*t1**2
            q0=p0*(1-r_ball/np.linalg.norm(p0)); q1=p1*(1-r_ball/np.linalg.norm(p1))
            return np.linalg.norm(p1-p0)*25, np.linalg.norm(q1-q0)*25
        raw=[np.linalg.norm(P[k+1]-P[k])*25/(c[k+1]-c[k]) for k in range(len(j)-1)]
        print(' %s: fit rms %.2f cm; inst speed at cap38 %.1f, cap40 %.1f, cap44 %.1f; fwd-diff 38->39 phys %.1f label %.1f; 37->38 extrap phys %.1f'%(name,np.sqrt((res**2).sum(1).mean()),sp(0),sp(2/25),sp(6/25),*fd(38),fd(37)[0]))
        print('   raw step speeds', np.round(raw,1))
        print('   mean velocity vector over fit (cm/s)', np.round(co[1]+co[2]*(T[-1]),1), 'dir at start', np.round(co[1]/np.linalg.norm(co[1]),3))
