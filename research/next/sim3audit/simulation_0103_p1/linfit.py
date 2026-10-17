import numpy as np
def fit_track(t,x,y,Ps,dds,nh=2):
    """x=(a+bt)/(1+dd t)+harmonics, y=(c+e t)/(1+dd t)+harmonics; grid over period P (s) and dd; linear LS."""
    best=None
    for P in Ps:
        w=2*np.pi/P
        H=np.column_stack([f(k*w*t) for k in range(1,nh+1) for f in (np.cos,np.sin)])
        for dd in dds:
            A=np.column_stack([1/(1+dd*t), t/(1+dd*t), H])
            cx,rx,_,_=np.linalg.lstsq(A,x,rcond=None)
            cy,ry,_,_=np.linalg.lstsq(A,y,rcond=None)
            sse=((A@cx-x)**2).sum()+((A@cy-y)**2).sum()
            if best is None or sse<best[0]: best=(sse,P,dd,cx,cy)
    sse,P,dd,cx,cy=best
    f=lambda tt:((cx[0]+cx[1]*tt)/(1+dd*tt),(cy[0]+cy[1]*tt)/(1+dd*tt))
    return dict(P=P,dd=dd,cx=cx,cy=cy,rms=np.sqrt(sse/(2*len(t))),f=f)
