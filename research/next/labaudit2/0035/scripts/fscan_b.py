# For camera b: test focal length hypotheses. Size-based ball centres (bb diameter known; soccer diameter free)
# -> floor plane -> angle between the two baseboards (walls should be orthogonal), residuals, camera height.
from geom import *
tr=load_tr('b'); bb=tr['bb']; sb=tr['sb']
fb=[k for k in list(range(0,11))+list(range(28,46)) if k in bb]
fs=[k for k in list(range(0,11))+list(range(26,49)) if k in sb]
def line_normal_f(a,b,f):
    p1=np.array([(0-CX)/f,(b-CY)/f,1.0]); p2=np.array([(1000-CX)/f,(a*1000+b-CY)/f,1.0])
    m=np.cross(p1,p2); return m/np.linalg.norm(m)
for f in [700,711,730,750,765,777,790,810]:
    K=166.1*f/716.0
    Pb=np.array([size_range(bb[k],K,f=f)*ray(bb[k]['cx'],bb[k]['cy'],f) for k in fb])
    best=None
    for Ds in np.arange(0.160,0.200,0.002):
        Ks=K*Ds/0.232
        Ps=np.array([size_range(sb[k],Ks,f=f)*ray(sb[k]['cx'],sb[k]['cy'],f) for k in fs])
        n=np.array([0,-0.8,-0.6]); 
        for it in range(8):
            Q=np.vstack([Pb,Ps+(0.116-Ds/2)*n]); n,hc=fit_plane(Q)
        res=Q@n+hc; rms=np.sqrt((res**2).mean())
        if best is None or rms<best[0]: best=(rms,Ds,n,hc)
    rms,Ds,n,hc=best
    mR=line_normal_f(0.1982,72.44,f); mL=line_normal_f(-0.5346,517.22,f)
    d1=np.cross(n,mR); d2=np.cross(n,mL); d1/=np.linalg.norm(d1); d2/=np.linalg.norm(d2)
    ang=np.degrees(np.arccos(abs(d1@d2)))
    print(f'f={f} Ds={Ds:.3f} n={np.round(n,3)} cam_h={hc+0.116:.3f} pitch={np.degrees(np.arcsin(-n[2])):.1f} rms={100*rms:.2f}cm baseboard angle={ang:.1f}')
