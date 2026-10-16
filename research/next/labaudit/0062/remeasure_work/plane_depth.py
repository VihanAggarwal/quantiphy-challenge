import numpy as np
f=711.; cx=640; cy=360
def bp(u,v,r):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return r*d/np.linalg.norm(d)
pts={'bag':(837.5,329.2,3.307),'box':(516.8,495.5,2.082),'mario':(635.1,623.8,2.016),
     'board34':(705.2,414.8,2.815),'board33':(716.6,425.1,2.815),'trash':(337.9,156.1,2.303)}
P={k:bp(*v) for k,v in pts.items()}
for k,v in P.items(): print(k, np.round(v,3))
def fit(keys):
    A=np.array([P[k] for k in keys]); c=A.mean(0)
    u,s,vt=np.linalg.svd(A-c); n=vt[-1]
    if n[1]<0: n=-n
    h=n@c
    return n,h,[(k,round(float(n@P[k]-h),3)) for k in keys]
for keys in [['bag','box','mario','board34'],['bag','box','mario','board33'],['bag','board34','mario'],['bag','board34','box'],['bag','box','mario','board34','trash']]:
    n,h,res=fit(keys)
    pitch=np.degrees(np.arcsin(n[2]))  # tilt of optical axis below horizontal
    print(keys,'n',np.round(n,3),'h',round(h,3),'pitch',round(float(np.degrees(np.arccos(n[1]))),1),res)
