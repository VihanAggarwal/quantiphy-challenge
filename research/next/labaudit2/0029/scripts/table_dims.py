# table-top dimensions implied by the stated depths: plane through the three ball centres (stated surface range + r
# along the clicked ray), shifted down by r, corner rays intersected with it. Second route: PnP with f free.
import numpy as np, json, cv2
from geom import C, ray
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0029/track.json'))
o=T['o']; x=T['x']
uv={k:np.array([(o[k]['cx']+x[k]['cx'])/2,(o[k]['cy']+x[k]['cy'])/2]) for k in range(49)}
anch={24:0.901,30:1.144,38:1.027}
for f in [690.,711.,730.]:
  for roff in [0.0335,0.0335+0.022]:   # ToF read as surface; or ToF 2.2 cm long (A-route mean bias) removed
    def unit(p): d=ray(*p,f); return d/np.linalg.norm(d)
    A=np.array([(anch[k]+0.0335-(roff-0.0335))*unit(uv[k]) for k in sorted(anch)])
    nn=np.cross(A[1]-A[0],A[2]-A[0]); nn/=np.linalg.norm(nn)
    if nn[1]>0: nn=-nn          # up (camera y down)
    c0=nn@A[0]-0.0335           # table-top plane: nn.X = c0  (r below the centre plane)
    P=[(c0/(nn@unit(p)))*unit(p) for p in C]
    W1=np.linalg.norm(P[1]-P[0]); W2=np.linalg.norm(P[2]-P[3]); D1=np.linalg.norm(P[3]-P[0]); D2=np.linalg.norm(P[2]-P[1])
    print('f %.0f ToF bias %.1f cm: back %.1f front %.1f | left %.1f right %.1f cm | cam height %.3f'%(f,100*(roff-0.0335),100*W1,100*W2,100*D1,100*D2,-c0))
