# plane-route distance of the ball centre in front of the table back edge (BL-BR) for each frame
import numpy as np, json
from geom import pose, on_plane, C
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0029/track.json'))
o=T['o']; x=T['x']
uv={k:np.array([(o[k]['cx']+x[k]['cx'])/2,(o[k]['cy']+x[k]['cy'])/2]) for k in range(49)}
R,t,n,d0,err=pose()
W,D=0.76,0.603
Rinv=R.T
for k in range(22,49):
    P=on_plane(*uv[k],R,t,n,d0,0.0335)
    X=Rinv@(P-t)     # table coords: x along FL->FR, y along FL->BL, z normal
    print(k,'table coords x=%.3f y=%.3f z=%.3f'%tuple(X),' gap to back edge (D - y) = %.1f cm'%(100*(D-X[1])))
