import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from vhull import *
MA=np.load('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/MA.npy'); MC=np.load('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/MC.npy')
A,C=build(dict(fA=3460,pA=18.7,fC=3870,pC=53.0))
g=0.5
xs=np.arange(-14,18,g); ys=np.arange(-64,-16,g); zs=np.arange(0,12,g)
X,Y,Z=np.meshgrid(xs,ys,zs,indexing='ij')
keep=carve([(A,MA),(C,MC)],(X,Y,Z),keep_right=[True,False])
# YZ profile: for each Y, max z over X ; also per-Y X-extent at z=1.5
print('Y    zmax  Xext@z1.5  Xext@z4')
for j in range(0,len(ys),2):
    col=keep[:,j,:]
    zz=np.where(col.any(0))[0]
    zmax=zs[zz].max() if len(zz) else None
    def xe(zv):
        k=np.argmin(abs(zs-zv)); xx=np.where(col[:,k])[0]
        return (xs[xx].min(),xs[xx].max()) if len(xx) else None
    print(ys[j],zmax,xe(1.5),xe(4.0))
# top view at z=1.5: Y-extent per X
print('X   Yext@z1.5')
k=np.argmin(abs(zs-1.5))
for i in range(0,len(xs),2):
    yy=np.where(keep[i,:,k])[0]; print(xs[i],(ys[yy].min(),ys[yy].max()) if len(yy) else None)
