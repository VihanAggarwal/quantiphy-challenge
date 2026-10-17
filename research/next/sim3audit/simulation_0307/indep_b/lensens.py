import numpy as np
from frame3d import axes
from sweep import to3d, E
import sweep
pts={'Lpod_nose':((1413,796),0.008225),'Rpod_nose':((1692,743),0.007885),'fin_TE_mid':((1899,957),0.009255),'fin_TE_top':((1903,933),0.00928),
     'Lfin_bot':((1360,926),None),'Lfin_top':((1378,821),0.008866),'Rfin_top':((1950,712),0.008146)}
O=np.load('contour3d.npy')
q_lb=[(a[5]+a[6])/2 for a in O if int(a[0])==1360 and int(a[1])==926][0]
pts['Lfin_bot']=((1360,926),q_lb)
for e in [np.array([-765.,-483.]),np.array([-745.,-471.]),np.array([-785.,-495.])]:
  sweep.E[:]=e
  for f in [3550,3590,3640]:
    V,S,U=axes(f,e)
    X={k:to3d(p,q,f,18.49/24,e=e)[0] for k,(p,q) in pts.items()}
    fore={k:X[k]@V for k in X}
    front=(fore['Lpod_nose']+fore['Rpod_nose'])/2
    L1=front-fore['fin_TE_mid']; L2=front-fore['fin_TE_top']
    span=(X['Rfin_top']-X['Lfin_top'])@S
    print('E',e,'f',f,'length(N=24) TEmid %.2f TEtop %.2f | N=25: %.2f %.2f | fin-top span %.2f'%(L1,L2,L1*24/25,L2*24/25,span))
