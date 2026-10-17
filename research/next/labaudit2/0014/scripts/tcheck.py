import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0014/scripts')
from tplane import *
f=711.
n,c,rep,R,t=pose(f)
pts={'pen':((468,437),1.6725,0.005),'book':((653,410),1.665,0.0146),'slope_near':((559.2,416.2),1.701,0.0),'cookie_base?':((486,405),1.7355,0.0)}
for nm,(uv,rs,h) in pts.items():
    d=ray(*uv,f)
    # plane n.X=c, with n pointing from camera toward table? c>0: n.X=c on table; object above table toward camera: n.X = c - h
    r=(c-h)/(n@d)
    print(f'{nm:12s} plane range {r:.4f} stated {rs:.4f}  -> c needed {c*rs/r + h*(1-rs/r):.4f}' )
print('PnP c',round(c,4))
