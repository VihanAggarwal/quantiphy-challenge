import json, numpy as np
rows=json.load(open('diam2_simulation_0254.json'))
R={int(r[0]):r for r in rows}
fr=np.array(sorted(i for i in R if 19<=i<=46))
cx=np.array([R[i][5] for i in fr]); cy=np.array([R[i][6] for i in fr])
d=np.array([np.cos(np.radians(44.224)),np.sin(np.radians(44.224))])
s=cx*d[0]+cy*d[1]; t=fr/24.0
# projective of quadratic: s = sinf + M/(1+q1 t+q2 t^2); grid over q1,q2, linear solve for sinf,M
best=None
for q1 in np.linspace(-0.5,0.5,201):
    for q2 in np.linspace(-0.5,0.5,201):
        den=1+q1*t+q2*t**2
        if np.any(den<=0.05): continue
        A=np.c_[np.ones_like(t),1/den]
        c=np.linalg.lstsq(A,s,rcond=None)[0]; r=s-A@c; e=(r**2).sum()
        if best is None or e<best[0]: best=(e,q1,q2,c,r,den)
e,q1,q2,c,r,den=best
print('projective fit q1,q2',q1,q2,'sinf,M',c,'rms',r.std())
print('implied size ratio frame46/frame19 (den19/den46):',den[0]/den[-1])
