import numpy as np
f=711.0; cx=640; cy=360
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.0]); return d/np.linalg.norm(d)
def bp(u,v,r): return r*ray(u,v)
