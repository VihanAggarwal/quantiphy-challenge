import json,numpy as np
from lm import least_squares
f=711.0; cx,cy=640.,360.
def cap(n): return int(np.floor(25*n/24+0.5))
tr=json.load(open('tracks.json'))
arcs={'A':range(12,19),'B':range(21,28),'C':range(29,36),'D':range(37,43),'E':range(44,49)}
def fit(sfx,frames,g=9.81,gdir=(0,1,0),Zfix=None):
    n=np.array(list(frames)); t=np.array([cap(k) for k in n])/25.0; t0=t.mean(); tt=t-t0
    u=np.array([tr[sfx][k]['cx'] for k in n]); v=np.array([tr[sfx][k]['cy'] for k in n])
    gd=np.array(gdir,float); gd/=np.linalg.norm(gd)
    def model(p):
        P0=p[:3]; V=p[3:6]
        if Zfix is not None: P0=np.array([p[0],p[1],Zfix])
        P=P0[None]+V[None]*tt[:,None]+0.5*g*gd[None]*tt[:,None]**2
        return cx+f*P[:,0]/P[:,2], cy+f*P[:,1]/P[:,2], P
    def res(p):
        a,b,_=model(p); return np.r_[a-u,b-v]
    Z0=1.0; p0=np.r_[(u.mean()-cx)/f*Z0,(v.mean()-cy)/f*Z0,Z0,0,0,0]
    r=least_squares(res,p0)
    a,b,P=model(r.x)
    return r, tt, P, np.sqrt(np.mean(r.fun**2)), n, t
for sfx in ['s','x']:
    for k,fr in arcs.items():
        r,tt,P,rms,n,t=fit(sfx,fr)
        print(sfx,k,'Z0=%.3f V=(%.3f,%.3f,%.3f) |V|=%.3f rms=%.2fpx'%(r.x[2],*r.x[3:6],np.linalg.norm(r.x[3:6]),rms), 'Z range %.3f..%.3f'%(P[0,2],P[-1,2]))
