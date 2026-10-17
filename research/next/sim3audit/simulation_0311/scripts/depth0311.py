# route 2b: 0311's own rays + 0311's depth_info -> displacement between t=1 and t=2 (no motion model needed)
import numpy as np
base='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/'
vid='0311'; ref=30
T = np.load(base+'tracks_%s_%d.npy' % (vid, ref)); s = np.load(base+'s_%s_%d.npy'%(vid,ref)); v = np.load(base+'vp_%s_%d.npy'%(vid,ref))
vv = np.load(base+'vvp.npy')
nF,N,_ = T.shape; valid = ~np.isnan(T[:,:,0]); keep = valid.sum(0)>=15; T=T[:,keep]; valid=valid[:,keep]; N=T.shape[1]
P=T[ref]; idx=np.arange(nF); c=np.zeros(N)
for k in range(N):
    m=valid[:,k]&(idx!=ref); x=T[m,k]; d=v-x
    R=np.sum((x-P[k])*d,1)/np.sum(d*d,1); c[k]=np.sum(R*s[m])/np.sum(s[m]**2)
good=c>0.01
cx,cy=1280,720
r1s, r2s = 17.8278, 23.1989
for f in (3900,4150,4400):
    D=np.array([(v[0]-cx)/f,(v[1]-cy)/f,1.0]); D/=np.linalg.norm(D)
    Dn=np.array([(vv[0]-cx)/f,(vv[1]-cy)/f,1.0]); Dn/=np.linalg.norm(Dn)
    rays=np.stack([(P[:,0]-cx)/f,(P[:,1]-cy)/f,np.ones(N)],1)
    X0=(rays*(D[2]/c)[:,None])[good]
    proj=X0@D
    for delta in (0.0,0.1,0.2):
        for dz in (0.0, 0.05):
            Xc=X0.mean(0)+delta*D+dz*Dn
            out=[]
            for i1 in (23,24):
                r=Xc+s[i1]*D; r/=np.linalg.norm(r)
                b=r1s*(r@D); disc=b*b-(r1s**2-r2s**2)
                Delta=-b+np.sqrt(disc)
                out.append((i1, round(Delta,3), 'v1=',round(Delta-2.5-5/48,2),'v2=',round(Delta+2.5-5/48,2)))
            print('f',f,'shift fwd',delta,'down',dz,out)
