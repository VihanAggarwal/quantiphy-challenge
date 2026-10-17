import numpy as np
class Cam:
    def __init__(s,f,d_deg,c,roll_deg=0.0):
        s.f=f; s.d=np.radians(d_deg); s.c=np.array(c,float)
        d=s.d; ro=np.radians(roll_deg)
        # camera axes in world (E=right, N=forward horiz, U=up); cam x right, y down, z forward
        z=np.array([0,np.cos(d),-np.sin(d)])
        x0=np.array([1,0,0]); y0=np.cross(z,x0)  # y = z cross x -> down-ish
        x=np.cos(ro)*x0+np.sin(ro)*y0; y=np.cross(z,x)
        s.R=np.stack([x,y,z],1)  # world = R @ cam
    def ray(s,u,v):
        r=np.stack([(np.asarray(u,float)-s.c[0])/s.f,(np.asarray(v,float)-s.c[1])/s.f,np.ones_like(np.asarray(u,float))],-1)
        r=r/np.linalg.norm(r,axis=-1,keepdims=True)
        return r@s.R.T   # world dirs
    def pt(s,u,v,D):  # world point (camera at origin) at range D
        return s.ray(u,v)*np.asarray(D,float)[...,None]
    def ground(s,u,v,h):  # intersect with plane U=-h
        r=s.ray(u,v); t=-h/r[...,2]; return r*t[...,None]
    def proj(s,P):
        c=P@s.R; return np.stack([s.f*c[...,0]/c[...,2]+s.c[0], s.f*c[...,1]/c[...,2]+s.c[1]],-1), c[...,2]
