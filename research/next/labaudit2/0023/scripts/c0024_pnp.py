import cv2, numpy as np, json
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
C=json.load(open(D+'scripts/c0024_board.json'))['table']
img=np.array([C['BL'],C['BR'],C['TR'],C['TL']],float)
W=0.242
for f in [650,711,780]:
    K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
    best=None
    for Lb in np.arange(0.26,0.40,0.002):
        obj=np.array([[0,0,0],[W,0,0],[W,Lb,0],[0,Lb,0]],float)
        ok,rv,tv=cv2.solvePnP(obj,img,K,None,flags=cv2.SOLVEPNP_IPPE)
        proj,_=cv2.projectPoints(obj,rv,tv,K,None); err=np.sqrt(((proj.reshape(-1,2)-img)**2).sum(1)).max()
        if best is None or err<best[0]:
            Rm,_=cv2.Rodrigues(rv); best=(err,Lb,Rm,tv.ravel())
    err,Lb,Rm,tv=best
    obj=np.array([[0,0,0],[W,0,0],[W,Lb,0],[0,Lb,0]],float); Pc=(Rm@obj.T).T+tv
    mid_bot=(Pc[0]+Pc[1])/2; mid_top=(Pc[2]+Pc[3])/2
    print('f',f,'best board length %.3f m (err %.2f px); range bottom-mid %.3f top-mid %.3f (ToF near 0.990 far 1.243)'%(Lb,err,np.linalg.norm(mid_bot),np.linalg.norm(mid_top)))
