import numpy as np, json, cv2
C=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0033/corners.json'))
P=np.array([C['FL'],C['FR'],C['NR'],C['NL']])
def rays(p,f,cx=640,cy=360):
    d=np.c_[(p[:,0]-cx)/f,(p[:,1]-cy)/f,np.ones(len(p))]; return d
for f in [690,700,711,720,730]:
    d=rays(P,f)
    # plane through 4 rays forming a parallelogram: find depths lam_i s.t. lam0 d0 + lam2 d2 = lam1 d1 + lam3 d3 (diagonals bisect)
    # set lam0=1, solve 3 unknowns least squares
    A=np.c_[-d[2],d[1],d[3]]; b=d[0]
    sol,*_=np.linalg.lstsq(A,b,rcond=None)
    lam=np.r_[1,sol[1],sol[0],sol[2]]  # order FL,FR,NR,NL : lam0=FL, lam2=NR, lam1=FR, lam3=NL
    X=d*lam[:,None]
    w_far=np.linalg.norm(X[1]-X[0]); w_near=np.linalg.norm(X[2]-X[3]); dl=np.linalg.norm(X[3]-X[0]); dr=np.linalg.norm(X[2]-X[1])
    ang=np.degrees(np.arccos(np.dot(X[1]-X[0],X[3]-X[0])/w_far/dl))
    W=(w_far+w_near)/2; D=(dl+dr)/2
    for (Wt,Dt) in [(76.0,60.3),(60.3,76.0)]:
        s=Wt/W
        print('f',f,'W/D=%.3f'%(W/D),'angle %.1f'%ang,'target %.3f'%(Wt/Dt),'scale-> ranges FL FR NR NL',np.round(np.linalg.norm(X*s,axis=1),1))
