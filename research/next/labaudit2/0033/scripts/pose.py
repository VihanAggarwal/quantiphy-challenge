import cv2, numpy as np, json
C=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0033/corners.json'))
img=np.array([C['FL'],C['FR'],C['NL'],C['NR']],float)
for f in [680,711,740,770]:
  K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
  for W,D in [(60.3,76.0),(76.0,60.3)]:
    obj=np.array([[0,D,0],[W,D,0],[0,0,0],[W,0,0]],float)  # y axis away from camera (far edge y=D)
    ok,rv,tv=cv2.solvePnP(obj,img,K,None,flags=cv2.SOLVEPNP_IPPE)
    Rm,_=cv2.Rodrigues(rv)
    pr,_=cv2.projectPoints(obj,rv,tv,K,None)
    err=np.abs(pr.reshape(-1,2)-img).max()
    cam=-Rm.T@tv.ravel()
    n_cam=Rm[:,2]  # plane normal in camera coords
    print(f,W,D,'err %.2f'%err,'cam pos (table coords) %s'%np.round(cam,1),'normal_cam',np.round(n_cam,4))
