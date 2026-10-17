import json, numpy as np
from numpy.linalg import lstsq
rows=json.load(open('diam2_simulation_0254.json'))
R={int(r[0]):r for r in rows}
import sys
lo,hi=int(sys.argv[1]),int(sys.argv[2])
fr=np.array(sorted(i for i in R if lo<=i<=hi))
cx=np.array([R[i][5] for i in fr]); cy=np.array([R[i][6] for i in fr])
d=np.array([np.cos(np.radians(44.224)),np.sin(np.radians(44.224))])
s=cx*d[0]+cy*d[1]
t=fr/24.0
# Model B: from rest at t0, v'=a0-k v  => s = s0 + (a0/k)[(t-t0) - (1-exp(-k(t-t0)))/k]
def modelB(k,t0):
    tau=t-t0
    g=(tau-(1-np.exp(-k*tau))/k)/k  # coefficient of a0
    A=np.c_[np.ones_like(t),g]
    c,_,_,_=lstsq(A,s,rcond=None)
    r=s-A@c
    return c,r
best=None
for k in np.linspace(0.01,1.5,150):
    for t0 in np.linspace(-0.6,0.5,111):
        c,r=modelB(k,t0)
        e=(r**2).sum()
        if best is None or e<best[0]: best=(e,k,t0,c)
e,k,t0,c=best
# refine
for it in range(3):
    ks=np.linspace(k-0.02,k+0.02,41); ts=np.linspace(t0-0.02,t0+0.02,41)
    for kk in ks:
        for tt in ts:
            cc,r=modelB(kk,tt); ee=(r**2).sum()
            if ee<e: e,k,t0,c=ee,kk,tt,cc
c,r=modelB(k,t0)
a0=c[1]
print(f'frames {lo}-{hi}: Model B k={k:.4f}/s t0={t0:.4f}s a0={a0:.1f}px/s2 rms={r.std():.3f}px')
def v(tq): return (a0/k)*(1-np.exp(-k*(tq-t0))) if tq>t0 else 0.0
def S(tq): 
    tau=tq-t0
    return c[0]+a0*((tau-(1-np.exp(-k*tau))/k)/k) if tau>0 else c[0]
for tq in (0.5,1.0,1.5,1.75):
    vb=(S(tq)-S(tq-1/24))*24
    a=a0*np.exp(-k*(tq-t0))
    ab=(vb-(S(tq-1/24)-S(tq-2/24))*24)*24
    print(f'  t={tq}: v_inst={v(tq):.1f} v_back={vb:.1f} px/s  a_inst={a:.1f} a_back2={ab:.1f} px/s2')
# Model B2: constant + damping without from-rest constraint is the same family; also fit with t0 fixed at 0
for t0f in (0.0,-1/24,1/24):
    e2=None
    for kk in np.linspace(0.01,1.5,1491):
        cc,r=modelB(kk,t0f); ee=(r**2).sum()
        if e2 is None or ee<e2[0]: e2=(ee,kk,cc,r)
    print(f'  t0 fixed {t0f:.4f}: k={e2[1]:.3f} a0={e2[2][1]:.1f} rms={e2[3].std():.3f}')
