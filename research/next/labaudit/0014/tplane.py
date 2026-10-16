import numpy as np
from plane import L, C
from geo import bp
F=711.
v1=np.cross(L('left'),L('right')); v2=np.cross(L('front'),L('back'))
l=np.cross(v1,v2)
K=np.array([[F,0,640],[0,F,360],[0,0,1.]])
N=K.T@l; N/=np.linalg.norm(N); N*=np.sign(N[1])
def onplane(u,v,c,h=0.0,f=F):
    """3D point on plane n.X=c-h (h = height above table)"""
    d=np.array([(u-640)/f,(v-360)/f,1.0])
    s=(c-h)/(N@d); return s*d
