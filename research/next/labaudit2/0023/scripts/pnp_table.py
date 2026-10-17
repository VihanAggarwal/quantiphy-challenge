import cv2, numpy as np, json
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
c=json.load(open(D+'scripts/table_corners_s48.json'))
img=np.array([c['FL'],c['FR'],c['BR'],c['BL']],float)
for f in [680,711,740]:
  K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
  for W,Dp in [(0.603,0.760),(0.760,0.603)]:
    obj=np.array([[0,0,0],[W,0,0],[W,Dp,0],[0,Dp,0]],float)  # table plane z=0, y away from camera
    ok,rv,tv=cv2.solvePnP(obj,img,K,None,flags=cv2.SOLVEPNP_IPPE)
    Rm,_=cv2.Rodrigues(rv)
    proj,_=cv2.projectPoints(obj,rv,tv,K,None)
    err=np.abs(proj.reshape(-1,2)-img).max()
    Pc=(Rm@obj.T).T+tv.ravel()
    rng=np.linalg.norm(Pc,axis=1)
    camC=-Rm.T@tv.ravel()
    print(f,W,Dp,'err %.2f'%err,'ranges FL FR BR BL',np.round(rng,3),'cam pos in table frame',np.round(camC,3))
