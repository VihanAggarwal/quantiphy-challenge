import numpy as np
f=711.0; cx,cy=640.0,360.0
K=np.array([[f,0,cx],[0,f,cy],[0,0,1]]); Ki=np.linalg.inv(K)
def ray(p):
    r=Ki@np.array([p[0],p[1],1.0]); return r/np.linalg.norm(r)
def vpdir(l1,l2):
    v=np.cross(l1,l2); d=Ki@v; return d/np.linalg.norm(d)
def rect_from_corners(TL,TR,BR,BL, fval=None):
    # returns plane normal, side ratios using vanishing points; plane at unit distance
    global K,Ki
    if fval is not None:
        Kl=np.array([[fval,0,cx],[0,fval,cy],[0,0,1]]); Kli=np.linalg.inv(Kl)
    else: Kli=Ki
    h=lambda p: np.array([p[0],p[1],1.0])
    lt=np.cross(h(TL),h(TR)); lb=np.cross(h(BL),h(BR)); ll=np.cross(h(TL),h(BL)); lr=np.cross(h(TR),h(BR))
    d1=Kli@np.cross(lt,lb); d1/=np.linalg.norm(d1)
    d2=Kli@np.cross(ll,lr); d2/=np.linalg.norm(d2)
    return d1,d2
def plane_points(pts, n, dist, fval=None):
    # intersect rays with plane n.X = dist
    out=[]
    for p in pts:
        if fval is None: r=Ki@np.array([p[0],p[1],1.0])
        else: r=np.array([(p[0]-cx)/fval,(p[1]-cy)/fval,1.0])
        t=dist/(n@r); out.append(t*r)
    return np.array(out)
