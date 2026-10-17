import numpy as np
def brentq(g,lo,hi,it=200):
    glo=g(lo); ghi=g(hi)
    if glo*ghi>0: return np.nan
    for _ in range(it):
        m=0.5*(lo+hi); gm=g(m)
        if glo*gm<=0: hi,ghi=m,gm
        else: lo,glo=m,gm
    return 0.5*(lo+hi)
def ray(u,v,f,cx,cy):
    r=np.array([u-cx,v-cy,f],float); return r/np.linalg.norm(r)
def P3(p,D,f,cx,cy,conv='range'):
    r=ray(p[0],p[1],f,cx,cy)
    return D*r if conv=='range' else D*r/r[2]
def solve_f(p1,p2,D1,D2,chord,cx,cy,conv='range',lo=300,hi=30000):
    g=lambda f: np.linalg.norm(P3(p2,D2,f,cx,cy,conv)-P3(p1,D1,f,cx,cy,conv))-chord
    return brentq(g,lo,hi)
