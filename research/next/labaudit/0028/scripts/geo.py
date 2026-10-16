import numpy as np
c=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0028/scripts/corners.npy')  # BL,BR,FR,FL
CX,CY=640,360
def model(f,which):
    d=np.array([[(u-CX)/f,(v-CY)/f,1.0] for u,v in c])
    A=np.stack([-d[1],d[2],-d[3]],1); b=-d[0]
    l=np.linalg.lstsq(A,b,rcond=None)[0]; lam=np.r_[1,l]; P=lam[:,None]*d
    W=(np.linalg.norm(P[1]-P[0])+np.linalg.norm(P[2]-P[3]))/2; D=(np.linalg.norm(P[3]-P[0])+np.linalg.norm(P[2]-P[1]))/2
    s= 0.603/W if which=='w' else 0.760/D
    P=P*s
    n=np.cross(P[1]-P[0],P[3]-P[0]); n/=np.linalg.norm(n)
    if n[1]>0: n=-n   # up normal should point to -y (image up)
    return P,n
def ray(u,v,f): r=np.array([(u-CX)/f,(v-CY)/f,1.0]); return r/np.linalg.norm(r)
def hitplane(u,v,f,P,n,off=0.0):
    r=ray(u,v,f); # plane n.(X-P0)=off
    t=(off+n@P[0])/(n@r); return t*r
for f in [711]:
  for which in ['w','d']:
    P,n=model(f,which)
    print('f',f,which,'corner ranges',np.round(np.linalg.norm(P,axis=1),3),'normal',np.round(n,3), 'cam height above plane',round(-(n@P[0]),3) if False else round(abs(n@P[0]),3))
    # back edge point at x=737
    for (u,v) in [(737,426),(737,423),(759,434),(766,454)]:
        X=hitplane(u,v,f,P,n); print('  table pt',(u,v),'range',round(np.linalg.norm(X),3))
    # ball centre 2cm above plane, point along ray
    for (u,v,lab) in [(736.8,406,'f26 centroid'),(737,413,'bounce ctr est')]:
        X=hitplane(u,v,f,P,n,off=0.02); print('  ball centre on 2cm plane',lab,round(np.linalg.norm(X),3))
