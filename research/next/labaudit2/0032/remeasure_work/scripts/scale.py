import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/remeasure_work/scripts')
from geom import *
print('normal',n, 'tilt vs camera y-axis deg', np.degrees(np.arccos(n[1])))
# table front edge corners FL FR BL BR
C=dict(FL=(462.94,482.41),FR=(963.71,494.87),BR=(851.13,428.32),BL=(574.72,424.04))
P={k:on_plane(*v,1.0) for k,v in C.items()}
W=np.linalg.norm(P['FR']-P['FL']); Wb=np.linalg.norm(P['BR']-P['BL'])
L1=np.linalg.norm(P['BL']-P['FL']); L2=np.linalg.norm(P['BR']-P['FR'])
print('per unit h: front W %.3f back W %.3f  left L %.3f right L %.3f'%(W,Wb,L1,L2))
print('h from W=60.3 (front,back):', 60.3/W, 60.3/Wb, ' h from L=76.0:', 76/L1, 76/L2)
# depth anchors
for name,(u,v),Rs,r in [('pingpong',(721.4,432.0),135.3,2.0),('tennis',(583.0,434.5),118.3,3.35)]:
    d=ray(u,v); Rc=Rs+r
    hh=Rc*(n@d)+r
    print(name,'h=%.2f cm'%hh)
