import cv2, numpy as np, json
f=711.0; K=np.array([[f,0,640],[0,f,360],[0,0,1.]]); Ki=np.linalg.inv(K)
C=np.array([(448.4,448.6),(918.6,467.1),(1141.0,587.2),(209.8,535.7)])  # BL BR FR FL (x render, frame 48)
W,D=0.760,0.603
O=np.array([[0,D,0],[W,D,0],[W,0,0],[0,0,0]],float)
def pose(Cimg=C,f=f,W=W,D=D):
    K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
    O=np.array([[0,D,0],[W,D,0],[W,0,0],[0,0,0]],float)
    ok,rv,tv=cv2.solvePnP(O,Cimg,K,None,flags=cv2.SOLVEPNP_IPPE)
    R,_=cv2.Rodrigues(rv); 
    pr,_=cv2.projectPoints(O,rv,tv,K,None); err=np.abs(pr[:,0]-Cimg).max()
    n=R[:,2]          # table normal in camera coords
    d0=n@tv.ravel()   # plane: n.X = d0
    return R,tv.ravel(),n,d0,err
def ray(u,v,f=f):
    d=np.array([(u-640)/f,(v-360)/f,1.0]); return d
def on_plane(u,v,R,t,n,d0,hgt,f=f):
    # point on the plane hgt above the table top along +normal direction of 'up'
    up=-n if (n@np.array([0,-1,0]))<0 else n   # up vector in camera coords (camera y points down)
    # plane of ball centres: points X with up.(X - t) = hgt
    d=ray(u,v,f); s=(hgt+up@t)/(up@d); return s*d
if __name__=='__main__':
    R,t,n,d0,err=pose()
    up=-n if (n@np.array([0,-1,0]))<0 else n
    print('reproj err px %.2f'%err, 'cam height above top %.3f'%(-(up@t)) , 'up',up.round(3))
    for nm,X in zip(['BL','BR','FR','FL'],O): 
        Xc=R@X+t; print(nm,'range %.3f'%np.linalg.norm(Xc), Xc.round(3))
    # aspect check: homography-based f estimate
    for ff in [650,680,711,740,770]:
        R2,t2,n2,d2,e2=pose(f=ff); print('f',ff,'reproj err %.2f'%e2)
