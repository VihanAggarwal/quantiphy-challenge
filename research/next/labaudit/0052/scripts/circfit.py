import cv2, numpy as np, json, sys
def fit_circle(pts):
    x,y=pts[:,0],pts[:,1]
    A=np.c_[2*x,2*y,np.ones(len(x))]; b=x**2+y**2
    s,*_=np.linalg.lstsq(A,b,rcond=None)
    cx,cy=s[0],s[1]; r=np.sqrt(s[2]+cx**2+cy**2); return cx,cy,r
def edge_circle(img, c, r0, angles_deg, band=(0.75,1.3), iters=4):
    g=cv2.GaussianBlur(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(np.float32),(3,3),0)
    gx=cv2.Sobel(g,cv2.CV_32F,1,0,ksize=3); gy=cv2.Sobel(g,cv2.CV_32F,0,1,ksize=3)
    cx,cy=c; r=r0
    for it in range(iters):
        pts=[]
        for a in np.radians(angles_deg):
            ux,uy=np.cos(a),np.sin(a)
            rs=np.arange(band[0]*r,band[1]*r,0.5)
            xs=cx+rs*ux; ys=cy+rs*uy
            ok=(xs>1)&(xs<1278)&(ys>1)&(ys<718)
            if ok.sum()<5: continue
            xs,ys,rs=xs[ok],ys[ok],rs[ok]
            # radial gradient (ball darker than surround typically -> positive outward); use abs
            gr=np.abs(cv2.remap(gx,xs.astype(np.float32)[None],ys.astype(np.float32)[None],cv2.INTER_LINEAR)[0]*ux+
                      cv2.remap(gy,xs.astype(np.float32)[None],ys.astype(np.float32)[None],cv2.INTER_LINEAR)[0]*uy)
            i=np.argmax(gr)
            if gr[i]>20: pts.append((xs[i],ys[i],gr[i]))
        pts=np.array(pts)
        if len(pts)<6: break
        cx,cy,r=fit_circle(pts[:,:2])
        # robust: drop outliers
        res=np.hypot(pts[:,0]-cx,pts[:,1]-cy)-r
        keep=np.abs(res)<max(2.5,2*np.median(np.abs(res)))
        if keep.sum()>=6: cx,cy,r=fit_circle(pts[keep,:2])
    return cx,cy,r,pts
