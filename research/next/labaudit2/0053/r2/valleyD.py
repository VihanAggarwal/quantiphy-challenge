import numpy as np, json
f=711.;cx=640.;cy=360.
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return d/np.linalg.norm(d)
def nvec(p,r):
    p,r=np.radians(p),np.radians(r); return np.array([np.sin(r)*np.cos(p),-np.cos(r)*np.cos(p),-np.sin(p)])
T=json.load(open('bintrack.json'))
R=np.array([ray(t['cx'],t['cy']) for t in T]); A=np.array([t['area'] for t in T]); size=np.sqrt(A*R[:,2]**3)
P10=2.73*R[10]
G={}
for l in open('planar_grid.txt'):
    if l.startswith('pitch'):
        w=l.split(); G[(float(w[1]),float(w[3]))]=float(w[7])
# for each pitch, best roll in grid
for p in sorted(set(k[0] for k in G)):
    rr=min((G[k],k[1]) for k in G if k[0]==p)
    n=nvec(p,rr[1]); s=(n@P10)/(R@n)
    prod=size*s; prod/=prod[10]; k=np.polyfit(s,prod,1)[0]
    print(f'pitch {p:.0f} best roll {rr[1]:.0f} resid {rr[0]:.3f} D(0.4->1.4) {np.linalg.norm(s[34]*R[34]-P10):.3f} range34 {s[34]:.3f}  size*range drift {k:+.3f}/m')
