import numpy as np, sys, cv2
from masks import load
c=sys.argv[1]
fr=load(c)
tr=np.load(f'tracks_{c}.npy').astype(np.float64)[:,1:]
t=np.arange(tr.shape[1]).astype(float)
ngrid=np.exp(np.linspace(np.log(50),np.log(6000),300))
S=ngrid[:,None]/(ngrid[:,None]+t[None,:]); ss=(S*S).sum(1)
V=np.load(f'V_{c}.npy')
X=tr-V
A=np.einsum('gt,ntk->ngk',S,X)/ss[None,:,None]
res=(X**2).sum((1,2))[:,None]-(A**2).sum(2)*ss[None,:]
g=np.argmin(res,1); rms=np.sqrt(res[np.arange(len(tr)),g]/len(t))
img=fr[1].copy()
for k in range(len(tr)):
    col=(0,255,0) if rms[k]<1.5 else ((0,255,255) if rms[k]<5 else (0,0,255))
    cv2.polylines(img,[tr[k].astype(np.int32)],False,col,2)
    cv2.circle(img,tuple(tr[k,0].astype(int)),4,col,-1)
x0,y0,x1,y1=700,250,1900,1350
cv2.imwrite(f'frames/tracks_{c}.png',img[y0:y1,x0:x1])
