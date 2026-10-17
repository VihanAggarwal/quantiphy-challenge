import numpy as np, sys
c=sys.argv[1]; region=sys.argv[2] if len(sys.argv)>2 else 'all'
trall=np.load(f'tracks_{c}.npy').astype(np.float64)[:,1:]
x0=trall[:,0]
# body axis param: project onto track direction, from head
print('x0 x',np.percentile(x0[:,0],[0,25,50,75,100]).round(), 'y',np.percentile(x0[:,1],[0,25,50,75,100]).round())
t=np.arange(trall.shape[1]).astype(float)
ngrid=np.exp(np.linspace(np.log(50),np.log(6000),300))
S=ngrid[:,None]/(ngrid[:,None]+t[None,:]); ss=(S*S).sum(1)
def fit_tracks(V,tr):
    X=tr-V
    A=np.einsum('gt,ntk->ngk',S,X)/ss[None,:,None]
    xx=(X**2).sum((1,2))
    res=xx[:,None]-(A**2).sum(2)*ss[None,:]
    g=np.argmin(res,1)
    return res[np.arange(len(tr)),g]/len(t), ngrid[g]
V=np.load(f'V_{c}.npy')
r,n=fit_tracks(V,trall)
rms=np.sqrt(r)
# bins by x0
for lo in range(900,2500,200):
    s=(x0[:,0]>=lo)&(x0[:,0]<lo+200)
    if s.sum(): print('x0 in',lo,lo+200,'N',s.sum(),'rms med %.2f'%np.median(rms[s]),'n med %.0f'%np.median(n[s]))
# straight-line check: perpendicular deviation from each track's own best fit line
d=[]
for k in range(len(trall)):
    P=trall[k]-trall[k].mean(0); u,s_,vt=np.linalg.svd(P,full_matrices=False); d.append(s_[1]/np.sqrt(len(P)))
d=np.array(d); print('own-line perp rms median %.2f'%np.median(d))
