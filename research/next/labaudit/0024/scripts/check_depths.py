import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0024/scripts')
from slopeplane import *
for (u,v),st in [((747,394),1.0685),((680,443),0.977)]:
    for h in [0,0.0073,0.0146]:
        X=on_slope(u,v,h); print((u,v),'h',h,'model range %.3f stated %.4f ratio %.3f'%(np.linalg.norm(X),st,st/np.linalg.norm(X)),'slope coords',np.round(slope_coords(X),1))
