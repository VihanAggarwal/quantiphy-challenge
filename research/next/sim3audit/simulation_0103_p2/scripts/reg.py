import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from cam import Cam
def P_world(cam,pix,D,conv='range'):
    d=cam.ray(*pix)
    if conv=='z': D=D/(d@cam.fc)
    return cam.C+D*d
class Reg:
    """camera k registered into W (origin = boat origin at t=1, X = boat motion dir, Z up)"""
    def __init__(s,f,cx,cy,p,b1,b2,D1,D2,conv='range'):
        s.cam=Cam(f,cx,cy,p,0.0); s.conv=conv
        B1=P_world(s.cam,b1,D1,conv); B2=P_world(s.cam,b2,D2,conv)
        e1=B2-B1; s.boat_dz=e1[2]; s.boat_speed=np.linalg.norm(e1); e1[2]=0; e1/=np.linalg.norm(e1)
        e2=np.array([-e1[1],e1[0],0.]); s.R=np.stack([e1,e2,[0,0,1.]])  # rows: W axes in Wk coords
        s.B1=B1
    def to_W(s,P): return s.R@(np.asarray(P)-s.B1)
    def from_W(s,Q): return s.R.T@np.asarray(Q)+s.B1
    def obj_W(s,pix,D): return s.to_W(P_world(s.cam,pix,D,s.conv))
    def project_W(s,Q):
        P=s.from_W(Q); return s.cam.project(P)
    def cam_W(s): return s.to_W(s.cam.C)
