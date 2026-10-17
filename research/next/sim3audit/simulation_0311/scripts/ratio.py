import numpy as np, sys
vid = sys.argv[1]; ref = int(sys.argv[2]); norm = int(sys.argv[3])
base='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/'
T = np.load(base+'tracks_%s_%d.npy' % (vid, ref)); s = np.load(base+'s_%s_%d.npy'%(vid,ref)); v = np.load(base+'vp_%s_%d.npy'%(vid,ref))
nF,N,_ = T.shape; valid = ~np.isnan(T[:,:,0]); keep = valid.sum(0)>=15; T=T[:,keep]; valid=valid[:,keep]; N=T.shape[1]
P = T[ref]
# recompute c_k by LS on R = s c
c = np.zeros(N)
for k in range(N):
    m = valid[:,k] & (np.arange(nF)!=ref)
    x = T[m,k]; dvec = v - x
    R = np.sum((x-P[k])*dvec,1)/np.sum(dvec*dvec,1)
    c[k] = np.sum(R*s[m])/np.sum(s[m]**2)
cx, cy = 1280, 720
target = float(sys.argv[4]) if len(sys.argv)>4 else 23.1989/17.8278
for f in (3300, 3556, 3800, 4000, 4200, 4400):
    D = np.array([(v[0]-cx)/f, (v[1]-cy)/f, 1.0]); D/=np.linalg.norm(D)
    out=[]
    for (i1,i2) in ((24,48),(23,47)):
        rays = np.stack([(P[:,0]-cx)/f, (P[:,1]-cy)/f, np.ones(N)],1)
        X1 = rays + (s[i1]*c/D[2])[:,None]*D[None]
        X2 = rays + (s[i2]*c/D[2])[:,None]*D[None]
        r = np.linalg.norm(X2,axis=1)/np.linalg.norm(X1,axis=1)
        out.append((i1, r.min().round(4), np.median(r).round(4), r.max().round(4)))
    print('f',f, out, 'target', round(target,4))
