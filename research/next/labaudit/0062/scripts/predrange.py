import numpy as np
from common import *
exec(open('wbplane.py').read().split('frames=[n')[0])
nm=normal(38.93,8.53)
objs={'whiteboard n34 centre':((704.8,409.8),0.0,2.815),'whiteboard n33.6':((710.3,415.0),0.0,2.815),
      'bag (mask centroid)':((837.4,329.2),0.0,3.307),'bag body centre':((832,333),0.0,3.307),
      'box top-face centre':((517,489),0.072,2.082),'box centroid (mid-height)':((516.8,495.5),0.036,2.082),
      'mario centroid':((635.1,623.8),0.05,2.016),'bin centroid (mid-height)':((337.9,156.1),0.19,2.303),'bin front face mid':((335,175),0.19,2.303)}
for h in (1.79,1.84,1.88):
    print('h=%.2f'%h)
    for k,(uv,dz,st) in objs.items():
        d=np.r_[(np.array(uv)-[CX,CY])/F,1]; dh=d/np.linalg.norm(d)
        rng=(h-dz)/(dh@nm)
        print('   %-28s pred %.3f  stated %.3f  stated/pred %.3f'%(k,rng,st,st/rng))
