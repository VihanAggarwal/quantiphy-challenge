import numpy as np
def make_cam(f, pp, vpM, vpC):
    Kinv=np.linalg.inv(np.array([[f,0,pp[0]],[0,f,pp[1]],[0,0,1.]]))
    d1=Kinv@np.array([vpM[0],vpM[1],1.]); d1/=np.linalg.norm(d1)
    d2=Kinv@np.array([vpC[0],vpC[1],1.]); d2-=d1*(d1@d2); d2/=np.linalg.norm(d2)
    up=np.cross(d1,d2)
    # want up pointing "up" in world: camera y axis is down, so up should have negative y component
    if up[1]>0: up=-up
    return Kinv, d1, d2, up
def ground_pt(Kinv, up, uv, H=1.0):
    r=Kinv@np.array([uv[0],uv[1],1.]); t=-H/(r@up)   # camera at origin, ground plane: X.up = -H
    return r*t
def line_ground(Kinv, up, ln, xs=None, ys=None):
    a,b,c=ln
    if ys is not None: pts=[(-(b*y+c)/a, y) for y in ys]
    else: pts=[(x, -(a*x+c)/b) for x in xs]
    return np.array([ground_pt(Kinv,up,p) for p in pts])
