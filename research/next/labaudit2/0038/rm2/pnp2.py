import cv2, numpy as np
D='/home/user/quantiphy-challenge/research/next/labaudit2/0038/rm2/'
C=np.load(D+'corners.npy')
def solve(f,W=76.0,Dp=60.3,cx=640,cy=360):
    K=np.array([[f,0,cx],[0,f,cy],[0,0,1.]])
    obj=np.array([[0,0,0],[W,0,0],[W,Dp,0],[0,Dp,0]],float)
    ok,rv,tv=cv2.solvePnP(obj,C,K,None,flags=cv2.SOLVEPNP_IPPE)
    ok,rv,tv=cv2.solvePnP(obj,C,K,None,rv,tv,True,flags=cv2.SOLVEPNP_ITERATIVE)
    pr,_=cv2.projectPoints(obj,rv,tv,K,None); err=np.sqrt(((pr.reshape(-1,2)-C)**2).sum(1)).mean()
    R,_=cv2.Rodrigues(rv); return K,R,tv.ravel(),err
def table_pt(K,R,t,px,h=0.0):
    u=np.linalg.solve(K,[px[0],px[1],1.]); u/=np.linalg.norm(u)
    n=R[:,2]; # plane z=h in table coords: n.(X-t)=h  -> X = s u
    # table z axis: obj y toward back, x right -> z = x cross y = down? check sign
    s=(h*1+n@t)/(n@u)
    return s*u
for f in [711,750,780,800]:
    K,R,t,err=solve(f)
    n=R[:,2]
    up = -n if n[1]>0 else n   # camera y down; up has negative y
    sgn = 1 if np.allclose(up,n) else -1
    card=table_pt(K,R,t,(569,543))
    # ball surface at frame 34 center (726,496): center at height 2cm above table
    bc=table_pt(K,R,t,(726,496),h=2.0*sgn)
    print('f=%d err=%.2f card=%.1f ballC=%.1f ballSurf=%.1f'%(f,err,np.linalg.norm(card),np.linalg.norm(bc),np.linalg.norm(bc)-2), 'cam height above table %.1f'%abs(n@t))
for f in np.arange(700,900,10):
    print(f, '%.2f'%solve(f)[3])
print('---- sign check')
for f in [711,750]:
    K,R,t,err=solve(f)
    Cw=-R.T@t
    print('f',f,'camera in table coords',Cw.round(1))
    up=np.sign(Cw[2])
    for name,px in [('ball34',(726,496)),('ball22',(527.7,493.6))]:
        for h in [0,2.0*up]:
            P=table_pt(K,R,t,px,h=h)
            Pt=R.T@(P-t)
            print(name,'h=%.1f'%h,'range %.1f'%np.linalg.norm(P),'table coords',Pt.round(1))
