import numpy as np
c=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0028/scripts/corners.npy')  # BL,BR,FR,FL
CX,CY=640,360
def solve(f):
    d=np.array([[(u-CX)/f,(v-CY)/f,1.0] for u,v in c])
    # P_i = l_i d_i ; BL + FR = BR + FL  -> l0 d0 + l2 d2 - l1 d1 - l3 d3 = 0, l0=1
    A=np.stack([-d[1],d[2],-d[3]],1); b=-d[0]
    l,res,_,_=np.linalg.lstsq(A,b,rcond=None); lam=np.r_[1,l[0],l[1],l[2]]
    P=lam[:,None]*d
    back=np.linalg.norm(P[1]-P[0]); front=np.linalg.norm(P[2]-P[3]); left=np.linalg.norm(P[3]-P[0]); right=np.linalg.norm(P[2]-P[1])
    ang=np.degrees(np.arccos(np.dot(P[1]-P[0],P[3]-P[0])/back/left))
    return P,back,front,left,right,ang
for f in [690,700,711,720,730,750]:
    P,b,fr,l,r,a=solve(f)
    print(f,'width/depth',round((b+fr)/(l+r),3),'angle',round(a,2))
f=711
P,b,fr,l,r,a=solve(f)
W=(b+fr)/2; D=(l+r)/2
for s_w,s_d in [(76.0,60.3),(60.3,76.0)]:
    print('if width',s_w,'scale from width',s_w/W,'from depth',s_d/D)
