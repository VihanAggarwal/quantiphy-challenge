import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0024/scripts')
from slopeplane import *
top=[(755,351.3),(760,351.3),(770,352.3),(780,352.3),(790,351.8),(800,351.4),(810,351.4),(820,351.4),(830,351.3),(840,351.3)]
pb=[(750,391),(760,392),(770,392),(780,393),(790,394),(800,393),(810,393)]
for H in [1.2,1.46,1.8]:
    A1=[slope_coords(on_slope(u,v,H/100)) for u,v in top]
    A2=[slope_coords(on_slope(u,v,0)) for u,v in pb]
    a1=np.array([a[1] for a in A1]); a2=np.array([a[1] for a in A2])
    print('H=%.2f  up-edge along: %s  mean %.2f | pages-bottom along: %s mean %.2f | W_sil = %.2f'%(H,np.round(a1,1),a1.mean(),np.round(a2,1),a2.mean(),a1.mean()-a2.mean()))
    print('   across range of up edge %.1f..%.1f'%(min(a[0] for a in A1),max(a[0] for a in A1)))
