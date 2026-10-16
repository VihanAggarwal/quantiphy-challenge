import cv2, numpy as np, json, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0047/scripts')
from track import *
rend=sys.argv[1] if len(sys.argv)>1 else 'x'
f_px=float(sys.argv[2]) if len(sys.argv)>2 else F
res={}
for n in range(14,49):
    f=cv2.imread(D+f'frames/x_{n:02d}.png').astype(int)
    green=(f[:,:,1]>150)&(f[:,:,0]<110)&(f[:,:,2]<110)
    fg=(~green).astype(np.uint8)
    fg[705:]=0
    dt=cv2.distanceTransform(fg,cv2.DIST_L2,5)
    y0,x0=np.unravel_index(np.argmax(dt),dt.shape); r0=dt[y0,x0]
    er=cv2.erode(fg,np.ones((3,3),np.uint8))
    bd=(fg==1)&(er==0)
    bd[703:]=False
    ys,xs=np.nonzero(bd)
    pts=np.stack([xs,ys],1).astype(float)
    # initial circle from inscribed; grow radius by searching for boundary band
    cx,cy,r=float(x0),float(y0),float(r0)
    for it in range(6):
        dd=np.hypot(pts[:,0]-cx,pts[:,1]-cy)
        sel=np.abs(dd-r)<max(8,0.12*r)
        if it==0: sel=(dd>r-3)&(dd<r*1.35)
        P=pts[sel]
        # algebraic circle fit
        A=np.c_[2*P[:,0],2*P[:,1],np.ones(len(P))]; b=(P**2).sum(1)
        sol=np.linalg.lstsq(A,b,rcond=None)[0]
        cx,cy=sol[0],sol[1]; r=np.sqrt(sol[2]+cx**2+cy**2)
    dd=np.hypot(pts[:,0]-cx,pts[:,1]-cy)
    P=pts[np.abs(dd-r)<max(8,0.1*r)]
    c0=rays(np.array([cx]),np.array([cy]),f_px)[0]
    a0=np.arctan(r/f_px)
    c,a,rr,w=fit_cone(P,c0,a0,f_px)
    pc=proj(c,f_px)
    res[n]=dict(cx=cx,cy=cy,r=r,npts=int(len(P)),inl=int(w.sum()),cone_c=c.tolist(),alpha=float(a),pc=pc.tolist(),
                rms=float(np.sqrt(np.mean((rr[w>0])**2))*f_px))
    print(n,f'circ ({cx:.1f},{cy:.1f}) r={r:.1f}  cone pc=({pc[0]:.1f},{pc[1]:.1f}) alpha={np.degrees(a):.3f} sin={np.sin(a):.4f} n={len(P)} inl={int(w.sum())} rms={res[n]["rms"]:.2f}px')
json.dump(res,open(D+f'fit_{rend}_{int(f_px)}.json','w'),indent=1)
