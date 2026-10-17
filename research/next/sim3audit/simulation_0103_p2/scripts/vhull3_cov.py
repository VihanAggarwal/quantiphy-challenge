import numpy as np, sys, cv2
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from vhull import *
from vhull3 import base, MA, MC, M22
def proj(reg,P):
    Pk=(reg.R.T@P.T).T+reg.B1; d=Pk-reg.cam.C; x=d@reg.cam.xc; y=-(d@reg.cam.uc); z=d@reg.cam.fc
    return reg.cam.cx+reg.cam.f*x/z, reg.cam.cy+reg.cam.f*y/z
def coverage(prm,g=0.3,tag=''):
    A,C=build(prm); R22=Reg(prm['f22'],480,480,prm['p22'],prm['b1'],(753.9,638.6),148.7451,146.9726)
    xs=np.arange(-16,20,g); ys=np.arange(-66,-14,g); zs=np.arange(-4,14,g)
    X,Y,Z=np.meshgrid(xs,ys,zs,indexing='ij')
    views=[(A,MA),(C,MC),(R22,M22)]
    keep=carve(views,(X,Y,Z),keep_right=[True,False,False])
    P=np.stack([X[keep],Y[keep],Z[keep]],1)
    res=[]
    for name,(reg,M) in zip(['A','C','22'],views):
        u,v=proj(reg,P); H,W=M.shape
        img=np.zeros_like(M,dtype=np.uint8)
        ok=(u>=0)&(u<W)&(v>=0)&(v<H)
        ui=np.round(u[ok]).astype(int); vi=np.round(v[ok]).astype(int); img[vi,ui]=1
        img=cv2.dilate(img,np.ones((5,5),np.uint8))
        cov=(img.astype(bool)&M).sum()/M.sum()
        # which rows uncovered
        unc=M&~img.astype(bool); yy,xx=np.where(unc)
        res.append('%s cov %.3f uncovered rows %s'%(name,cov,(np.percentile(yy,[5,50,95]).round() if len(yy) else None)))
        cv2.imwrite('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/frames/cov_%s%s.png'%(name,tag),(np.stack([M*255,img*255,np.zeros_like(img)],2)).astype(np.uint8))
    print(prm if not tag else tag,' | '.join(res))
coverage(base,tag='base')
