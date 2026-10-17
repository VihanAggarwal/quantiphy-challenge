import cv2, numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0014/scripts')
from frames import load
from tplane import *
res={}
for r in ['','s','x']:
    fr=load(r)
    im=np.median(np.stack([f.astype(np.float32) for f in fr[30:49]]),0).astype(np.uint8)
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    H,S,V=[hsv[...,i].astype(int) for i in range(3)]
    m=((H>75)&(H<105)&(S>25)&(V>150)).astype(np.uint8)
    roi=np.zeros_like(m); roi[370:450,610:700]=1; m*=roi
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n_,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); m=(lab==k).astype(np.uint8)
    cv2.imwrite(f'img/bookmask_{r or "o"}.png',cv2.resize(m*255,None,fx=1,fy=1))
    cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cs,key=cv2.contourArea)[:,0,:].astype(float)
    hull=cv2.convexHull(c.astype(np.float32))[:,0,:]
    q=cv2.approxPolyDP(hull,4,True)[:,0,:]
    if len(q)!=4:
        q=cv2.boxPoints(cv2.minAreaRect(c.astype(np.float32)))
    lines=[]
    for i in range(4):
        a=q[i]; b=q[(i+1)%4]; d=b-a; L=np.linalg.norm(d); t=d/L; nr=np.array([-t[1],t[0]])
        rel=c-a; s=rel@t; dist=np.abs(rel@nr); sel=(s>0.2*L)&(s<0.8*L)&(dist<3)
        vx,vy,x0,y0=cv2.fitLine(c[sel].astype(np.float32),cv2.DIST_L2,0,0.01,0.01).ravel()
        lines.append((np.array([x0,y0]),np.array([vx,vy])))
    cor=[]
    for i in range(4):
        (p1,d1),(p2,d2)=lines[i-1],lines[i]
        s=np.linalg.solve(np.array([d1,-d2]).T,p2-p1); cor.append(p1+s[0]*d1)
    cor=np.array(cor)
    print(r or 'o','area',int(m.sum()),'corners',np.round(cor,1).tolist())
    res[r or 'o']=cor.tolist()
json.dump(res,open('/home/user/quantiphy-challenge/research/next/labaudit2/0014/book_corners.json','w'))
