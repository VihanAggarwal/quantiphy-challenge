import numpy as np
tr=np.load('tracks_0304.npy').astype(np.float64)   # frames 0..71
t=np.arange(1,72).astype(float)
V=np.load('V_0304.npy')
X=tr[:,1:]-V
ngrid=np.exp(np.linspace(np.log(50),np.log(8000),800))
tt=t-1
S=ngrid[:,None]/(ngrid[:,None]+tt[None,:]); ss=(S*S).sum(1)
A=np.einsum('gt,ntk->ngk',S,X)/ss[None,:,None]
res=(X**2).sum((1,2))[:,None]-(A**2).sum(2)*ss[None,:]
g=np.argmin(res,1); rms=np.sqrt(res[np.arange(len(tr)),g]/len(t))
good=rms<1.0
# mean head displacement per frame (image) along the track direction
D=tr[good,1:]-tr[good,1:2]
d=np.mean(D[:,-1],0); d/=np.linalg.norm(d)
s=np.mean(D@d,0)
v=np.diff(s)
print('good',good.sum())
for a,b in ((1,12),(12,24),(24,36),(36,48),(48,60),(60,71)):
    print('frames %2d-%2d mean image speed %.3f px/frame'%(a,b,(s[b-1]-s[a-1])/(b-a)))
# residual from model per frame-block (signed, along d)
Ag=A[np.arange(len(tr)),g]; ng=ngrid[g]
pred=Ag[:,None,:]*(ng[:,None]/(ng[:,None]+tt[None,:]))[:,:,None]
e=((X-pred)@d)[good].mean(0)
print('mean signed residual along track (px) every 6 frames:',np.round(e[::6],2))
