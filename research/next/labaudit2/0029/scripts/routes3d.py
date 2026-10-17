# 3D ball-centre tracks by three routes; label-style forward differences at the asked times
import numpy as np, json
from geom import pose, ray, on_plane
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0029/track.json'))
o=T['o']; x=T['x']
uv={k:np.array([(o[k]['cx']+x[k]['cx'])/2,(o[k]['cy']+x[k]['cy'])/2]) for k in range(49)}
minor={k:x[k]['ell'][2] for k in range(49)}
r=0.0335; f=711.
cap=lambda k: k+(k>=12)+(k>=36)
anch={24:0.901,30:1.144,38:1.027}
def unit(u,v): d=ray(u,v,f); return d/np.linalg.norm(d)
R,t,n,d0,err=pose(f=f)
PA={k:on_plane(*uv[k],R,t,n,d0,r,f=f) for k in range(18,49)}
A=np.array([(anch[k]+r)*unit(*uv[k]) for k in sorted(anch)])
nn=np.cross(A[1]-A[0],A[2]-A[0]); nn/=np.linalg.norm(nn); c0=nn@A[0]
PB={k:(c0/(nn@unit(*uv[k])))*unit(*uv[k]) for k in range(18,49)}
PC={k:(f*0.067/minor[k])*unit(*uv[k]) for k in range(18,49)}
routes=dict(A_pnp=PA,B_anchorplane=PB,C_size=PC)
print('k  n   rangeA  rangeB  rangeC   stepA stepB stepC (cm per capture step; double step across drop)')
for k in range(18,49):
    s=[]
    for nm,P in routes.items():
        s.append(np.linalg.norm(P[k]))
    st=[]
    for nm,P in routes.items():
        st.append(100*np.linalg.norm(P[k+1]-P[k]) if k+1 in P else np.nan)
    print(k,cap(k),' '.join('%.3f'%v for v in s),'  ',' '.join('%5.2f'%v for v in st), ' stated %.3f'%anch[k] if k in anch else '')
json.dump({nm:{k:list(map(float,v)) for k,v in P.items()} for nm,P in routes.items()},open('/home/user/quantiphy-challenge/research/next/labaudit2/0029/routes3d.json','w'))
