import cv2, numpy as np, json, sys
sys.path.insert(0,'scripts')
from geo import *
def binmask(n):
    im=cv2.imread(f'frames/x_{n:02d}.png').astype(int)
    m=(~((im[...,1]>200)&(im[...,2]<80)&(im[...,0]<80))).astype(np.uint8)
    m[690:,1000:]=0
    k,lab,st,cen=cv2.connectedComponentsWithStats(m)
    cand=[i for i in range(1,k) if st[i][4]>4000 and not (abs(cen[i][0]-986)<6 and abs(cen[i][1]-370)<6)]
    i=max(cand,key=lambda i:st[i][4])
    return lab==i, cen[i]
rows=[]
for n in range(0,48):
    m,c=binmask(n)
    ys,xs=np.nonzero(m)
    cov=np.cov(np.c_[xs,ys].T); ev=np.sqrt(np.linalg.eigvalsh(cov))
    rows.append((n,c[0],c[1],m.sum(),ev[0],ev[1],xs.max()-xs.min()+1,ys.max()-ys.min()+1))
R=np.array(rows)
np.save('binsize.npy',R)
def avg(ns,col): return R[ns,col].mean()
a=[9,10,11]; b=[33,34,35]
for col,name in [(3,'sqrt area'),(4,'minor sd'),(5,'major sd'),(6,'bbox w'),(7,'bbox h')]:
    ra=avg(a,col); rb=avg(b,col)
    k=ra/rb if col!=3 else np.sqrt(ra/rb)
    print('%-10s ratio n10/n34 %.4f -> r34 = %.3f'%(name,k,2.73*k))
# plus: correct for off-axis: apparent size ~ 1/range * (angle factor); compute ray angles
for n in (10,34):
    r=ray(R[n,1],R[n,2]); print(n,'ray z-cos %.4f'%r[2])
