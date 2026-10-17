import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0038_segmented.mp4')
cap.set(cv2.CAP_PROP_POS_FRAMES,30); ok,f=cap.read()
g=f.astype(np.int16); m=((255-g.min(axis=2))>30).astype(np.uint8)
n,lab,st,cen=cv2.connectedComponentsWithStats(m)
k=1+np.argmax(st[1:,4]); rock=(lab==k)
ys,xs=np.nonzero(rock)
print('bbox',xs.min(),xs.max(),ys.min(),ys.max())
print('leftmost pt rows', ys[xs==xs.min()].min(), ys[xs==xs.min()].max(), 'rightmost rows', ys[xs==xs.max()].min(), ys[xs==xs.max()].max())
print('top pt cols', xs[ys==ys.min()].min(), xs[ys==ys.min()].max(), 'bottom pt cols', xs[ys==ys.max()].min(), xs[ys==ys.max()].max())
cnt,_=cv2.findContours(rock.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
c=max(cnt,key=len)[:,0,:].astype(float)
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/rock38_contour.npy',c)
cx=cy=767.5
def model(R=179.1,k=33.7,delta=np.radians(49.3),pv=(492.5,812.0),pel=0.95):
    f=k*R
    a=delta-np.arctan((pv[1]-cy)/f)
    H=pel+R*np.sin(delta)
    return f,a,H
def ground(u,v,f,a,H,z0=0.0):
    d=np.array([0,np.cos(a),-np.sin(a)]); xc=np.array([1,0,0]); yd=np.array([0,-np.sin(a),-np.cos(a)])
    r=d[None,:]+((u-cx)/f)[:,None]*xc[None,:]+((v-cy)/f)[:,None]*yd[None,:]
    t=(z0-H)/r[:,2]
    P=np.array([0,0,H])[None,:]+t[:,None]*r
    return P
for R in (160,179.1,200):
  for kk in (32.5,33.7,35.0):
    f,a,H=model(R=R,k=kk)
    # person ground positions check
    out=[]
    for z0 in (0,2,4,6):
        P=ground(c[:,0],c[:,1],f,a,H,z0)
        out.append((z0, P[:,0].max()-P[:,0].min(), P[:,1].max()-P[:,1].min()))
    # also mixed: bottom (near) part at z=0, top part at z=zt
    print(f'R={R} k={kk} f={f:.0f} a={np.degrees(a):.1f} H={H:.1f}', ' '.join(f'z{z}: X{x:.1f} Y{y:.1f}' for z,x,y in out))
