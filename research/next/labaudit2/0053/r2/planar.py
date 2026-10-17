import numpy as np, json, sys
f=711.;cx=640.;cy=360.
T=json.load(open('bintrack.json'))
tr=np.load('track_captured_0053_10.npy')
ref=10
def normc(x): return np.c_[(x[:,0]-cx)/f,(x[:,1]-cy)/f,np.ones(len(x))]
def nvec(p,r):
    p,r=np.radians(p),np.radians(r); return np.array([np.sin(r)*np.cos(p),-np.cos(r)*np.cos(p),-np.sin(p)])
def rot(n,psi):
    K=np.array([[0,-n[2],n[1]],[n[2],0,-n[0]],[-n[1],n[0],0]])
    return np.eye(3)+np.sin(psi)*K+(1-np.cos(psi))*K@K
def basis(n):
    e1=np.cross(n,[0,0,1.]); e1/=np.linalg.norm(e1); e2=np.cross(n,e1); return e1,e2
def sampson(n,psi,phi,x0,x1):
    e1,e2=basis(n); t=np.cos(phi)*e1+np.sin(phi)*e2
    tx=np.array([[0,-t[2],t[1]],[t[2],0,-t[0]],[-t[1],t[0],0]])
    E=tx@rot(n,psi)
    Ex0=x0@E.T; Etx1=x1@E
    num=(x1*Ex0).sum(1)**2
    den=Ex0[:,0]**2+Ex0[:,1]**2+Etx1[:,0]**2+Etx1[:,1]**2
    return num/den*f*f   # px^2
pairs=[int(a) for a in sys.argv[1].split(',')] if len(sys.argv)>1 else [0,4,16,22,28,34,40,47]
data={}
for j in pairs:
    ok=~np.isnan(tr[j,:,0])&~np.isnan(tr[ref,:,0])
    data[j]=(normc(tr[ref][ok]),normc(tr[j][ok]))
def fitpair(n,j,init=None):
    x0,x1=data[j]
    # coarse grid
    best=None
    psis=np.radians(np.arange(-20,20.01,1.0)); phis=np.radians(np.arange(0,360,2.0))
    if init is not None:
        psis=init[0]+np.radians(np.arange(-3,3.01,0.5)); phis=init[1]+np.radians(np.arange(-6,6.01,1))
    for psi in psis:
        for phi in phis:
            r=sampson(n,psi,phi,x0,x1); c=np.sum(np.minimum(r,4.0))   # robust (cap 2px)
            if best is None or c<best[0]: best=(c,psi,phi)
    # refine
    c,psi,phi=best; st=np.radians(0.25)
    for _ in range(40):
        improved=False
        for dpsi,dphi in [(st,0),(-st,0),(0,st),(0,-st)]:
            r=sampson(n,psi+dpsi,phi+dphi,x0,x1); cc=np.sum(np.minimum(r,4.0))
            if cc<c: c,psi,phi=cc,psi+dpsi,phi+dphi; improved=True
        if not improved: st/=2
        if st<np.radians(0.005): break
    return c,psi,phi
results=[]
for pitch in np.arange(30,46,1.0):
    for roll in np.arange(-6,16,1.0):
        n=nvec(pitch,roll); tot=0; cnt=0
        for j in pairs:
            c,psi,phi=fitpair(n,j); tot+=c; cnt+=len(data[j][0])
        results.append((tot/cnt,pitch,roll))
        print(f'pitch {pitch:.0f} roll {roll:.0f} mean capped sampson {tot/cnt:.4f}',flush=True)
results.sort()
print('best',results[:8])
