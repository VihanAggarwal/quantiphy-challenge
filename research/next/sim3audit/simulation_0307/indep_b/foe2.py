import numpy as np
def cost(e,P,minlen=40):
    tot=0;n=0
    for j in range(P.shape[1]):
        ok=np.isfinite(P[:,j,0])
        if ok.sum()<minlen: continue
        q=P[ok,j]-e
        w=np.linalg.eigvalsh(q.T@q)
        tot+=w[0]; n+=ok.sum()
    return tot/n
def grid(P,cx,cy,span,step):
    best=None
    for x in np.arange(cx-span,cx+span+1e-9,step):
        for y in np.arange(cy-span,cy+span+1e-9,step):
            c=cost(np.array([x,y]),P)
            if best is None or c<best[0]: best=(c,x,y)
    return best
Ps={c:np.load(f'tracks_{c}.npy') for c in ['0303','0305','0307']}
Ps['all']=np.concatenate([Ps['0303'],Ps['0305'],Ps['0307']],axis=1)
for c,P in Ps.items():
    b=grid(P,-730,-465,120,20)
    b=grid(P,b[1],b[2],20,4)
    b=grid(P,b[1],b[2],4,1)
    print(c,'FOE',b[1],b[2],'rms',np.sqrt(b[0]))
# identity check
A=Ps['0305'];B=Ps['0307']
d=[]
for j in range(B.shape[1]):
    p=B[1,j]; dist=np.linalg.norm(A[1]-p,axis=1); k=np.argmin(dist)
    if dist[k]<1.0 and np.isfinite(A[48,k,0]) and np.isfinite(B[48,j,0]):
        d.append(np.linalg.norm(A[48,k]-B[48,j]))
print('0305 vs 0307 matched tracks', len(d), 'median diff at f48', np.median(d) if d else None)
