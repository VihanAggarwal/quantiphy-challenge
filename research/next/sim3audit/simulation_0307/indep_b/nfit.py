import numpy as np
from frame3d import axes
from sweep import to3d, E, C
f=3590; Vz=18.49
V,S,U=axes(f)
d1,d2=102.6664,121.8263
def implied_N(body, shift=0):
    # body = (fore,span,up) offset from fin-top midpoint; returns N such that ranges match d2/d1, for t=i/N+shift frames
    best=None
    for N in np.arange(22,28.001,0.01):
        vzf=Vz/N
        i1=N+shift; i2=2*N+shift
        def P(i):
            XL=to3d((1378,821),0.008866,f,vzf,iref=i)[0]; XR=to3d((1950,712),0.008146,f,vzf,iref=i)[0]
            return (XL+XR)/2+body[0]*V+body[1]*S+body[2]*U
        r1=np.linalg.norm(P(i1)); r2=np.linalg.norm(P(i2))
        err=(r1-d1)**2+(r2-d2)**2
        if best is None or err<best[0]: best=(err,N,r1,r2)
    return best
cands={'AABB centre':(-2.09,-0.2,-1.58),'fin-top mid':(0,0,0),'wing/pod mid':(0.4,-0.2,-2.0),'tail fin':(-9.5,-0.2,-1.8),'canopy':(2.8,0,-0.5),'AABB centre, bottom':(-2.09,-0.2,-3.57)}
for k,b in cands.items():
    for sh in [0,1,-1]:
        e,N,r1,r2=implied_N(b,sh)
        print('%-22s t0-shift %+d frames: N=%.2f  r1=%.2f r2=%.2f rms=%.3f'%(k,sh,N,r1,r2,np.sqrt(e/2)))
