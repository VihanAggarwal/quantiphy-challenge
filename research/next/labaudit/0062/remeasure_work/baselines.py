import cv2, numpy as np
from edgefit import bilinear, edge_line
from seams import dark_line, L as SL
gcol=cv2.imread('median_bg.png'); g=cv2.cvtColor(gcol,cv2.COLOR_BGR2GRAY).astype(np.float32)
f=711.;cx=640.;cy=360.
Kinv=np.linalg.inv(np.array([[f,0,cx],[0,f,cy],[0,0,1]]))
# right baseline: dark line along wall base, sample in segments to check curvature
p=np.array([700.,95.]); q=np.array([1275.,497.])
d=q-p; Ln=np.linalg.norm(d); d/=Ln; nrm=np.array([-d[1],d[0]])
pts=[]
for s in np.arange(0,Ln,3):
    c=p+s*d; t=np.arange(-12,12.01,0.25)
    prof=bilinear(g,c[0]+t*nrm[0],c[1]+t*nrm[1])
    # wall base: transition from bright wall (one side) to dark baseboard; use strongest gradient
    gr=np.diff(prof); k=np.argmax(np.abs(gr))
    pts.append(c+t[k]*nrm)
pts=np.array(pts)
vx,vy,x0,y0=cv2.fitLine(pts.astype(np.float32),cv2.DIST_HUBER,0,0.01,0.01).ravel()
lr=np.cross([x0,y0,1.],[x0+vx,y0+vy,1.])
res=(np.c_[pts,np.ones(len(pts))]@lr)/np.hypot(lr[0],lr[1])
print('right baseline rms',round(float(np.sqrt(np.mean(res**2))),2))
for a in range(0,len(res),20): print('   s',a*3,'xy',np.round(pts[a],0),'res',round(float(res[a]),2))
np.save('rb_pts.npy',pts)
