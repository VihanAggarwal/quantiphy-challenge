import numpy as np
F=711.0; CX=640.0; CY=360.0
def bp(u,v,d,f=F):
    r=np.array([(u-CX)/f,(v-CY)/f,1.0]); return d*r/np.linalg.norm(r)
def dist(a,b): return float(np.linalg.norm(np.asarray(a)-np.asarray(b)))
