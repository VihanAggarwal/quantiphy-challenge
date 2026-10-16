import sys; sys.path.insert(0,'.')
import numpy as np
import geom
from geom import *
TL=(751.12,359.46);TR=(863.97,361.12);BR=(707.58,492.35);BL=(603.54,469.91)
bk=np.load('slopebook_corners.npy')  # TL,TR,BR,BL
c_static=np.array([782.3,368.0]); c24=np.array([748.8,392.6]); c29=np.array([672.0,446.0])
def run(fv, which='board'):
    geom.f=fv; geom.K=np.array([[fv,0,cx],[0,fv,cy],[0,0,1]]); geom.Ki=np.linalg.inv(geom.K)
    if which=='board': d1,d2=rect_from_corners(TL,TR,BR,BL,fv)
    else: d1,d2=rect_from_corners(*bk,fv)
    n=np.cross(d1,d2); n/=np.linalg.norm(n)
    if n[2]>0: n=-n
    r=lambda p: (lambda v: v/np.linalg.norm(v))(np.array([(p[0]-cx)/fv,(p[1]-cy)/fv,1.0]))
    P24=1.0685*r(c24); d=n@P24
    rho_s=d/(n@r(c_static)); rho29=d/(n@r(c29))
    X=np.array([ (d/(n@r(p)))*r(p) for p in bk])
    top=np.linalg.norm(X[1]-X[0]); bot=np.linalg.norm(X[2]-X[3]); lef=np.linalg.norm(X[3]-X[0]); rig=np.linalg.norm(X[2]-X[1])
    P29=rho29*r(c29); Ps=rho_s*r(c_static)
    tilt=np.degrees(np.arccos(abs(n@np.array([0,-1,0]))))
    print('f=%d %s cos12=%.3f n=%s plane_d=%.3f rho_static=%.3f rho29(pred)=%.3f [given .977] |P29-P24|=%.3f  book top=%.2f bot=%.2f left=%.2f right=%.2f cm'%(fv,which,d1@d2,n.round(3),d,rho_s,rho29,np.linalg.norm(P29-P24),top*100,bot*100,lef*100,rig*100))
for fv in [650,711,780,835]:
    run(fv,'board')
for fv in [711]:
    run(fv,'book')
