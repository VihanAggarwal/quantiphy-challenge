import numpy as np
c=np.load('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/rock38_contour.npy')
cx=cy=767.5
def model(R=179.1,k=33.7,delta=np.radians(49.3),pv=(492.5,812.0),pel=0.95):
    f=k*R; a=delta-np.arctan((pv[1]-cy)/f); H=pel+R*np.sin(delta); return f,a,H
def ground(u,v,f,a,H,z0):
    d=np.array([0,np.cos(a),-np.sin(a)]); xc=np.array([1,0,0]); yd=np.array([0,-np.sin(a),-np.cos(a)])
    r=d[None,:]+((u-cx)/f)[:,None]*xc[None,:]+((v-cy)/f)[:,None]*yd[None,:]
    t=(z0-H)/r[:,2]; return np.array([0,0,H])[None,:]+t[:,None]*r
# split near/far by line joining leftmost and rightmost points
iL=np.argmin(c[:,0]); iR=np.argmax(c[:,0])
pL=c[iL]; pR=c[iR]
side=(c[:,1]-(pL[1]+(c[:,0]-pL[0])*(pR[1]-pL[1])/(pR[0]-pL[0])))  # >0 below line = near
for k in (32.5,33.7,35.0):
  f,a,H=model(k=k)
  for zf in (0,2,4,6):
    z=np.where(side>0,0.0,zf)
    P=np.vstack([ground(c[i:i+1,0],c[i:i+1,1],f,a,H,z[i]) for i in range(len(c))])
    th=np.radians(np.arange(0,180,5))
    E=[np.ptp(P[:,0]*np.cos(t)+P[:,1]*np.sin(t)) for t in th]
    E=np.array(E)
    # AABB pairs
    pairs=[(E[i],E[(i+18)%36]) for i in range(18)]
    print(f'k={k} zfar={zf}: E(0)={E[0]:.1f} E(90)={E[18]:.1f} Emin={E.min():.1f}@{np.degrees(th[E.argmin()]):.0f} Emax={E.max():.1f}@{np.degrees(th[E.argmax()]):.0f}')
    if k==33.7: print('   E by 15deg:', ' '.join(f'{int(np.degrees(t))}:{e:.1f}' for t,e in zip(th[::3],E[::3])))
