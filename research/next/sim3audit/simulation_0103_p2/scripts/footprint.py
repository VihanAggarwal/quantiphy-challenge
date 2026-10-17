import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from vhull import *
np.set_printoptions(precision=2,suppress=True)
MA=np.load('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/MA.npy'); MC=np.load('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/MC.npy')
def lower_boundary(M):
    H,W=M.shape; pts=[]
    for x in range(W):
        ys=np.where(M[:,x])[0]
        if len(ys): pts.append((x,ys.max()+0.5,ys.min()-0.5))
    return np.array(pts)
def to_ground(reg,u,v,zW):
    o=reg.to_W(reg.cam.C); d=reg.R@reg.cam.ray(u,v); t=(zW-o[2])/d[2]; return o+t*d
for prm in [dict(fA=3460,pA=18.7,fC=3870,pC=53.0),dict(fA=3401,pA=18.7,fC=3800,pC=53.0),dict(fA=3517,pA=18.7,fC=3950,pC=53.0),dict(fA=3460,pA=17.7,fC=3870,pC=51.0),dict(fA=3460,pA=19.7,fC=3870,pC=55.0)]:
    A,C=build(prm)
    out=[]
    for name,reg,M in [('A',A,MA),('C',C,MC)]:
        lb=lower_boundary(M)
        for zW in [1.1]:
            G=np.array([to_ground(reg,x,y,zW) for x,y,_ in lb])
            iL=np.argmin(G[:,0]); iR=np.argmax(G[:,0]); iN=np.argmax(G[:,1])
            out.append('%s: Xmin %.1f (Y%.1f) Xmax %.1f (Y%.1f) ext %.2f | nearest Y %.1f at X %.1f'%(name,G[iL,0],G[iL,1],G[iR,0],G[iR,1],G[iR,0]-G[iL,0],G[iN,1],G[iN,0]))
    print(prm); print('   ','\n    '.join(out))
