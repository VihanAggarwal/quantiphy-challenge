import numpy as np, cv2, sys
from sweep import sweep, to3d
from frame3d import axes
Mp=np.load('masks0303_packed.npy'); m=np.unpackbits(Mp[1])[:1440*2560].reshape(1440,2560)
cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
cnt=max(cs,key=len)[:,0,:]
pts=cnt[::4]
print('contour pts',len(pts))
res=[]
qs=np.linspace(0.0074,0.0100,105)
for p in pts:
    q3,c3,_=sweep('0303',p,r=8,qs=qs,fr=list(range(2,72,2)))
    q5,c5,_=sweep('0305',p,r=8,qs=qs,fr=list(range(2,72,2)))
    res.append((p[0],p[1],q3,c3,q5,c5))
np.save('contour_sweep.npy',np.array(res))
