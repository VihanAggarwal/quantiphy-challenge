import cv2,numpy as np
f=711.0; K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
img=np.array([[210,540],[1137,589],[935,476],[447,453]],float)
for W,D in [(0.760,0.603),(0.603,0.760)]:
    obj=np.array([[0,0,0],[W,0,0],[W,D,0],[0,D,0]],float)
    ok,rv,tv=cv2.solvePnP(obj,img,K,None,flags=cv2.SOLVEPNP_IPPE)
    R,_=cv2.Rodrigues(rv)
    pr,_=cv2.projectPoints(obj,rv,tv,K,None)
    print(W,D,'reproj',np.round(pr.reshape(-1,2)-img,1).tolist())
    n=R[:,2]; d=n@tv.ravel()
    print(' normal(cam)',np.round(n,3),'plane dist',round(d,4), 'cam height above table',abs(d))
    # card center range
    for name,(u,v),rng in [('card',(563,541),0.679),('tower_base',(686,495),0.905)]:
        ray=np.array([(u-640)/f,(v-360)/f,1]); ray/=np.linalg.norm(ray)
        t=d/(n@ray)
        print(' ',name,'range to table along ray',round(t,4),'given',rng)
    # pitch: angle between optical axis and table plane
    print(' pitch deg (optical axis vs plane)',np.degrees(np.arcsin(abs(n[2]))), 'roll-ish', np.degrees(np.arctan2(n[0],n[1])))
