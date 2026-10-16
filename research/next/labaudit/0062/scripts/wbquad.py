import cv2, numpy as np, json
from common import *
X=load('x')
def board_mask(f):
    g=f.max(axis=2); m=(g>60).astype(np.uint8)
    k,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    i=1+np.argmax(st[1:,4]); return (lab==i).astype(np.uint8)
def lineint(l1,l2):
    p=np.cross(l1,l2); return p[:2]/p[2]
def fitline(pts):
    c=pts.mean(0); u,s,vt=np.linalg.svd(pts-c); d=vt[0]; nrm=np.array([-d[1],d[0]])
    return np.array([nrm[0],nrm[1],-nrm@c]), s
out={}
for n in range(17,49):
    m=board_mask(X[n])
    cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cs,key=cv2.contourArea).reshape(-1,2).astype(float)
    hull=cv2.convexHull(c.astype(np.float32)).reshape(-1,2)
    peri=cv2.arcLength(hull.reshape(-1,1,2),True)
    for eps in np.linspace(0.01,0.1,50):
        ap=cv2.approxPolyDP(hull.reshape(-1,1,2),eps*peri,True).reshape(-1,2)
        if len(ap)<=4: break
    if len(ap)!=4: print(n,'no quad',len(ap)); continue
    # refine each edge using contour points near the middle of edge
    lines=[]
    for i in range(4):
        a,b=ap[i],ap[(i+1)%4]
        ab=b-a; L=np.linalg.norm(ab); u=ab/L; nn=np.array([-u[1],u[0]])
        t=(c-a)@u; d=(c-a)@nn
        sel=(t>0.2*L)&(t<0.8*L)&(np.abs(d)<20)
        P=c[sel]
        for it in range(5):
            l,s=fitline(P)
            r=P@l[:2]+l[2]
            med=np.median(r)
            keep=np.abs(r-med)<2.5
            # keep the outer-most consistent band
            P=P[keep]
        lines.append(l)
    corners=np.array([lineint(lines[i-1],lines[i]) for i in range(4)])
    out[n]=corners.tolist()
    print(n, np.round(corners,1).tolist(), 'touch' if (c[:,1].max()>=715 or c[:,0].max()>=1275) else '')
json.dump(out,open(O+'wbquads.json','w'))
