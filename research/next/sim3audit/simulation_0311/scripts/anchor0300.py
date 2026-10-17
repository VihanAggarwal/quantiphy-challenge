# depth-anchored acceleration for the sibling 0300 car (independent of the a=5 prior)
import numpy as np
base='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/'
vid='0300'; ref=40
T = np.load(base+'tracks_%s_%d.npy' % (vid, ref)); s = np.load(base+'s_%s_%d.npy'%(vid,ref)); v = np.load(base+'vp_%s_%d.npy'%(vid,ref))
nF,N,_ = T.shape; valid = ~np.isnan(T[:,:,0]); keep = valid.sum(0)>=15; T=T[:,keep]; valid=valid[:,keep]; N=T.shape[1]
P = T[ref]
idx = np.arange(nF)
c = np.zeros(N)
for k in range(N):
    m = valid[:,k]&(idx!=ref); x=T[m,k]; d=v-x
    R=np.sum((x-P[k])*d,1)/np.sum(d*d,1); c[k]=np.sum(R*s[m])/np.sum(s[m]**2)
good = c>0.01
# quadratic fit of s(i): s = A*(i-i0)^2 + B
ii = idx[(idx>=3)]; A_ = np.polyfit(ii, s[ii], 2); print('s(i) quad coeffs', A_, 'vertex at i=', -A_[1]/(2*A_[0]))
acc_units = 2*A_[0]*576   # units / s^2
cx,cy=1280,720
for f in (3450, 3556, 3650):
    D=np.array([(v[0]-cx)/f,(v[1]-cy)/f,1.0]); D/=np.linalg.norm(D)
    rays=np.stack([(P[:,0]-cx)/f,(P[:,1]-cy)/f,np.ones(N)],1)
    X0 = rays*(D[2]/c)[:,None]       # positions at s=0 (frame 40), units
    X0 = X0[good]
    lo, hi = X0.min(0), X0.max(0)
    # centroid of tracked features
    for name, Xc in (('feat-centroid', X0.mean(0)),):
        for (i1,i2) in ((24,48),(23,47)):
            r1=np.linalg.norm(Xc+s[i1]*D); r2=np.linalg.norm(Xc+s[i2]*D)
            mpu = 17.8278/r1
            print('f',f,name,(i1,i2),'ratio',round(r2/r1,4),'target 1.3013','m/unit',round(mpu,3),'-> a =',round(acc_units*mpu,3), ' (using r2:', round(acc_units*23.1989/r2,3),')')
print('--- shift reference point forward along motion by delta units (body centre is ahead of rear features)')
f=3556
D=np.array([(v[0]-cx)/f,(v[1]-cy)/f,1.0]); D/=np.linalg.norm(D)
rays=np.stack([(P[:,0]-cx)/f,(P[:,1]-cy)/f,np.ones(N)],1)
X0=(rays*(D[2]/c)[:,None])[good]
# extent of features along D
proj = X0@D
print('feature extent along D (units)', round(proj.max()-proj.min(),3), 'centroid offset from rearmost', round(X0.mean(0)@D - proj.min(),3))
for delta in (0.0,0.05,0.1,0.15,0.2):
    Xc = X0.mean(0)+delta*D
    for (i1,i2) in ((24,48),(23,47)):
        r1=np.linalg.norm(Xc+s[i1]*D); r2=np.linalg.norm(Xc+s[i2]*D)
        print(delta,(i1,i2),'ratio',round(r2/r1,4),'a(r1)',round(acc_units*17.8278/r1,3),'a(r2)',round(acc_units*23.1989/r2,3))
