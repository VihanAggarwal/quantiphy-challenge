import cv2, numpy as np, json, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0014/scripts')
from geo import ray, bp, proj, CX, CY
TC=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0014/table_corners.json'))
img=np.array([TC['FL'],TC['FR'],TC['BR'],TC['BL']],np.float64)
def pose(f,W=0.603,D=0.760):
    obj=np.array([[0,0,0],[W,0,0],[W,D,0],[0,D,0]],np.float64)
    K=np.array([[f,0,CX],[0,f,CY],[0,0,1]])
    ok,rv,tv=cv2.solvePnP(obj,img,K,None,flags=cv2.SOLVEPNP_IPPE)
    R,_=cv2.Rodrigues(rv)
    rep=cv2.projectPoints(obj,rv,tv,K,None)[0][:,0,:]
    n=R[:,2]; P0=tv.ravel(); c=n@P0
    if c<0: n=-n; c=-c
    return n,c,float(np.abs(rep-img).max()),R,tv.ravel()
def plane_from_vps(f):
    # normal from VPs of L/R and F/B edges
    h=lambda p: np.array([p[0],p[1],1.0])
    FL,FR,BR,BL=[np.array(TC[k]) for k in ('FL','FR','BR','BL')]
    v1=np.cross(np.cross(h(FL),h(BL)),np.cross(h(FR),h(BR)))
    v2=np.cross(np.cross(h(FL),h(FR)),np.cross(h(BL),h(BR)))
    Ki=np.array([[1/f,0,-CX/f],[0,1/f,-CY/f],[0,0,1]])
    d1=Ki@v1; d1/=np.linalg.norm(d1); d2=Ki@v2; d2/=np.linalg.norm(d2)
    n=np.cross(d1,d2); n/=np.linalg.norm(n)
    return n,float(d1@d2)
def inter(u,v,n,c,f=711.):
    d=ray(u,v,f); return c/(n@d)*d
if __name__=='__main__':
    for f in [680,711,740]:
        n,c,rep,R,t=pose(f)
        nv,orth=plane_from_vps(f)
        if nv@n<0: nv=-nv
        print(f'f={f} PnP n={np.round(n,3)} c={c:.4f} maxrep={rep:.2f}px | VP n={np.round(nv,3)} d1.d2={orth:.3f} angle(n,nv)={np.degrees(np.arccos(min(1,n@nv))):.2f}')
        # swapped dims
        n2,c2,rep2,_,_=pose(f,0.760,0.603)
        print(f'      swapped dims maxrep={rep2:.2f}')
        # table-size check from plane c using VP normal
        FL,FR,BR,BL=[np.array(TC[k]) for k in ('FL','FR','BR','BL')]
        X=[inter(*p,nv,c,f) for p in (FL,FR,BR,BL)]
        print('      VP-normal plane at PnP c: front',round(100*np.linalg.norm(X[0]-X[1]),1),'back',round(100*np.linalg.norm(X[3]-X[2]),1),'left',round(100*np.linalg.norm(X[0]-X[3]),1),'right',round(100*np.linalg.norm(X[1]-X[2]),1))
