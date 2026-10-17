import json, numpy as np, sys
rows=json.load(open('diam2_simulation_0254.json'))
R={int(r[0]):r for r in rows}
lo,hi=int(sys.argv[1]),int(sys.argv[2])
fr=np.array(sorted(i for i in R if lo<=i<=hi))
cx=np.array([R[i][5] for i in fr]); cy=np.array([R[i][6] for i in fr])
d=np.array([np.cos(np.radians(44.224)),np.sin(np.radians(44.224))])
s=cx*d[0]+cy*d[1]; t=fr/24.0
def solve(q1,q2):
    Q=1+q1*t+q2*t**2
    A=np.c_[np.ones_like(t),-1/Q]
    c=np.linalg.lstsq(A,s,rcond=None)[0]; r=s-A@c; return (r**2).sum(),c
def grid(q1s,q2s):
    best=None
    for q1 in q1s:
        for q2 in q2s:
            Q=1+q1*t+q2*t**2
            if np.any(Q<=0.01): continue
            e,c=solve(q1,q2)
            if best is None or e<best[0]: best=(e,q1,q2,c)
    return best
b=grid(np.linspace(-0.3,0.3,121),np.linspace(0.001,0.3,300))
for it in range(6):
    e,q1,q2,c=b; h1=0.3/(4**(it+1)); h2=0.3/(4**(it+1))
    b=grid(np.linspace(q1-h1,q1+h1,41),np.linspace(max(1e-5,q2-h2),q2+h2,41))
e,q1,q2,c=b
print(f'free: q1={q1:.5f} q2={q2:.5f} s_inf={c[0]:.0f} M={c[1]:.1f} rms={np.sqrt(e/len(t)):.3f} t0(rest)={-q1/(2*q2):.4f}')
# constrained from-rest at t0: q1=-2 q2 t0
for t0 in (0.0,-1/24,1/24,-0.08):
    best=None
    for q2 in np.linspace(0.0005,0.3,6000):
        e2,c2=solve(-2*q2*t0,q2)
        if best is None or e2<best[0]: best=(e2,q2,c2)
    e2,q2b,c2=best
    print(f'from rest t0={t0:+.4f}: q2={q2b:.5f} s_inf={c2[0]:.0f} M={c2[1]:.1f} rms={np.sqrt(e2/len(t)):.3f}')
json.dump(dict(q1=q1,q2=q2,sinf=c[0],M=c[1]),open('fitP2.json','w'))
