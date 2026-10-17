import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from vhull import *
from footprint import lower_boundary, to_ground
MA=np.load('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/MA.npy'); MC=np.load('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/MC.npy')
for prm in [dict(fA=3460,pA=18.7,fC=3870,pC=53.0),dict(fA=3401,pA=18.7,fC=3800,pC=53.0),dict(fA=3517,pA=18.7,fC=3950,pC=53.0),dict(fA=3460,pA=17.7,fC=3870,pC=51.0),dict(fA=3460,pA=19.7,fC=3870,pC=55.0)]:
    A,C=build(prm)
    lbA=lower_boundary(MA); lbC=lower_boundary(MC)
    print(prm)
    for zW in [1.1,2.0,2.5,3.0]:
        r=[]
        for name,reg,lb in [('A',A,lbA),('C',C,lbC)]:
            G=np.array([to_ground(reg,x,y,zW) for x,y,_ in lb])
            iL=np.argmin(G[:,0]); iR=np.argmax(G[:,0]); iN=np.argmax(G[:,1])
            r.append('%s X[%.1f,%.1f]=%.2f Yl %.1f Yr %.1f Ynear %.1f'%(name,G[iL,0],G[iR,0],G[iR,0]-G[iL,0],G[iL,1],G[iR,1],G[iN,1]))
        print('  z=%.1f  '%zW+'  ||  '.join(r))
