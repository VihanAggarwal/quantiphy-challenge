import numpy as np, sys
c=sys.argv[1] if len(sys.argv)>1 else '0304'
trall=np.load(f'tracks_{c}.npy').astype(np.float64)[:,1:]   # frames 1..71
rng=np.random.default_rng(0)
tr=trall[rng.choice(len(trall),min(120,len(trall)),replace=False)][:,::2]
T=tr.shape[1]; t=np.arange(T)*2.0
ngrid=np.exp(np.linspace(np.log(50),np.log(6000),160))
S=ngrid[:,None]/(ngrid[:,None]+t[None,:])
ss=(S*S).sum(1)
def fit_tracks(V, tr, t=t, S=S, ss=ss):
    X=tr-V
    A=np.einsum('gt,ntk->ngk',S,X)/ss[None,:,None]
    xx=(X**2).sum((1,2))
    res=xx[:,None]-(A**2).sum(2)*ss[None,:]
    g=np.argmin(res,1)
    return res[np.arange(len(tr)),g]/len(t), ngrid[g]
def cost(V): r,_=fit_tracks(np.asarray(V),tr); return np.median(r)
best=None
for vx in np.linspace(-4000,1000,26):
    for vy in np.linspace(-4000,400,23):
        cc=cost([vx,vy])
        if best is None or cc<best[0]: best=(cc,vx,vy)
print('grid best',best,flush=True)
for step in (80,20,5,1):
    cx,cy=best[1],best[2]
    for vx in np.arange(cx-4*step,cx+4.1*step,step):
        for vy in np.arange(cy-4*step,cy+4.1*step,step):
            cc=cost([vx,vy])
            if cc<best[0]: best=(cc,vx,vy)
V=np.array(best[1:]); print('V',V,'medres',best[0])
np.save(f'V_{c}.npy',V)
d=np.mean(tr[:,-1]-tr[:,0],0); d/=np.linalg.norm(d)
print('track dir',d)
for k in np.linspace(-1500,1500,13):
    print('shift along V-dir %6.0f  cost %.4f'%(k, cost(V+k*d)))
