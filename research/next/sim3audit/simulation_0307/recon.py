import numpy as np
c=np.array([1280.,720.])
allT={k:np.load(f'tracks_{k}.npy') for k in ['0303','0305','0307']}
def fit_vp(T):
    A=[];b=[]
    for tr in T:
        P=tr[1:]
        m=P.mean(0); U,S,Vt=np.linalg.svd(P-m); d=Vt[0]; n=np.array([-d[1],d[0]])
        A.append(n); b.append(n@m)
    A=np.array(A);b=np.array(b)
    return np.linalg.lstsq(A,b,rcond=None)[0]
def track_fit(tr,e,idx):
    d=tr[idx]-e
    rho=np.linalg.norm(d,axis=1)
    ang=np.arctan2(d[:,1],d[:,0]); a0=np.angle(np.mean(np.exp(1j*ang)))
    u=np.array([np.cos(a0),np.sin(a0)])
    perp=d@np.array([-u[1],u[0]])
    # weighted fit 1/rho = A + B i, weights rho^2 (pixel-ish)
    w=rho**2
    M=np.stack([np.ones_like(idx,dtype=float),idx.astype(float)],1)
    W=np.sqrt(w)
    A,B=np.linalg.lstsq(M*W[:,None],(1/rho)*W,rcond=None)[0]
    pred=1/(A+B*idx)
    along=rho-pred
    return A,B,u,np.sqrt(np.mean(perp**2+along**2))
def total(T,e,idx):
    return np.sqrt(np.mean([track_fit(tr,e,idx)[3]**2 for tr in T]))
out={}
for k,T in allT.items():
    idx=np.arange(1,T.shape[1])
    e=fit_vp(T)
    # refine by grid search
    step=40.
    for it in range(6):
        best=(total(T,e,idx),e)
        for dx in (-2,-1,0,1,2):
            for dy in (-2,-1,0,1,2):
                ee=e+np.array([dx,dy])*step
                s=total(T,ee,idx)
                if s<best[0]: best=(s,ee)
        e=best[1]; step/=2.5
    rms=total(T,e,idx)
    res=[track_fit(tr,e,idx) for tr in T]
    n=np.array([r[0]/r[1] for r in res])  # frames-to-contact at i=0 : Z(i)=Vzf*(n+i)
    rr=np.array([r[3] for r in res])
    print(k,'VP',e.round(1),'rms',rms.round(3),'n range',n.min().round(1),n.max().round(1),'median track rms',np.median(rr).round(3))
    out[k]=dict(e=e,n=n,rms=rr,T=T)
np.save('recon.npy',out,allow_pickle=True)
