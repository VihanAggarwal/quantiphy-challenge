import cv2, numpy as np, sys
fr = int(sys.argv[1]) if len(sys.argv)>1 else 58
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0010.mp4'); i=0
while True:
    ok,f=c.read()
    if not ok or i==fr: break
    i+=1
g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32)
g = cv2.GaussianBlur(g,(0,0),1.0)
cx0, cy0 = 1733, 1164
# radial profiles: for each angle, find the outer rim edge (strong gradient) between r=85 and r=125
gx = cv2.Sobel(g, cv2.CV_32F,1,0,ksize=3); gy = cv2.Sobel(g, cv2.CV_32F,0,1,ksize=3)
pts=[]
for a in np.linspace(0,2*np.pi,360,endpoint=False):
    rs = np.arange(85,125,0.5)
    xs = cx0+rs*np.cos(a); ys = cy0+rs*np.sin(a)
    gr = cv2.remap(gx, xs.astype(np.float32).reshape(1,-1), ys.astype(np.float32).reshape(1,-1), cv2.INTER_LINEAR).ravel()*np.cos(a) + \
         cv2.remap(gy, xs.astype(np.float32).reshape(1,-1), ys.astype(np.float32).reshape(1,-1), cv2.INTER_LINEAR).ravel()*np.sin(a)
    # outer edge of dark rim against lighter background: intensity increases outward -> positive radial gradient
    k = np.argmax(gr)
    if gr[k] > 15: pts.append((xs[k], ys[k], a, gr[k]))
pts = np.array(pts)
print('n pts', len(pts))
P = pts[:,:2].astype(np.float32)
for it in range(4):
    (ex,ey),(MA,ma),ang = cv2.fitEllipse(P)
    # residual: distance approx
    t = np.deg2rad(ang)
    dx = P[:,0]-ex; dy = P[:,1]-ey
    u = dx*np.cos(t)+dy*np.sin(t); v = -dx*np.sin(t)+dy*np.cos(t)
    r = np.sqrt((u/(MA/2))**2+(v/(ma/2))**2)-1
    s = np.median(np.abs(r))*1.4826+1e-4
    keep = np.abs(r)<3*s
    print('iter',it,'centre (%.1f,%.1f) axes w=%.2f h=%.2f ang=%.2f  n=%d  med|r|*R=%.2f'%(ex,ey,MA,ma,ang,len(P),np.median(np.abs(r))*100))
    P = P[keep]
vis = f[1030:1300, 1590:1880].copy()
vis = cv2.resize(vis,None,fx=3,fy=3,interpolation=cv2.INTER_CUBIC)
for x,y,a,gv in pts:
    cv2.circle(vis,(int((x-1590)*3),int((y-1030)*3)),2,(0,0,255),-1)
cv2.imwrite('frames/wheel_pts.png', vis)
