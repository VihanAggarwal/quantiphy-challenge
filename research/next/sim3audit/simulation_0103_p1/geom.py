import numpy as np
def P3(u,v,r,f,c=480.0):
    ray=np.array([(u-c)/f,(v-c)/f,1.0]); return r*ray/np.linalg.norm(ray)
def solve_f(u1,v1,r1,u2,v2,r2,speed,c=480.0,lo=500,hi=20000):
    g=lambda f: np.linalg.norm(P3(u2,v2,r2,f,c)-P3(u1,v1,r1,f,c))-speed
    for _ in range(100):
        m=0.5*(lo+hi)
        if g(lo)*g(m)<=0: hi=m
        else: lo=m
    return 0.5*(lo+hi)
def pitch_level(D):
    # camera coords x right,y down,z fwd; world up=(0,-cos th,-sin th); level => -Dy cos - Dz sin =0
    return np.degrees(np.arctan2(-D[1],D[2]))
