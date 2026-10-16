import cv2, numpy as np, json
f0=711.; cx=640.; cy=360.
K=np.array([[f0,0,cx],[0,f0,cy],[0,0,1]])
def board_quad(i, thr_frac=0.5, src='o'):
    fo=cv2.imread('frames/%s_%02d.png'%(src,i)); g=cv2.cvtColor(fo,cv2.COLOR_BGR2GRAY).astype(float)
    fx=cv2.imread('frames/x_%02d.png'%i); hsv=cv2.cvtColor(fx,cv2.COLOR_BGR2HSV)
    m=((hsv[...,2]>170)&(hsv[...,1]<40)).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m); j=1+np.argmax(st[1:,4]); m=(lab==j).astype(np.uint8)
    roi=cv2.dilate(m,np.ones((25,25),np.uint8))
    inner=cv2.erode(m,np.ones((9,9),np.uint8))
    ring=(roi>0)&(cv2.dilate(m,np.ones((13,13),np.uint8))==0)
    wv=np.median(g[inner>0]); bv=np.median(g[ring])
    t=bv+thr_frac*(wv-bv)
    b=((g>t)&(roi>0)).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(b); j=1+np.argmax(st[1:,4]); b=(lab==j).astype(np.uint8)
    cnts,_=cv2.findContours(b,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cnts,key=cv2.contourArea).reshape(-1,2).astype(float)
    hull=cv2.convexHull(c.astype(np.float32)).reshape(-1,2)
    # find 4-corner approx via minimal area quad: approxPolyDP on hull with increasing eps
    for eps in np.linspace(0.01,0.1,50):
        ap=cv2.approxPolyDP(hull.reshape(-1,1,2),eps*cv2.arcLength(hull.reshape(-1,1,2),True),True).reshape(-1,2)
        if len(ap)<=4: break
    if len(ap)!=4: return None
    # order corners: by angle around centroid
    cc=ap.mean(0); ang=np.arctan2(ap[:,1]-cc[1],ap[:,0]-cc[0]); ap=ap[np.argsort(ang)]
    # refine lines using contour points on each side (trim ends)
    lines=[]
    for k in range(4):
        p,q=ap[k],ap[(k+1)%4]
        d=q-p; L=np.linalg.norm(d); d/=L; nrm=np.array([-d[1],d[0]])
        s=(c-p)@d; o=(c-p)@nrm
        sel=(s>0.2*L)&(s<0.8*L)&(np.abs(o)<6)
        pts=c[sel]
        if len(pts)<10: return None
        vx,vy,x0,y0=cv2.fitLine(pts.astype(np.float32),cv2.DIST_HUBER,0,0.01,0.01).ravel()
        lines.append(np.cross([x0,y0,1],[x0+vx,y0+vy,1]))
    corners=[]
    for k in range(4):
        X=np.cross(lines[k-1],lines[k]); corners.append(X[:2]/X[2])
    return np.array(corners), (wv,bv,t)
if __name__=='__main__':
    out={}
    for i in range(17,49):
        r=board_quad(i)
        if r is None: print(i,'fail'); continue
        out[i]=r[0].tolist()
        print(i, np.round(r[0],1).tolist(), np.round(r[1],0))
    json.dump(out,open('board_corners_o.json','w'))
