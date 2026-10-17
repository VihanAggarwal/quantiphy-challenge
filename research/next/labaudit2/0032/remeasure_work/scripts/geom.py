import numpy as np
f=711.; cx=640.; cy=360.
K=np.array([[f,0,cx],[0,f,cy],[0,0,1.]]); Ki=np.linalg.inv(K)
vpd=np.array([717.6312,349.4066,1.]); vpl=np.array([-5951.974,322.874,1.])
lh=np.cross(vpd,vpl)
n=K.T@lh; n/=np.linalg.norm(n)
# orient n so that points below horizon (table) have positive n.ray (camera y down => table at +y)
if n[1]<0: n=-n
def ray(u,v):
    d=Ki@np.array([u,v,1.]); return d/np.linalg.norm(d)
def on_plane(u,v,hh):
    d=ray(u,v); return d*hh/(n@d)
