import numpy as np,json,cv2
C=json.load(open('corners.json')); P={k:np.array(v+[1.0]) for k,v in C.items()}
c=np.array([640,360.])
l_back=np.cross(P['BL'],P['BR']); l_front=np.cross(P['FL'],P['FR'])
l_left=np.cross(P['BL'],P['FL']); l_right=np.cross(P['BR'],P['FR'])
v1=np.cross(l_back,l_front); v1=v1[:2]/v1[2]
v2=np.cross(l_left,l_right); v2=v2[:2]/v2[2]
print('vanishing',v1,v2)
f2=-np.dot(v1-c,v2-c); print('f from orthogonality', np.sqrt(f2) if f2>0 else f2)
for f in [711.0, np.sqrt(abs(f2))]:
    K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
    for W,D in [(76.0,60.3),(60.3,76.0)]:
        obj=np.array([[0,0,0],[W,0,0],[0,D,0],[W,D,0]],float) # FL,FR,BL,BR ; x along front edge, y away
        img=np.array([C['FL'],C['FR'],C['BL'],C['BR']],float)
        ok,rv,tv=cv2.solvePnP(obj,img,K,None,flags=cv2.SOLVEPNP_IPPE)
        pr,_=cv2.projectPoints(obj,rv,tv,K,None); err=np.linalg.norm(pr.reshape(-1,2)-img,axis=1)
        R,_=cv2.Rodrigues(rv)
        print(f'f={f:.1f} W={W} D={D} reproj={err.round(2)} t={tv.ravel().round(1)} normal={R[:,2].round(3)}')
