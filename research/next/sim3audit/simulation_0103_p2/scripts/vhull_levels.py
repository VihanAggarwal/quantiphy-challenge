import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from vhull import *
from vhull3 import base, MA, MC, M22
g=0.25
for ch in [{}, dict(p22=-1.76), dict(fA=3401,fC=3800), dict(fA=3517,fC=3950)]:
    prm=dict(base); prm.update(ch)
    A,C=build(prm); R22=Reg(prm['f22'],480,480,prm['p22'],prm['b1'],(753.9,638.6),148.7451,146.9726)
    xs=np.arange(-14,18,g); ys=np.arange(-66,-20,g); zs=np.arange(-3,7,g)
    X,Y,Z=np.meshgrid(xs,ys,zs,indexing='ij')
    keep=carve([(A,MA),(C,MC),(R22,M22)],(X,Y,Z),keep_right=[True,False,False])
    print(ch)
    for k in range(0,len(zs),2):
        sl=keep[:,:,k]
        if not sl.any(): continue
        ii=np.where(sl)
        print('  z %.2f  X %.1f..%.1f (%.1f)  Y %.1f..%.1f (%.1f)  area %.0f'%(zs[k],xs[ii[0]].min(),xs[ii[0]].max(),xs[ii[0]].max()-xs[ii[0]].min()+g,ys[ii[1]].min(),ys[ii[1]].max(),ys[ii[1]].max()-ys[ii[1]].min()+g,sl.sum()*g*g))
