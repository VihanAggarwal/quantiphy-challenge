import numpy as np
c=np.load('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/rock38_contour.npy')
cx=cy=767.5
def model(R=179.1,k=33.7,delta=np.radians(49.3),pv=(492.5,812.0),pel=0.95):
    f=k*R; a=delta-np.arctan((pv[1]-cy)/f); H=pel+R*np.sin(delta); return f,a,H
def ground(u,v,f,a,H,z0):
    u=np.atleast_1d(u).astype(float); v=np.atleast_1d(v).astype(float); z0=np.broadcast_to(z0,u.shape)
    d=np.array([0,np.cos(a),-np.sin(a)]); xc=np.array([1,0,0]); yd=np.array([0,-np.sin(a),-np.cos(a)])
    r=d[None,:]+((u-cx)/f)[:,None]*xc[None,:]+((v-cy)/f)[:,None]*yd[None,:]
    t=(z0-H)/r[:,2]; return np.array([0,0,H])[None,:]+t[:,None]*r
iL=np.argmin(c[:,0]); iR=np.argmax(c[:,0]); pL=c[iL]; pR=c[iR]
side=(c[:,1]-(pL[1]+(c[:,0]-pL[0])*(pR[1]-pL[1])/(pR[0]-pL[0])))
# 0037 measurements (frame 24 ~ t=1): person x, rock ends
x_p37=838.0; x_R37=715.0; x_L37=15.0; kp37=None
for k in (32.5,33.7,35.0):
  f,a,H=model(k=k)
  Pp=ground(494.0,850.5,f,a,H,0.0)[0]
  for zf in (0,2,4):
    z=np.where(side>0,0.0,zf)
    P=ground(c[:,0],c[:,1],f,a,H,z)[:,:2]-Pp[:2]
    best=[]
    for th in np.arange(-40,41,2):
        t=np.radians(th); fwd=np.array([np.cos(t),np.sin(t)]); right=np.array([np.sin(t),-np.cos(t)])
        lat=P@right; dep=P@fwd
        for Zp in (122.86,):
          for kp in (33.0,34.3,35.5):
            # pixel x relative to person: kp*Zp*lat/(Zp+dep)
            xr=x_p37+kp*Zp*lat/(Zp+dep)
            best.append((th,kp,xr.min(),xr.max(),dep[np.argmin(xr)],dep[np.argmax(xr)],dep.mean()))
    B=np.array(best)
    err=np.abs(B[:,2]-x_L37)+np.abs(B[:,3]-x_R37)
    o=np.argsort(err)[:3]
    for i in o:
        th,kp,xl,xr,dl,dr,dm=B[i]
        print(f'k38={k} zfar={zf} th={th:+.0f} kp37={kp} pred L={xl:.0f} R={xr:.0f} (meas 15,715) err={err[i]:.0f} depth L={dl:+.1f} R={dr:+.1f} mean={dm:+.1f}')
