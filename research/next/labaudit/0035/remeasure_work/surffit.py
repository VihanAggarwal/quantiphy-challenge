import numpy as np
cx,cy=640,360; R=0.116; Rs=0.089
def u(x,y,f):
    v=np.array([x-cx,y-cy,f]); return v/np.linalg.norm(v)
def KT(l,f): return np.array([f*l[0],f*l[1],cx*l[0]+cy*l[1]+l[2]])
lL=np.array([0.5362,1,-517.84]); lR=np.array([-0.19881,1,-71.728])
th=np.radians(np.linspace(1,89,441)); ph=np.radians(np.linspace(0,180,901))
TH,PH=np.meshgrid(th,ph,indexing='ij')
N=np.stack([np.sin(TH)*np.cos(PH),np.sin(TH)*np.sin(PH),np.cos(TH)],-1)
f=711.
a=KT(lL,f); b=KT(lR,f)
dL=np.cross(np.broadcast_to(a,N.shape),N); dR=np.cross(np.broadcast_to(b,N.shape),N)
r_orth=(dL*dR).sum(-1)/np.linalg.norm(dL,axis=-1)/np.linalg.norm(dR,axis=-1)
u1=u(828.7,279.9,f)
for mode in ['floor-behind','surface']:
  for assign in [('bb',2.602,'so',2.373),('bb',2.373,'so',2.602)]:
    labs=[((671.3,392.7),2.7777,R),((533.4,462.0),assign[1],R),((611.7,480.6),2.477,Rs),((689.2,488.8),assign[3],Rs)]
    # floor contact plane: n.X = hf
    # floor-behind: X = L u on floor -> hf = L (n.u)
    # surface: centre = (L+r) u, centre on plane n.X = hf - r -> hf = (L+r)(n.u) + r
    H=[]
    for p,L,r in labs:
        uu=u(*p,f); d=N@uu
        H.append(L*d if mode=='floor-behind' else (L+r)*d + r)
    H=np.stack(H,-1); hf=H.mean(-1); rel=H/hf[...,None]-1; cost=(rel**2).mean(-1)
    j=np.unravel_index(np.argmin(cost),cost.shape); n=N[j]
    rest=(hf[j]-R)/(n@u1)
    print('%-12s bb1.4=%.3f  n=%s relres=%s rms=%.4f orth=%.3f (angle %.1f deg) | rest centre pred=%.3f (size-based 3.224)'%(mode,assign[1],np.round(n,3),np.round(rel[j],4),np.sqrt(cost[j]),r_orth[j],np.degrees(np.arccos(abs(r_orth[j]))),rest))
