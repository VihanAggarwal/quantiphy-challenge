import numpy as np,sys
c=np.array([1280.,720.])
T=np.load('tracks_pool.npy'); src=np.load('src_pool.npy')
idx=np.arange(1,T.shape[1])
def track_fit(tr,e):
    d=tr[idx]-e; rho=np.linalg.norm(d,axis=1)
    ang=np.arctan2(d[:,1],d[:,0]); a0=np.angle(np.mean(np.exp(1j*ang)))
    u=np.array([np.cos(a0),np.sin(a0)]); perp=d@np.array([-u[1],u[0]])
    W=rho; M=np.stack([np.ones(len(idx)),idx.astype(float)],1)
    A,B=np.linalg.lstsq(M*W[:,None],(1/rho)*W,rcond=None)[0]
    along=rho-1/(A+B*idx)
    return A,B,np.sqrt(np.mean(perp**2+along**2))
def total(T,e): return np.sqrt(np.mean([track_fit(tr,e)[2]**2 for tr in T]))
e=np.array([-750.,-475.]); keep=np.ones(len(T),bool)
for rnd in range(3):
    step=40.
    for it in range(7):
        best=(total(T[keep],e),e)
        for dx in (-2,-1,0,1,2):
            for dy in (-2,-1,0,1,2):
                ee=e+np.array([dx,dy])*step; s=total(T[keep],ee)
                if s<best[0]: best=(s,ee)
        e=best[1]; step/=2.5
    rr=np.array([track_fit(tr,e)[2] for tr in T]); keep=rr<max(1.5,3*np.median(rr))
res=[track_fit(tr,e) for tr in T]; n=np.array([r[0]/r[1] for r in res])
print('VP',e.round(1),'kept',keep.sum(),len(T))
np.save('pool_fit.npy',dict(e=e,n=n,rr=rr,keep=keep),allow_pickle=True)
