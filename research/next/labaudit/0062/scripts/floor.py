import numpy as np, itertools
from common import ray
pts={'wb':((705.5,415.3),2.815),'bag':((837.4,329.2),3.307),'box':((516.8,495.5),2.082),'mario':((635.1,623.8),2.016),'bin':((337.9,156.1),2.303)}
for f in (700,711,722):
    P={k:r*ray(*uv,f=f) for k,(uv,r) in pts.items()}
    # plane through wb, bag, and lowered box/mario (unknown offsets) -> first exact plane with wb,bag,box
    for trio in [('wb','bag','box'),('wb','bag','mario'),('wb','box','mario'),('bag','box','mario')]:
        A=np.array([P[k] for k in trio])
        n=np.cross(A[1]-A[0],A[2]-A[0]); n/=np.linalg.norm(n)
        if n[1]<0: n=-n   # y down in camera: floor normal pointing down (+y)
        h=np.dot(n,A[0])  # camera height above plane
        pitch=np.degrees(np.arcsin(n[2]))  # tilt
        res={k:round(np.dot(n,P[k])-h,3) for k in P}
        print(f,trio,'h=%.3f'%h,'n=',np.round(n,3),'pitch=%.1f'%np.degrees(np.arccos(n[1])),res)
    print('dists', {k:np.round(P[k],3) for k in P})
