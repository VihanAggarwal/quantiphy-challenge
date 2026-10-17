import numpy as np
from sweep import E,C
def axes(f,e=E):
    e3=np.array([e[0]-C[0],e[1]-C[1],f]); V=e3/np.linalg.norm(e3)
    phi=np.arctan2(C[1]-e[1],f)
    up=np.array([0,-np.cos(phi),-np.sin(phi)]); up=up-V*(up@V); up/=np.linalg.norm(up)
    S=np.cross(V,up); S/=np.linalg.norm(S); U=np.cross(S,V)
    return V,S,U
