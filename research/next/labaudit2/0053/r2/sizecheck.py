import numpy as np, json
f=711.;cx=640.;cy=360.
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return d/np.linalg.norm(d)
def nvec(p,r):
    p,r=np.radians(p),np.radians(r); return np.array([np.sin(r)*np.cos(p),-np.cos(r)*np.cos(p),-np.sin(p)])
T=json.load(open('bintrack.json'))
R=np.array([ray(t['cx'],t['cy']) for t in T]); A=np.array([t['area'] for t in T]); cosa=R[:,2]
bw=np.array([t['bw'] for t in T]); bh=np.array([t['bh'] for t in T])
P10=2.73*R[10]
size=np.sqrt(A*cosa**3)
idx=[0,4,8,10,14,18,22,26,30,34,38,42,47]
for name,(p,r) in [('image-n',(37,10)),('valley',(34,13)),('roll8',(37,8)),('depthfit',(37.4,1.4))]:
    n=nvec(p,r); s=(n@P10)/(R@n)
    prod=size*s; prod/=prod[10]
    k=np.polyfit(s,prod,1)
    print(f'{name:9s} range0 {s[0]:.3f} range47 {s[47]:.3f}  sqrt(A)*range normalised:',' '.join(f'{prod[i]:.3f}' for i in idx), f' slope vs range {k[0]:+.3f}/m')
