import numpy as np
f=711.;cx,cy=640.,360.
def r(p): v=np.array([(p[0]-cx)/f,(p[1]-cy)/f,1.]); return v/np.linalg.norm(v)
def h(p): return np.array([p[0],p[1],1.])
Kt=np.array([[f,0,0],[0,f,0],[cx,cy,1]])  # K^T
L=(414.4,468.1); F=(642.75,576.0)
sFR=-0.168
for sLB in [-0.03,-0.05,-0.06,-0.08,-0.10,-0.12]:
    lLB=np.cross(h(L),h((L[0]+100,L[1]+100*sLB)))
    lFR=np.cross(h(F),h((F[0]+100,F[1]+100*sFR)))
    mLB=Kt@lLB; mFR=Kt@lFR
    e2=np.cross(mLB,mFR); e2/=np.linalg.norm(e2)
    if e2[0]<0: e2=-e2
    L3=1.035*r(L)
    # solve rho_F s.t. (rho r_F - L3).e2 = 0
    rho=(L3@e2)/(r(F)@e2)
    F3=rho*r(F); a=np.linalg.norm(F3-L3); e1=(F3-L3)/a
    n=np.cross(e1,e2); n/=np.linalg.norm(n)
    if n[1]>0: n=-n
    # camera height above table
    hcam=-(n@L3)
    # vanishing pt of e2
    vp=np.array([f*e2[0]/e2[2]+cx, f*e2[1]/e2[2]+cy])
    print('sLB=%.2f e2=%s rhoF=%.3f |LF|=%.3f n=%s camh=%.3f vpE2=%s'%(sLB,e2.round(3),rho,a,n.round(3),hcam,vp.round(0)))
