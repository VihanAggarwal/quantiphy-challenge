import cv2, numpy as np
W='/home/user/quantiphy-challenge/research/next/labaudit/0035/remeasure_work/'
B=np.load(W+'captured_0035b.npy')
cx,cy,f=640,360,711.
# local background: median over frames where ball not near (use frames far in time)
def meas(i,near,bgframes,thr):
    x,y=near; r=42
    patch=B[i][y-r:y+r,x-r:x+r].astype(np.int16)
    bg=np.median(np.stack([B[k][y-r:y+r,x-r:x+r] for k in bgframes]),axis=0).astype(np.int16)
    d=(patch.mean(axis=2)-bg.mean(axis=2))
    dd=np.abs(patch-bg).max(axis=2)
    m=(dd>thr).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cc=cv2.connectedComponentsWithStats(m)
    j=1+np.argmax(st[1:,4]); mm=(lab==j).astype(np.uint8)
    cnts,_=cv2.findContours(mm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cnts,key=cv2.contourArea); area=cv2.contourArea(c)
    (ex,ey),(a,b),ang=cv2.fitEllipse(c)
    ex+=x-r; ey+=y-r
    u=np.array([ex-cx,ey-cy,f]); u/=np.linalg.norm(u)
    return ex,ey,2*np.sqrt(area/np.pi),min(a,b),max(a,b),u[2],st[j][2],st[j][3]
for i,near in [(19,(588,500)),(20,(597,492)),(21,(606,485)),(22,(616,478)),(23,(624,472)),(24,(631,466)),(31,(680,486)),(32,(684,487)),(33,(688,489)),(34,(690,489)),(35,(693,489)),(36,(697,489))]:
    bgf=[k for k in range(49) if abs(k-i)>8]
    for thr in (25,40,60):
        r=meas(i,near,bgf,thr)
        print(i,thr,'c=(%.1f,%.1f) eqd=%.1f ell=%.1f/%.1f cos=%.3f bbox=%dx%d'%r)
