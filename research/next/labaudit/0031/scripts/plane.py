import cv2, numpy as np
C=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0031/scripts/corners.npy')  # BL BR FR FL
cx,cy=640,360
for f in [650,711,760]:
    K=np.array([[f,0,cx],[0,f,cy],[0,0,1.]])
    # vanishing points
    def line(p,q): return np.cross([*p,1],[*q,1])
    BL,BR,FR,FL=C
    vd=np.cross(line(FL,BL),line(FR,BR)); vd=vd/vd[2]
    vw=np.cross(line(FL,FR),line(BL,BR));
    dd=np.linalg.inv(K)@vd; dd/=np.linalg.norm(dd)
    dw=np.linalg.inv(K)@vw; dw/=np.linalg.norm(dw)
    print('f',f,'vd',vd[:2].round(1),'cos(dw,dd)',float(abs(dd@dw)).__round__(4))
    n=np.cross(dd,dw); n/=np.linalg.norm(n)
    if n[1]>0: n=-n  # normal pointing up (camera y down => up is -y)
    # plane: n.X = -h ; back-project corners with plane at unit distance
    rays=[np.linalg.inv(K)@np.array([*p,1.]) for p in C]
    # choose plane n.X = d0 with d0 arbitrary=1 -> X = d0*r/(n.r)
    P=[r/(n@r) for r in rays]
    wF=np.linalg.norm(P[2]-P[3]); wB=np.linalg.norm(P[1]-P[0]); lL=np.linalg.norm(P[0]-P[3]); lR=np.linalg.norm(P[1]-P[2])
    W=(wF+wB)/2; Lg=(lL+lR)/2
    print('  aspect L/W',round(Lg/W,3),'wF wB lL lR',np.round([wF,wB,lL,lR],3))
    for scale_name,s in [('W=60.3',60.3/W),('L=76',76.0/Lg)]:
        Ps=[p*s for p in P]
        print('  ',scale_name,'cam height above plane cm',round(abs(s*1.0),1),'corner ranges cm',[round(np.linalg.norm(p),1) for p in Ps],'W',round(W*s,1),'L',round(Lg*s,1))
    np.save(f'/home/user/quantiphy-challenge/research/next/labaudit/0031/scripts/plane_f{f}.npy',np.concatenate([n,[W,Lg]]))
