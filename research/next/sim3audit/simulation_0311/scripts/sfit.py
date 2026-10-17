import numpy as np, sys
vid = sys.argv[1]; ref = int(sys.argv[2]); norm = int(sys.argv[3]) if len(sys.argv)>3 else 54
T = np.load('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/tracks_%s_%d.npy' % (vid, ref))
nF, N, _ = T.shape
valid = ~np.isnan(T[:,:,0])
keep = valid.sum(0) >= 15
T = T[:, keep]; valid = valid[:, keep]; N = T.shape[1]
P = T[ref]
def vp_fit(T, valid):
    # each track: fit line by PCA; intersect lines (weighted LS)
    A=[];b=[]
    for k in range(T.shape[1]):
        pts = T[valid[:,k],k]
        if len(pts) < 10: continue
        mu = pts.mean(0); U,S,Vt = np.linalg.svd(pts-mu)
        n = Vt[1]
        w = np.linalg.norm(pts[-1]-pts[0])  # longer tracks weigh more
        A.append(n*w); b.append(n@mu*w)
    return np.linalg.lstsq(np.array(A), np.array(b), rcond=None)[0]
v = vp_fit(T, valid)
# perpendicular residuals of tracks w.r.t. lines through VP
perp=[]
for k in range(N):
    pts = T[valid[:,k],k]; d = P[k]-v; n = np.array([-d[1],d[0]])/np.linalg.norm(d)
    perp += list((pts-P[k])@n)
print('VP', v.round(1), 'perp rms px', np.sqrt(np.mean(np.square(perp))).round(3), 'Ntracks', N)
# ratio r_ki = s_i c_k : projection of (x-p) on (v-x) direction
R = np.full((nF,N), np.nan)
for i in range(nF):
    for k in range(N):
        if not valid[i,k]: continue
        x = T[i,k]; dvec = v - x
        R[i,k] = ((x-P[k])@dvec)/(dvec@dvec)
# rank-1 ALS: R ~ s_i c_k
c = np.ones(N); s = np.zeros(nF)
W = valid & (np.arange(nF)[:,None]!=ref)
for it in range(200):
    for i in range(nF):
        m = W[i]
        if m.sum(): s[i] = np.sum(R[i,m]*c[m])/np.sum(c[m]**2)
    for k in range(N):
        m = W[:,k]
        if m.sum(): c[k] = np.sum(R[m,k]*s[m])/np.sum(s[m]**2)
sc = s[norm]; s/=sc; c*=sc
res = np.where(W, R - s[:,None]*c[None], np.nan)
# convert residual to px approx
print('rank1 rel resid', np.nanstd(res)/np.nanstd(R))
np.save('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/s_%s_%d.npy'%(vid,ref), s)
np.save('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/vp_%s_%d.npy'%(vid,ref), v)
cnt = W.sum(1)
for i in range(nF):
    print(i, cnt[i], round(s[i],5))
