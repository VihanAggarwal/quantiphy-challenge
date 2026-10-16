import sys, cv2, numpy as np; sys.path.insert(0,'scripts')
from geo import *
rng=np.random.default_rng(0)
def board_corners(n):
    im=cv2.imread(f'other/0062x_{n:02d}.png').astype(int)
    # white board: bright & low saturation
    m=((im.min(2)>170)).astype(np.uint8); m[690:,1000:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    k,lab,st,cen=cv2.connectedComponentsWithStats(m)
    i=max(range(1,k),key=lambda j:st[j][4]); mm=(lab==i).astype(np.uint8)
    cs,_=cv2.findContours(mm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cs,key=cv2.contourArea)
    pts=c.reshape(-1,2).astype(float)
    hull=cv2.convexHull(c)
    for e in np.arange(2,40,0.5):
        ap=cv2.approxPolyDP(hull,e,True)
        if len(ap)==4: break
    quad=ap.reshape(-1,2).astype(float)
    lines=[]
    for j in range(4):
        p0=quad[j]; p1=quad[(j+1)%4]; d=p1-p0; L=np.linalg.norm(d); d/=L; nr=np.array([-d[1],d[0]])
        t=(pts-p0)@d; s=(pts-p0)@nr
        sel=(t>0.2*L)&(t<0.8*L)&(np.abs(s)<6)
        q=pts[sel]
        # robust line: iterate
        mu=q.mean(0); U,S,Vt=np.linalg.svd(q-mu); dd=Vt[0]
        for it in range(3):
            nn=np.array([-dd[1],dd[0]]); r=(q-mu)@nn; q2=q[np.abs(r)<1.5]
            mu=q2.mean(0); U,S,Vt=np.linalg.svd(q2-mu); dd=Vt[0]
        lines.append((mu,dd,len(q)))
    corn=[]
    for j in range(4):
        (m1,d1,_),(m2,d2,_)=lines[j-1],lines[j]
        t=np.linalg.solve(np.c_[d1,-d2],m2-m1); corn.append(m1+t[0]*d1)
    return np.array(corn), mm.sum(), [l[2] for l in lines]
for n in (24,40,48):
    corn,a,nl=board_corners(n)
    print('frame',n,'corners',np.round(corn,1).tolist(),'npts',nl)
    for name,dn,H in [('roll',DOWN_ROLL,1.689),('noroll',DOWN_NOROLL,1.711),('tofit',None,1.704)]:
        if dn is None:
            a,b=np.radians(34.5),np.radians(-0.4); dn=np.array([np.sin(b)*np.cos(a),np.cos(b)*np.cos(a),np.sin(a)])
        Q=np.array([floor_pt(u,v,H,dn,0.01) for u,v in corn])
        e=[np.linalg.norm(Q[(j+1)%4]-Q[j]) for j in range(4)]
        ang=[np.degrees(np.arccos((Q[j-1]-Q[j])@(Q[(j+1)%4]-Q[j])/np.linalg.norm(Q[j-1]-Q[j])/np.linalg.norm(Q[(j+1)%4]-Q[j]))) for j in range(4)]
        print('   %-7s edges cm'%name,np.round(np.array(e)*100,1),'angles',np.round(ang,1))
