import numpy as np
from sweep import *
from frame3d import axes
Q={'Lpod_rear':0.00895,'Rpod_rear':0.00856,'Rvfin_tip':0.00922,'Lfin_top':0.008866,'Rfin_top':0.008146,'Lpod_front':0.00823,'Rpod_front':0.00789,
 'canopy_top':0.00826,'probe_tip':0.00824,'nozzle_bot':0.00891,'Lfin_bot':0.00884,'Rtail_tip':0.00913,'Rwing_rear':0.00826}
P={'Lpod_rear':(1622,982),'Rpod_rear':(1911,918),'Rvfin_tip':(1895,993),'Lfin_top':(1378,821),'Rfin_top':(1950,712),
   'Lpod_front':(1414,798),'Rpod_front':(1692,746),'canopy_top':(1620,746),'probe_tip':(1539,771),'nozzle_bot':(1742,946),
   'Lfin_bot':(1342,912),'Rtail_tip':(1984,834),'Rwing_rear':(1998,787)}
f=3575; vzf=18.49/24
V,S,U=axes(f)
X={k:to3d(P[k],Q[k],f,vzf)[0] for k in P}
ref=(X['Lfin_top']+X['Rfin_top'])/2
for k in P:
    d=X[k]-ref
    print('%-11s fore %6.2f span %6.2f up %6.2f  Z %.2f'%(k,d@V,d@S,d@U,X[k][2]))
print('fin-top distance',np.linalg.norm(X['Lfin_top']-X['Rfin_top']))
