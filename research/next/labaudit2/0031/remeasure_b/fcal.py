import cv2, numpy as np
P=np.load('/home/user/quantiphy-challenge/research/next/labaudit2/0031/remeasure_b/corners.npy')
for W,D in [(60.3,76.0),(76.0,60.3)]:
    obj=np.array([[-W/2,D,0],[W/2,D,0],[W/2,0,0],[-W/2,0,0]],float)  # back-left, back-right, front-right, front-left; y away
    res=[]
    for f in np.arange(550,1000,5):
        K=np.array([[f,0,640],[0,f,360],[0,0,1]],float)
        ok,rv,tv=cv2.solvePnP(obj,P,K,None,flags=cv2.SOLVEPNP_IPPE)
        pr,_=cv2.projectPoints(obj,rv,tv,K,None)
        e=np.sqrt(((pr[:,0]-P)**2).sum(1)).mean()
        res.append((e,f,tv.ravel()))
    res.sort(key=lambda r:r[0])
    print(W,D,[(round(r[0],2),r[1]) for r in res[:5]], res[0][2])
    for f in (711,760):
        K=np.array([[f,0,640],[0,f,360],[0,0,1]],float)
        ok,rv,tv=cv2.solvePnP(obj,P,K,None,flags=cv2.SOLVEPNP_IPPE)
        pr,_=cv2.projectPoints(obj,rv,tv,K,None)
        R,_=cv2.Rodrigues(rv)
        cam=-R.T@tv
        print('  f',f,'err',np.round(np.sqrt(((pr[:,0]-P)**2).sum(1)),2),'cam pos in table frame',cam.ravel().round(1))
