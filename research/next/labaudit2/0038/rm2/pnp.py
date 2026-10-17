import cv2, numpy as np
D='/home/user/quantiphy-challenge/research/next/labaudit2/0038/rm2/'
C=np.load(D+'corners.npy')  # FL FR BR BL
for f in [690,711,730]:
  K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
  for W,Dp in [(76.0,60.3),(60.3,76.0)]:
    obj=np.array([[0,0,0],[W,0,0],[W,Dp,0],[0,Dp,0]],float)  # x along front edge, y toward back
    ok,rv,tv=cv2.solvePnP(obj,C,K,None,flags=cv2.SOLVEPNP_IPPE)
    pr,_=cv2.projectPoints(obj,rv,tv,K,None); err=np.abs(pr.reshape(-1,2)-C).max()
    R,_=cv2.Rodrigues(rv)
    n=R[:,2]; d=n@tv.ravel()
    # card pixel range check: credit card center approx (569,543)
    def ray_plane(px,h=0):
        u=np.linalg.solve(K,[px[0],px[1],1.]); u/=np.linalg.norm(u)
        # plane: n.X = d + h*(-?) ; table normal pointing up: object z up?
        t=(d - h*np.sign(1)*0)/(n@u); return t*u
    P=ray_plane((569,543))
    print(f,W,Dp,'reproj %.2f'%err,'card range %.1f cm'%np.linalg.norm(P), 'tvec',tv.ravel().round(1),'normal',n.round(3))
