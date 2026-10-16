"""Consistency of the table plane (h) with the ball's own size scale: fit each hop's height above the plane
(ball centre, depth from 4 cm size) with a parabola of fixed g; at the bounce the centre should be 2 cm high."""
import numpy as np, sys
from track3d import track, P, F
n=np.load('plane.npy')
FPS=24.0
for v in sys.argv[1:] or ['x']:
    T=track(v); mi=T[:,3]
    idx=np.arange(12,49); p=np.polyfit(idx,1/mi[idx],2)   # smooth 1/minor (depth) in time
    Z=lambda i: F*0.04*np.polyval(p,i)
    X=np.array([P(T[i,1],T[i,2],Z(i)) if i>=12 else np.full(3,np.nan) for i in range(49)])
    hops=[(13,18),(21,27),(29,35),(37,42),(44,48)]
    for h in (0.172,0.18,0.19):
        H=h+X@n
        fits=[]
        for a,b in hops:
            t=np.arange(a,b+1)/FPS
            # fit H = c0 + c1 t - g/2 t^2 with g = 9.8 (along the table normal)
            A=np.c_[np.ones_like(t),t]; y=H[a:b+1]+4.9*t**2
            c=np.linalg.lstsq(A,y,rcond=None)[0]; fits.append(c)
        mins=[]
        for (c0,c1),(d0,d1) in zip(fits[:-1],fits[1:]):
            # bounce time where the two parabolas meet (same t^2 term -> linear)
            tb=(d0-c0)/(c1-d1); hb=c0+c1*tb-4.9*tb**2; mins.append((round(tb*FPS,2),round(hb*100,2)))
        print(v,'h=%.3f'%h,'bounces (frame, centre height cm):',mins)
