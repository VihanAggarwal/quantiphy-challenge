import cv2,numpy as np,json
C=json.load(open('table_corners.json'))
img=np.array([C['NL'],C['NR'],C['FR'],C['FL']],float)
for f in [690,711,730]:
  K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
  for W,D in [(0.760,0.603),(0.603,0.760)]:
    obj=np.array([[0,0,0],[W,0,0],[W,D,0],[0,D,0]],float)  # x right, y away
    ok,rv,tv=cv2.solvePnP(obj,img,K,None,flags=cv2.SOLVEPNP_IPPE)
    pr,_=cv2.projectPoints(obj,rv,tv,K,None)
    err=np.linalg.norm(pr.reshape(-1,2)-img,axis=1)
    R,_=cv2.Rodrigues(rv)
    n=R[:,2]; cam=-R.T@tv.ravel()
    print(f,W,D,'reproj',err.round(2),'cam pos in table frame',cam.round(3),'normal(cam)',n.round(3))
