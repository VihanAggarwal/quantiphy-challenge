import cv2, numpy as np, sys, json
sys.path.insert(0,'scripts')
from frames import load
res={}
for r in ['','s']:
    fr=load(r)
    im=np.median(np.stack([f.astype(np.float32) for f in fr[30:49]]),0).astype(np.uint8)
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    m=((hsv[...,2]>215)&(hsv[...,1]<40)).astype(np.uint8)
    roi=np.zeros_like(m); roi[290:440,490:625]=1; m*=roi
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); m=(lab==k).astype(np.uint8)
    cv2.imwrite(f'img/boardmask_{r or "o"}.png',m*255)
    cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cs,key=cv2.contourArea)[:,0,:].astype(float)
    ap=cv2.approxPolyDP(c.astype(np.float32),5,True)[:,0,:]
    hull=cv2.convexHull(c.astype(np.float32))[:,0,:]
    # approx quad
    q=cv2.approxPolyDP(hull,8,True)[:,0,:]
    print(r or 'o','approx quad',q.tolist())
    # refine: assign contour points to nearest quad edge (excluding corners region), fit lines
    Q=q if len(q)==4 else None
    if Q is None: continue
    lines=[]
    for i in range(4):
        a=Q[i]; b=Q[(i+1)%4]
        d=b-a; L=np.linalg.norm(d); t=d/L; nrm=np.array([-t[1],t[0]])
        rel=c-a; s=rel@t; dist=np.abs(rel@nrm)
        sel=(s>0.2*L)&(s<0.8*L)&(dist<4)
        pts=c[sel]
        vx,vy,x0,y0=cv2.fitLine(pts.astype(np.float32),cv2.DIST_L2,0,0.01,0.01).ravel()
        lines.append((np.array([x0,y0]),np.array([vx,vy])))
    corners=[]
    for i in range(4):
        (p1,d1),(p2,d2)=lines[i-1],lines[i]
        A=np.array([d1,-d2]).T; s=np.linalg.solve(A,p2-p1)
        corners.append((p1+s[0]*d1).tolist())
    print('corners',np.round(corners,1).tolist())
    res[r or 'o']=corners
json.dump(res,open('board_corners.json','w'))
