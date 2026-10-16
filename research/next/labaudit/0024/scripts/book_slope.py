import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0024/scripts')
from slopeplane import *
def Lc(a,b): return np.linalg.norm(a-b)*100
pts=dict(UL=(751,354),UR=(846,356),DR=(818,385),DL=(720,381))
for h in [0.010,0.0146,0.018]:
    X={k:on_slope(*p,h) for k,p in pts.items()}
    print('h=%.3f long: up %.1f down %.1f | short: left %.1f right %.1f'%(h,Lc(X['UL'],X['UR']),Lc(X['DL'],X['DR']),Lc(X['UL'],X['DL']),Lc(X['UR'],X['DR'])),
          ' coords', {k:np.round(slope_coords(v),1).tolist() for k,v in X.items()})
