# Joint fit: x_j(t) = vp + K_j/(t - s_j) for rigid translation; numpy Gauss-Newton via block elimination
import numpy as np, sys
vid=sys.argv[1] if len(sys.argv)>1 else '0302'
d=np.load(f'klt{vid}.npz'); T=d['T']; t=d['t']; vp=d['vp'].copy()
N=T.shape[1]
def per_track(vp):
    # for fixed vp, fit each track: radial line direction = mean dir; s_j, k_j via 1/r linear
    S=np.zeros(N); K=np.zeros((N,2)); res=np.zeros((len(t),N,2))
    for j in range(N):
        D=T[:,j]-vp; r=np.linalg.norm(D,axis=1); u=D.mean(0); u/=np.linalg.norm(u)
        A=np.polyfit(t,1/r,1); s=-A[1]/A[0]; k=1/A[0]
        S[j]=s; K[j]=u*k
        res[:,j]=vp+K[j][None,:]/(t[:,None]-s)-T[:,j]
    return S,K,res
def cost(vp):
    S,K,res=per_track(vp); return (res**2).sum()
# coarse-to-fine grid on vp
best=vp; bc=cost(vp)
for step in [64,32,16,8,4,2,1,0.5,0.25]:
    improved=True
    while improved:
        improved=False
        for dx in (-step,0,step):
            for dy in (-step,0,step):
                v=best+np.array([dx,dy]); cc=cost(v)
                if cc<bc-1e-9: bc,best,improved=cc,v,True
S,K,res=per_track(best)
rms=np.sqrt((res**2).sum(2).mean(0))
keep=rms<2.5*np.median(rms)
T=T[:,keep];N=T.shape[1]
bc=cost(best)
for step in [8,4,2,1,0.5,0.25]:
    improved=True
    while improved:
        improved=False
        for dx in (-step,0,step):
            for dy in (-step,0,step):
                v=best+np.array([dx,dy]); cc=cost(v)
                if cc<bc-1e-9: bc,best,improved=cc,v,True
S,K,res=per_track(best)
rms=np.sqrt((res**2).sum(2).mean(0))
print(vid,'vp',best,'N',N,'median rms px',np.median(rms))
print('t* percentiles',np.percentile(S,[0,5,50,95,100]))
np.savez(f'joint{vid}.npz',T=T,t=t,vp=best,s=S,K=K,rms=rms)
