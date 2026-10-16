import numpy as np
F=711.0; CX=640; CY=360
def bp(u,v,r,f=F):
    d=np.array([(u-CX)/f,(v-CY)/f,1.0]); d/=np.linalg.norm(d); return r*d
def bpz(u,v,z,f=F):
    return np.array([(u-CX)/f*z,(v-CY)/f*z,z])
def bisect(fn,a,b,it=80):
    fa=fn(a)
    for _ in range(it):
        m=(a+b)/2; fm=fn(m)
        if (fm>0)==(fa>0): a,fa=m,fm
        else: b=m
    return (a+b)/2
def proj(X,f=F): return np.array([f*X[0]/X[2]+CX, f*X[1]/X[2]+CY])
