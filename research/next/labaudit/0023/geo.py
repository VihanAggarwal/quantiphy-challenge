import numpy as np
F=711.; CX=640.; CY=360.
def ray(u,v,f=F):
    d=np.array([(u-CX)/f,(v-CY)/f,1.]); return d/np.linalg.norm(d)
def bp(u,v,r,f=F): return ray(u,v,f)*r
