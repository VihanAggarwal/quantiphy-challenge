import numpy as np
base='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/'
vid='0311'; ref=30
T = np.load(base+'tracks_%s_%d.npy' % (vid, ref)); s = np.load(base+'s_%s_%d.npy'%(vid,ref)); v = np.load(base+'vp_%s_%d.npy'%(vid,ref))
vv = np.load(base+'vvp.npy')
nF,N,_ = T.shape; valid = ~np.isnan(T[:,:,0]); keep = valid.sum(0)>=15; T=T[:,keep]; valid=valid[:,keep]; N=T.shape[1]
P = T[ref]
def cfit(track_pts, frames, p):
    x = track_pts; dvec = v - x
    R = np.sum((x-p)*dvec,1)/np.sum(dvec*dvec,1)
    return np.sum(R*s[frames])/np.sum(s[frames]**2)
c = np.array([cfit(T[valid[:,k]&(np.arange(nF)!=ref),k], np.where(valid[:,k]&(np.arange(nF)!=ref))[0], P[k]) for k in range(N)])
good = c>0.01
cx, cy = 1280, 720
G30 = np.array([1480.,1250.]); G60 = np.array([915.,785.])
cG = cfit(G60[None], np.array([60]), G30)
print('cG', cG)
for f in (3900, 4150, 4400):
    D = np.array([(v[0]-cx)/f, (v[1]-cy)/f, 1.0]); D/=np.linalg.norm(D)
    Dn = np.array([(vv[0]-cx)/f, (vv[1]-cy)/f, 1.0]); Dn/=np.linalg.norm(Dn)  # down
    print('f',f,'D.down', round(D@Dn,4))
    ray = lambda p: np.array([(p[0]-cx)/f,(p[1]-cy)/f,1.0])
    X = np.array([ray(P[k])*D[2]/c[k] for k in range(N) if good[k]])   # in lambda units (Z = lam*Dz/c)
    XG = ray(G30)*D[2]/cG
    hcam = XG@Dn   # camera height above ground in lambda units
    h = hcam - X@Dn  # heights above ground
    print('  cam height (lam units)', round(hcam,3), 'feature heights min/med/max', h.min().round(3), np.median(h).round(3), np.percentile(h,98).round(3), h.max().round(3))
    lam = 1.15/np.percentile(h,99.5)
    print('  lam if top feature = 1.15m:', round(lam,3))
    # range of car centre at frame 24 in metres
    Xc = X.mean(0); Xc24 = Xc + s[24]*D  # in lam units: X(s) = X0 + s*D  (lam units per unit s)
    print('  centroid range frame24 (lam units)', round(np.linalg.norm(Xc24),3), '-> m', round(np.linalg.norm(Xc24)*lam,2), 'frame48', round(np.linalg.norm(Xc+s[48]*D)*lam,2))
