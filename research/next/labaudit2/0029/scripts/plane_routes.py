import numpy as np, json
from geom import pose, ray, on_plane, C
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0029/track.json'))
o=T['o']; x=T['x']
uv={k:np.array([(o[k]['cx']+x[k]['cx'])/2,(o[k]['cy']+x[k]['cy'])/2]) for k in range(49)}
r=0.0335
anch={24:0.901,30:1.144,38:1.027}
def unit(u,v,f=711.): d=ray(u,v,f); return d/np.linalg.norm(d)
for f in [711.,740.]:
    R,t,n,d0,err=pose(f=f)
    print('== f',f,'PnP err %.1f'%err)
    P={k:on_plane(*uv[k],R,t,n,d0,r,f=f) for k in range(17,49)}
    for k,d in anch.items():
        rc=np.linalg.norm(P[k]); print(' video',k,'plane centre range %.3f  surface %.3f  stated %.3f'%(rc,rc-r,d))
    # plane from the 3 anchors (centre = (d+r) along ray)
    A=np.array([(anch[k]+r)*unit(*uv[k],f) for k in anch])
    nn=np.cross(A[1]-A[0],A[2]-A[0]); nn/=np.linalg.norm(nn)
    up=-n if (n@np.array([0,-1,0]))<0 else n
    if nn@up<0: nn=-nn
    print(' anchor-plane normal',nn.round(3),'PnP up',up.round(3),'angle deg %.1f'%np.degrees(np.arccos(np.clip(nn@up,-1,1))))
