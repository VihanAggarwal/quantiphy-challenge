import cv2, numpy as np, json, sys
render=sys.argv[1] if len(sys.argv)>1 else 'captured_0031'
tr=json.load(open('track_captured_0031x.json'))
def fit_circle(P):
    A=np.c_[2*P[:,0],2*P[:,1],np.ones(len(P))]; b=(P**2).sum(1)
    c=np.linalg.lstsq(A,b,rcond=None)[0]; r=np.sqrt(c[2]+c[0]**2+c[1]**2); return c[0],c[1],r
res=[]
for i in range(14,44):
    f=cv2.imread('frames/%s_%02d.png'%(render,i)).astype(float)
    hsv=cv2.cvtColor(f.astype(np.uint8),cv2.COLOR_BGR2HSV).astype(float)
    # yellowness: G+R-2B
    g=(f[...,1]+f[...,2])/2-f[...,0]
    g=cv2.GaussianBlur(g,(0,0),0.8)
    w=tr[i]['tennis']; cx,cy=w['cx'],w['cy']; r0=w['w']/2
    pts=[]
    for ang in np.linspace(0,2*np.pi,90,endpoint=False):
        rs=np.arange(max(2,r0*0.4),r0*1.6,0.1)
        xs=cx+rs*np.cos(ang); ys=cy+rs*np.sin(ang)
        prof=cv2.remap(g.astype(np.float32),xs.astype(np.float32).reshape(1,-1),ys.astype(np.float32).reshape(1,-1),cv2.INTER_LINEAR).ravel()
        d=np.gradient(prof); k=np.argmin(d); pts.append((xs[k],ys[k],d[k],ang))
    pts=np.array(pts); P=pts[:,:2]; keep=np.ones(len(P),bool)
    for it in range(4):
        x0,y0,r=fit_circle(P[keep]); dist=np.hypot(P[:,0]-x0,P[:,1]-y0)-r
        keep=np.abs(dist)<max(1.0,2.5*np.std(dist[keep]))
    x0,y0,r=fit_circle(P[keep])
    res.append(dict(i=i,cx=x0,cy=y0,d=2*r))
    print(i,'c=(%.1f,%.1f) d=%.2f n=%d R(f711,6.7)=%.1f'%(x0,y0,2*r,keep.sum(),711*6.7/(2*r)))
json.dump(res,open('circT_%s.json'%render,'w'))
