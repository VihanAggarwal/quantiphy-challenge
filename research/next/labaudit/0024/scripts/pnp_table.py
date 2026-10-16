import cv2, numpy as np
K=np.array([[711,0,640],[0,711,360],[0,0,1.]])
img=np.array([[411.7,466.4],[643.6,574.7],[1142.7,489.4],[790.6,438.8]])  # L, F, R, B
for f in [711,760,831]:
  K[0,0]=K[1,1]=f
  for (a,b) in [(76.0,60.3),(60.3,76.0)]:
    # L->F edge length a, F->R edge length b; F at origin
    obj=np.array([[0,a,0],[0,0,0],[b,0,0],[b,a,0]],float)/100
    ok,rv,tv=cv2.solvePnP(obj,img,K,None,flags=cv2.SOLVEPNP_IPPE)
    pr,_=cv2.projectPoints(obj,rv,tv,K,None)
    err=np.abs(pr.reshape(-1,2)-img).max()
    R,_=cv2.Rodrigues(rv)
    P=(R@obj.T).T+tv.ravel()
    rng=np.linalg.norm(P,axis=1)
    n=R[:,2]; cam_h=abs(n@tv.ravel())
    print(f,a,b,'maxerr',round(err,1),'ranges L F R B',np.round(rng,3),'cam height above table',round(cam_h,3))
