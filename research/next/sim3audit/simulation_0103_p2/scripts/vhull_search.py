import numpy as np, sys, cv2, itertools
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from vhull import *
from vhull3 import base, MA, MC, M22
from vhull3_cov import proj
def evalp(prm,g=0.4):
    A,C=build(prm); R22=Reg(prm['f22'],480,480,prm['p22'],prm['b1'],(753.9,prm['b1'][1]+0.6),148.7451,146.9726)
    xs=np.arange(-16,20,g); ys=np.arange(-68,-14,g); zs=np.arange(-5,14,g)
    X,Y,Z=np.meshgrid(xs,ys,zs,indexing='ij')
    views=[(A,MA),(C,MC),(R22,M22)]
    keep=carve(views,(X,Y,Z),keep_right=[True,False,False])
    if keep.sum()==0: return None
    P=np.stack([X[keep],Y[keep],Z[keep]],1)
    covs=[]
    for reg,M in views:
        u,v=proj(reg,P); H,W=M.shape; img=np.zeros(M.shape,np.uint8)
        ok=(u>=0)&(u<W)&(v>=0)&(v<H); img[np.round(v[ok]).astype(int).clip(0,H-1),np.round(u[ok]).astype(int).clip(0,W-1)]=1
        img=cv2.dilate(img,np.ones((5,5),np.uint8)); covs.append((img.astype(bool)&M).sum()/M.sum())
    ii=np.where(keep)
    ext=[xs[ii[0]].max()-xs[ii[0]].min()+g, ys[ii[1]].max()-ys[ii[1]].min()+g, zs[ii[2]].max()-zs[ii[2]].min()+g]
    return covs,ext,(zs[ii[2]].min(),zs[ii[2]].max()),(ys[ii[1]].min(),ys[ii[1]].max())
rows=[]
for p22,f22,pA,by in itertools.product([-2.2,-1.25,-0.3],[4400,4600],[17.7,18.7,19.7],[600,638]):
    prm=dict(base); prm.update(p22=p22,f22=f22,pA=pA,b1=(864,by))
    r=evalp(prm)
    if r is None: print(p22,f22,pA,by,'EMPTY'); continue
    covs,ext,zr,yr=r
    print('p22 %.2f f22 %d pA %.1f by %d | cov A %.3f C %.3f 22 %.3f min %.3f | ext X %.1f Y %.1f Z %.1f | z %.1f..%.1f  Y %.1f..%.1f'%(p22,f22,pA,by,*covs,min(covs),*ext,*zr,*yr))
