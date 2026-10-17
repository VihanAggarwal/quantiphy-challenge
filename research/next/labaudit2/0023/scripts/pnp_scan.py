import cv2, numpy as np, json
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
c=json.load(open(D+'scripts/table_corners_s48.json'))
img=np.array([c['FL'],c['FR'],c['BR'],c['BL']],float)
for W,Dp in [(0.603,0.760),(0.760,0.603)]:
  best=None
  for f in range(400,1400,10):
    K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
    obj=np.array([[0,0,0],[W,0,0],[W,Dp,0],[0,Dp,0]],float)
    ok,rv,tv=cv2.solvePnP(obj,img,K,None,flags=cv2.SOLVEPNP_IPPE)
    ok,rv,tv=cv2.solvePnP(obj,img,K,None,rv,tv,True,flags=cv2.SOLVEPNP_ITERATIVE)
    proj,_=cv2.projectPoints(obj,rv,tv,K,None)
    err=np.sqrt(((proj.reshape(-1,2)-img)**2).sum(1)).max()
    Rm,_=cv2.Rodrigues(rv); Pc=(Rm@obj.T).T+tv.ravel(); rng=np.linalg.norm(Pc,axis=1)
    if f%50==0 or (best and err<best[0]): pass
    if best is None or err<best[0]: best=(err,f,rng)
    if f%100==0: print(W,Dp,f,'err %.2f'%err,np.round(rng,3), 'camC',np.round(-Rm.T@tv.ravel(),3))
  print('BEST',best)
