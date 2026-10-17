import cv2, numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from track import *; from reg import *
def rockmask(clip,frame,cut_y=None,cut_below=True):
    im=frames(clip,[frame])[frame]; m=fgmask(im)
    if cut_y is not None:
        if cut_below: m[cut_y:]=False
        else: m[:cut_y]=False
    n,l,st,cen=cv2.connectedComponentsWithStats(m.astype(np.uint8))
    k=1+np.argmax(st[1:,4]); return (l==k)
def build(params):
    fA,pA,fC,pC=params['fA'],params['pA'],params['fC'],params['pC']
    A=Reg(fA,480,480,pA,(616.6,585.2),(616.6-155.43,585.2-6.03),90.1103,90.4360)
    C=Reg(fC,540,540,pC,(359.2,925.3),(359.2-85.73,925.3-24.81),173.7093,174.5515)
    return A,C
def carve(regs_masks,grid,keep_right=None):
    X,Y,Z=grid; P=np.stack([X.ravel(),Y.ravel(),Z.ravel()],1)
    keep=np.ones(len(P),bool)
    for j,(reg,M) in enumerate(regs_masks):
        Pk=(reg.R.T@P.T).T+reg.B1   # world-k coords
        d=Pk-reg.cam.C; x=d@reg.cam.xc; y=-(d@reg.cam.uc); z=d@reg.cam.fc
        u=reg.cam.cx+reg.cam.f*x/z; v=reg.cam.cy+reg.cam.f*y/z
        H,W=M.shape; ui=np.round(u).astype(int); vi=np.round(v).astype(int)
        inside=(ui>=0)&(ui<W)&(vi>=0)&(vi<H)
        ok=np.zeros(len(P),bool)   # outside image -> carve, except declared open borders
        if keep_right is not None and keep_right[j]:
            ok[(ui>=W)&(vi>=0)&(vi<H)]=True
        ok[inside]=M[vi[inside],ui[inside]]
        keep&=ok
    return keep.reshape(X.shape)
