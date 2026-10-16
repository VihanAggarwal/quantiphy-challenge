import cv2, numpy as np
C=np.load('corners.npy')  # BL BR FR FL
for f in [690,711,730]:
  K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
  for W,Dp in [(76.0,60.3),(60.3,76.0)]:
    obj=np.array([[0,Dp,0],[W,Dp,0],[W,0,0],[0,0,0]],float)  # x right, y away from camera, z up
    ok,rv,tv=cv2.solvePnP(obj,C,K,None,flags=cv2.SOLVEPNP_IPPE)
    pr,_=cv2.projectPoints(obj,rv,tv,K,None)
    err=np.abs(pr.reshape(-1,2)-C).max()
    R,_=cv2.Rodrigues(rv); cam=-R.T@tv.ravel()
    print(f,W,Dp,'reproj max err %.2f'%err,'cam pos',cam.round(1))
