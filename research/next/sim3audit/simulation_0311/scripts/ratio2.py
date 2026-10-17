import numpy as np, sys
base='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/'
vid='0311'; ref=30
T = np.load(base+'tracks_%s_%d.npy' % (vid, ref)); s = np.load(base+'s_%s_%d.npy'%(vid,ref)); v = np.load(base+'vp_%s_%d.npy'%(vid,ref))
nF,N,_ = T.shape; valid = ~np.isnan(T[:,:,0]); keep = valid.sum(0)>=15; T=T[:,keep]; valid=valid[:,keep]; N=T.shape[1]
P = T[ref]
c = np.zeros(N)
for k in range(N):
    m = valid[:,k] & (np.arange(nF)!=ref)
    x = T[m,k]; dvec = v - x
    R = np.sum((x-P[k])*dvec,1)/np.sum(dvec*dvec,1)
    c[k] = np.sum(R*s[m])/np.sum(s[m]**2)
good = c > 0.01
# linear s model
sl = lambda i: (i-30)/24.0
cx, cy, f = 1280, 720, 4200
D = np.array([(v[0]-cx)/f, (v[1]-cy)/f, 1.0]); D/=np.linalg.norm(D)
rays = np.stack([(P[:,0]-cx)/f, (P[:,1]-cy)/f, np.ones(N)],1)[good]
cc = c[good]
for i1 in range(-24, 48, 4):
    X1 = rays + (sl(i1)*cc/D[2])[:,None]*D[None]; X2 = rays + (sl(i1+24)*cc/D[2])[:,None]*D[None]
    r = np.linalg.norm(X2,axis=1)/np.linalg.norm(X1,axis=1)
    print(i1, r.min().round(3), np.median(r).round(3), r.max().round(3))
