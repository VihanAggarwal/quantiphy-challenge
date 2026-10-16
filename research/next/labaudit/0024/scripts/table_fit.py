import cv2, numpy as np
import sys; sys.path.insert(0,"/home/user/quantiphy-challenge/research/next/labaudit/0024/scripts"); from lsq import least_squares
D='/home/user/quantiphy-challenge/research/next/labaudit/0024/'
BL=[(x,y) for x,y in zip(range(430,620,20),[466,464,462,461,460,458,457,455,454,452])]
BR=[(900,455),(920,460),(940,462),(960,464),(980,467),(1000,470),(1020,473),(1040,475),(1060,478),(1080,482)]
FL=[(430,475),(445,481),(460,489),(475,496),(490,503),(505,509),(520,516),(535,524),(550,531),(565,538),(580,545),(595,552)]
FR=[(870,536),(885,533),(900,531),(915,528),(930,526),(945,523),(960,521),(975,518),(990,515),(1005,513),(1020,511),(1035,508),(1050,505),(1065,503),(1080,500)]
def run(f,a=0.603,b=0.760,verbose=True):
    K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
    obj=np.array([[0,a,0],[0,0,0],[b,0,0],[b,a,0]],float) # L F R B
    edges={'FL':(0,1,FL),'FR':(1,2,FR),'BR':(2,3,BR),'BL':(3,0,BL)}
    def res(p):
        rv,tv=p[:3],p[3:]
        pr,_=cv2.projectPoints(obj,rv,tv,K,None); pr=pr.reshape(-1,2)
        r=[]
        for k,(i,j,pts) in edges.items():
            A,B=pr[i],pr[j]; d=B-A; n=np.array([-d[1],d[0]])/np.linalg.norm(d)
            for p_ in pts: r.append((np.array(p_)-A)@n)
        return np.array(r)
    img=np.array([[411.7,466.4],[643.6,574.7],[1142.7,489.4],[790.6,438.8]])
    ok,rv,tv=cv2.solvePnP(obj,img,K,None,flags=cv2.SOLVEPNP_IPPE)
    s=least_squares(res,np.r_[rv.ravel(),tv.ravel()])
    rv,tv=s.x[:3],s.x[3:]
    R,_=cv2.Rodrigues(rv); P=(R@obj.T).T+tv
    pr,_=cv2.projectPoints(obj,rv,tv,K,None)
    if verbose: print(f,'rms',round(np.sqrt(np.mean(s.fun**2)),2),'corners px',np.round(pr.reshape(-1,2),1).tolist(),'ranges',np.round(np.linalg.norm(P,axis=1),3))
    return R,tv,np.sqrt(np.mean(s.fun**2))
if __name__=='__main__':
    for f in [650,680,711,740,780,831]: run(f)
    R,t,_=run(711)
    np.save(D+'scripts/table_pose_711.npy',np.r_[R.ravel(),t])
