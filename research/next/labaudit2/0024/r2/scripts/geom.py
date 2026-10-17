"""Camera + table pose + slope plane for family 0024 (rebuilt from round-1 edge points, f=711, pp=(640,360))."""
import cv2, numpy as np, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from lsq import least_squares
F = 711.; CX = 640.; CY = 360.
HERE = os.path.dirname(os.path.abspath(__file__))
# round-1 table edge points (x00 render) -- re-verified visually in r2/png
BLe = [(x, y) for x, y in zip(range(430, 620, 20), [466, 464, 462, 461, 460, 458, 457, 455, 454, 452])]
BRe = [(900,455),(920,460),(940,462),(960,464),(980,467),(1000,470),(1020,473),(1040,475),(1060,478),(1080,482)]
FLe = [(430,475),(445,481),(460,489),(475,496),(490,503),(505,509),(520,516),(535,524),(550,531),(565,538),(580,545),(595,552)]
FRe = [(870,536),(885,533),(900,531),(915,528),(930,526),(945,523),(960,521),(975,518),(990,515),(1005,513),(1020,511),(1035,508),(1050,505),(1065,503),(1080,500)]
def fit_table(f=F, a=0.603, b=0.760):
    K = np.array([[f,0,CX],[0,f,CY],[0,0,1.]])
    obj = np.array([[0,a,0],[0,0,0],[b,0,0],[b,a,0]], float)  # L F R B
    edges = {'FL':(0,1,FLe),'FR':(1,2,FRe),'BR':(2,3,BRe),'BL':(3,0,BLe)}
    def res(p):
        pr,_ = cv2.projectPoints(obj,p[:3],p[3:],K,None); pr = pr.reshape(-1,2); r = []
        for k,(i,j,pts) in edges.items():
            A,B = pr[i],pr[j]; d = B-A; n = np.array([-d[1],d[0]])/np.linalg.norm(d)
            for q in pts: r.append((np.array(q)-A)@n)
        return np.array(r)
    img = np.array([[411.7,466.4],[643.6,574.7],[1142.7,489.4],[790.6,438.8]])
    ok,rv,tv = cv2.solvePnP(obj,img,K,None,flags=cv2.SOLVEPNP_IPPE)
    s = least_squares(res, np.r_[rv.ravel(),tv.ravel()])
    R,_ = cv2.Rodrigues(s.x[:3]); return R, s.x[3:], np.sqrt(np.mean(s.fun**2)), obj, K, s.x
_p = os.path.join(HERE, 'table_pose_711.npy')
if not os.path.exists(_p):
    R_, T_, rms_, *_ = fit_table(); np.save(_p, np.r_[R_.ravel(), T_, rms_])
_q = np.load(_p); R = _q[:9].reshape(3,3); T = _q[9:12]
n = R[:,2]
if n@(-T) < 0: n = -n
def ray(u, v, f=F):
    d = np.array([(u-CX)/f, (v-CY)/f, 1.]); return d/np.linalg.norm(d)
def on_plane(u, v, h=0.0):
    d = ray(u, v); s = (h + n@T)/(n@d); return s*d
cam_h = abs(n@T)
# slope (board) as rectangle: bottom edge on table plane, sides perpendicular to bottom edge (round-1 corner pixels)
BLp=(609,467); BRp=(705,493); TLp=(751,360); TRp=(857,361)
BL = on_plane(*BLp); BR = on_plane(*BRp)
e = (BL-BR)/np.linalg.norm(BL-BR)
def _corner_perp(P, base):
    r = ray(*P); s = (base@e)/(r@e); return s*r
TR = _corner_perp(TRp, BR); TL = _corner_perp(TLp, BL)
P0 = (BL+BR+TL+TR)/4
ns = np.cross(TR-BR, BL-BR); ns /= np.linalg.norm(ns)
if ns@(-P0) < 0: ns = -ns
up_dir = (TR-BR)/np.linalg.norm(TR-BR)
def on_slope(u, v, h=0.0):
    d = ray(u, v); s = (ns@P0 + h)/(ns@d); return s*d
def slope_coords(X):
    rel = X-BR; return np.array([rel@e, rel@up_dir, rel@ns])*100
if __name__ == '__main__':
    print('table rms px %.2f  camera height %.4f m' % (_q[12], cam_h))
    for nm,X in dict(BL=BL,BR=BR,TL=TL,TR=TR).items(): print(nm, np.round(slope_coords(X),1), 'range %.3f'%np.linalg.norm(X))
    print('slope len L %.1f R %.1f  bottom %.1f top %.1f  incline %.1f deg' % (np.linalg.norm(TL-BL)*100, np.linalg.norm(TR-BR)*100,
          np.linalg.norm(BL-BR)*100, np.linalg.norm(TL-TR)*100, np.degrees(np.arccos(abs(ns@n)))))
