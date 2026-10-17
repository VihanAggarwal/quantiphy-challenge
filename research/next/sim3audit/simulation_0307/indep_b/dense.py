import numpy as np, cv2, sys
from sweep import gray, E, C
c=sys.argv[1]; win=int(sys.argv[2]) if len(sys.argv)>2 else 15
G=gray(c)
x0,y0,x1,y1=1300,680,2040,1030
ref=1
A=G[ref][y0:y1,x0:x1]
qs=np.linspace(0.0072,0.0102,121)
frs=list(range(3,72,3))
k=(win,win)
def bx(a): return cv2.boxFilter(a,-1,k,normalize=True,borderType=cv2.BORDER_REFLECT)
mA=bx(A); vA=bx(A*A)-mA*mA
cost=np.zeros((len(qs),)+A.shape,np.float32)
for qi,q in enumerate(qs):
    acc=np.zeros(A.shape,np.float32)
    for i in frs:
        s=(1+q*ref)/(1+q*i)
        # map frame-1 coords u -> frame i: e + (u-e)*s ; with ROI offset
        M=np.array([[s,0,E[0]*(1-s)+s*x0],[0,s,E[1]*(1-s)+s*y0]],np.float32)
        B=cv2.warpAffine(G[i],M,(A.shape[1],A.shape[0]),flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP)
        mB=bx(B); vB=bx(B*B)-mB*mB; cAB=bx(A*B)-mA*mB
        ncc=cAB/np.sqrt(np.maximum(vA*vB,1e-3))
        acc+=1-ncc
    cost[qi]=acc/len(frs)
kbest=np.argmin(cost,0)
cmin=np.min(cost,0)
# subsample-level refine
kk=np.clip(kbest,1,len(qs)-2)
a=np.take_along_axis(cost,(kk-1)[None],0)[0]; b=np.take_along_axis(cost,kk[None],0)[0]; cc=np.take_along_axis(cost,(kk+1)[None],0)[0]
den=a-2*b+cc; d=np.where(den>1e-6,0.5*(a-cc)/np.maximum(den,1e-6),0)
qmap=qs[kk]+np.clip(d,-1,1)*(qs[1]-qs[0])
# sharpness: second difference
np.savez_compressed(f'dense_{c}_{win}.npz',qmap=qmap.astype(np.float32),cmin=cmin.astype(np.float32),curv=den.astype(np.float32),edge=(kbest==0)|(kbest==len(qs)-1),x0=x0,y0=y0,sd=np.sqrt(np.maximum(vA,0)).astype(np.float32))
print('done',c,qmap.shape)
