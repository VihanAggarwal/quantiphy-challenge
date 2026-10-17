import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from vhull import *
np.set_printoptions(precision=2,suppress=True)
B='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/'
MA=np.load(B+'MA.npy'); MC=np.load(B+'MC.npy'); M22=np.load(B+'M22.npy')
def run(prm,g=0.4,zfloor=None,verbose=False):
    A,C=build(prm)
    R22=Reg(prm['f22'],480,480,prm['p22'],prm['b1'],(753.9,638.6),148.7451,146.9726)
    xs=np.arange(-16,20,g); ys=np.arange(-66,-14,g); zs=np.arange(-4,14,g)
    X,Y,Z=np.meshgrid(xs,ys,zs,indexing='ij')
    views=[(A,MA),(C,MC),(R22,M22)]
    keep=carve(views,(X,Y,Z),keep_right=[True,False,False])
    ii=np.where(keep)
    if len(ii[0])==0: return None
    x0,x1=xs[ii[0]].min(),xs[ii[0]].max(); y0,y1=ys[ii[1]].min(),ys[ii[1]].max(); z0,z1=zs[ii[2]].min(),zs[ii[2]].max()
    out=dict(X=(x0,x1,x1-x0+g),Y=(y0,y1,y1-y0+g),Z=(z0,z1,z1-z0+g),nvox=len(ii[0]))
    if zfloor is not None:
        k=keep&(Z>=zfloor); jj=np.where(k)
        out['Xf']=xs[jj[0]].max()-xs[jj[0]].min()+g; out['Yf']=ys[jj[1]].max()-ys[jj[1]].min()+g; out['Hf']=zs[jj[2]].max()-zfloor+g
    return out
base=dict(fA=3460,pA=18.7,fC=3870,pC=53.0,f22=4513,p22=-1.25,b1=(864,638))
if __name__=='__main__':
    for ch in [{},dict(f22=4347,b1=(860,638)),dict(f22=4625,b1=(866.3,638.6)),dict(p22=-1.76),dict(p22=-0.5),dict(fA=3401,fC=3800),dict(fA=3517,fC=3950),dict(pA=17.7,pC=51.0),dict(pA=19.7,pC=55.0)]:
        prm=dict(base); prm.update(ch)
        r=run(prm,zfloor=1.1)
        print(ch, {k:(np.round(v,2) if not isinstance(v,int) else v) for k,v in r.items()} if r else None)
