import numpy as np
class Cam:
    """pinhole, roll 0. world: Z up, camera at (0,0,h), azimuth +Y, pitched down by p (deg)."""
    def __init__(s,f,cx,cy,p,h):
        s.f,s.cx,s.cy,s.h=f,cx,cy,h; pr=np.radians(p)
        s.xc=np.array([1.,0,0]); s.fc=np.array([0,np.cos(pr),-np.sin(pr)]); s.uc=np.array([0,np.sin(pr),np.cos(pr)])
        s.C=np.array([0,0,h])
    def ray(s,u,v):
        d=(u-s.cx)/s.f*s.xc-(v-s.cy)/s.f*s.uc+s.fc; return d/np.linalg.norm(d)
    def cam2world_vec(s,v):  # camera frame x right,y down,z fwd
        return v[0]*s.xc-v[1]*s.uc+v[2]*s.fc
    def ground(s,u,v,z0=0.):
        d=s.ray(u,v); t=(s.h-z0)/(-d[2]); return s.C+t*d
    def project(s,P):
        d=np.asarray(P)-s.C; x=d@s.xc; y=-(d@s.uc); z=d@s.fc
        return np.array([s.cx+s.f*x/z, s.cy+s.f*y/z])
def cam_from_object(f,cx,cy,p,pix,D,conv='range'):
    """camera height above an object point seen at pix with range D"""
    c=Cam(f,cx,cy,p,0.)
    d=c.ray(*pix)
    if conv=='z': D=D/(d@c.fc)
    return -(D*d)[2]   # object is this far below camera
