import numpy as np
from sweep import *
P={'Lpod_rear':(1622,982),'Rpod_rear':(1911,918),'Rvfin_tip':(1895,993),'Lfin_top':(1378,821),'Rfin_top':(1950,712),
   'Lpod_front':(1414,798),'Rpod_front':(1692,746),'canopy_top':(1620,746),'probe_tip':(1539,771),'nozzle_bot':(1742,946),
   'Lfin_bot':(1342,912),'Rtail_tip':(1984,834),'Rwing_rear':(1998,787)}
for c in ['0303','0305']:
    for k,p in P.items():
        q,cost,_=sweep(c,p)
        print(c,k,p,'q=%.6f'%q,'cost=%.3f'%cost)
