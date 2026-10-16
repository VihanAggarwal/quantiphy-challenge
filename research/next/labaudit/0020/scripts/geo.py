import numpy as np
F=711.; CX=640.; CY=360.
def bp(u,v,r,f=F):
    d=np.array([(u-CX)/f,(v-CY)/f,1.0]); return r*d/np.linalg.norm(d)
