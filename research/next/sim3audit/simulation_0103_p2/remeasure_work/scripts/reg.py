import numpy as np
from cam import Cam
W='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/remeasure_work/'
# camera configs: f, d, center, boat ref pt at t1, displacement t1->t2, D1, D2
CFG={
 'C2':dict(f=3860,d=54.5,c=(540,540),a1=(360,930),disp=(-85.74,-24.81),D=(173.7093,174.5515)),
 'C1':dict(f=3460,d=18.5,c=(480,480),a1=(611,600),disp=(-155.5,-6.05),D=(90.1103,90.4360)),
 'K22':dict(f=4500,d=0.0,c=(480,480),a1=(865,640),disp=(-110.57,0.0),D=(148.7451,146.9726)),
}
def frame_of(name,**over):
    g=dict(CFG[name]); g.update(over)
    cam=Cam(g['f'],g['d'],g['c'])
    a1=np.array(g['a1'],float); a2=a1+np.array(g['disp'],float)
    P1=cam.pt(a1[0],a1[1],g['D'][0]); P2=cam.pt(a2[0],a2[1],g['D'][1])
    V=P2-P1; X=np.array([V[0],V[1],0]); X/=np.linalg.norm(X); Z=np.array([0,0,1.]); Y=np.cross(Z,X)
    M=np.stack([X,Y,Z])
    return dict(cam=cam,P1=P1,P2=P2,V=V,M=M,g=g,C=-M@P1, speed=np.linalg.norm(V), vz=V[2])
def to_boat(F,p): return (np.asarray(p)-F['P1'])@F['M'].T
def from_boat(F,q): return np.asarray(q)@F['M']+F['P1']
def project(F,q):
    P=from_boat(F,q); return F['cam'].proj(P)
if __name__=='__main__':
    for n in CFG:
        F=frame_of(n); print(n,'cam pos in boat frame',np.round(F['C'],2),'speed',round(F['speed'],3),'Vz',round(F['vz'],3))
