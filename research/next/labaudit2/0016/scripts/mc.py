# MC of the label v(1.5): click jitter sigma_px, ToF noise sigma_tof on the unknown next/previous reading.
import numpy as np
rng=np.random.default_rng(0)
f=711.; pp=np.array([640.,360.])
def rays(P):
    v=np.c_[P[:,0]-pp[0],P[:,1]-pp[1],np.full(len(P),f)]; return v/np.linalg.norm(v,axis=1)[:,None]
N=200000
c36=np.array([812.2,77.2]); c37v=np.array([844.7,70.3]); c37=np.array([775.,96.])
for sp in [2.,3.]:
  for st in [0.01,0.02,0.03]:
    out=[]
    for conv in 'AB':
        for rmean in [1.46,1.47,1.48]:
            j1=rng.normal(0,sp,(N,2)); j2=rng.normal(0,sp,(N,2))
            r=rmean+rng.normal(0,st,N)
            if conv=='A': Q1=1.402*rays(c36+j1); Q2=r[:,None]*rays(c37v+j2)
            else: Q1=1.402*rays(c37+j1); Q2=r[:,None]*rays(c36+j2)
            v=25*np.linalg.norm(Q2-Q1,axis=1)
            out.append('%s r=%.2f med %.2f [p25 %.2f p75 %.2f]'%(conv,rmean,np.median(v),*np.percentile(v,[25,75])))
    print('click %.0fpx tof %.0fcm: '%(sp,100*st)+' | '.join(out))
