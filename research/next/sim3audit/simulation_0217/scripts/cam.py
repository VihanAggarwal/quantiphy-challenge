import numpy as np
f=2130.; cx=960.; cy=538.; h=0.784
vp1=4920.; vp2=-181.
D1=np.array([vp1-cx,f]); D1/=np.linalg.norm(D1)   # (x,z) along back wall, to the right
D2=np.array([vp2-cx,f]); D2/=np.linalg.norm(D2)   # toward back wall
def ground(u,v,hh=0.0):
    z=f*(h-hh)/(v-cy); x=(u-cx)*z/f
    return np.array([x,z])
def ac(P): return P@D1, P@D2
def a_from_u(u,c0):
    # point with coordinate c=c0 projecting to column u
    X=u-cx
    return c0*(f*D2[0]-X*D2[1])/(X*D1[1]-f*D1[0])
def rng(a,c,hz):
    return np.sqrt(a*a+c*c+(h-hz)**2)
