import numpy as np, cv2, sys
from sweep import E,C
from frame3d import axes
c=sys.argv[1]; win=sys.argv[2]
D=np.load(f'dense_{c}_{win}.npz')
q=D['qmap'];cm=D['cmin'];cv=D['curv'];x0=int(D['x0']);y0=int(D['y0']);sd=D['sd']
Mp=np.load('masks0303_packed.npy'); m=np.unpackbits(Mp[1])[:1440*2560].reshape(1440,2560)[y0:y0+q.shape[0],x0:x0+q.shape[1]]
md=cv2.dilate(m,np.ones((7,7),np.uint8))
good=(md>0)&(cm<0.25)&(cv>0.02)&(~D['edge'])&(sd>3)
print('good px',good.sum(),'of mask',m.sum())
# q image
qi=np.clip((q-0.0078)/(0.0096-0.0078),0,1)
col=cv2.applyColorMap((qi*255).astype(np.uint8),cv2.COLORMAP_JET)
col[~good]=(col[~good]*0.15).astype(np.uint8)
cv2.imwrite(f'fr/qmap_{c}.png',cv2.resize(col,None,fx=1.7,fy=1.7,interpolation=cv2.INTER_NEAREST))
f=3575; vzf=18.49/24; iref=24
V,S,U=axes(f)
ys,xs=np.nonzero(good)
qq=q[ys,xs].astype(float)
p=np.c_[xs+x0,ys+y0].astype(float)
s=(1+qq)/(1+qq*iref)
x=E+(p-E)*s[:,None]
Z=vzf*(1/qq+iref)
X=np.c_[(x[:,0]-C[0])*Z/f,(x[:,1]-C[1])*Z/f,Z]
np.save(f'dense3d_{c}.npy',np.c_[X,p,cm[ys,xs]])
