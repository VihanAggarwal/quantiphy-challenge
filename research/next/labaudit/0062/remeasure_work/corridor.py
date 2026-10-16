import cv2, numpy as np
from edgefit import bilinear
g=cv2.cvtColor(cv2.imread('median_bg.png'),cv2.COLOR_BGR2GRAY).astype(np.float32)
f=711.;cx=640.;cy=360.
Kinv=np.linalg.inv(np.array([[f,0,cx],[0,f,cy],[0,0,1]]))
def strongest_edge_line(p,q,half=12,step=3,rng=None):
    p=np.array(p,float); q=np.array(q,float); d=q-p; Ln=np.linalg.norm(d); d/=Ln; nrm=np.array([-d[1],d[0]])
    pts=[]
    for s in np.arange(0,Ln,step):
        c=p+s*d; t=np.arange(-half,half+0.01,0.25)
        prof=bilinear(g,c[0]+t*nrm[0],c[1]+t*nrm[1]); gr=np.diff(prof); k=np.argmax(np.abs(gr))
        if abs(gr[k])>2: pts.append(c+(t[k]+0.125)*nrm)
    pts=np.array(pts)
    if rng is not None: pts=pts[(pts[:,1]>rng[0])&(pts[:,1]<rng[1])]
    vx,vy,x0,y0=cv2.fitLine(pts.astype(np.float32),cv2.DIST_HUBER,0,0.01,0.01).ravel()
    l=np.cross([x0,y0,1.],[x0+vx,y0+vy,1.]); res=(np.c_[pts,np.ones(len(pts))]@l)/np.hypot(l[0],l[1])
    return l,pts,res
ll,pl,rl=strongest_edge_line((132,280),(121,700))
print('left baseline rms',round(float(np.sqrt(np.mean(rl**2))),2),'n',len(pl))
for a in range(0,len(rl),15): print('   ',np.round(pl[a],1),round(float(rl[a]),2))
rb=np.load('rb_pts.npy'); rb=rb[(rb[:,0]>740)&(rb[:,0]<1220)]
vx,vy,x0,y0=cv2.fitLine(rb.astype(np.float32),cv2.DIST_HUBER,0,0.01,0.01).ravel(); lr=np.cross([x0,y0,1.],[x0+vx,y0+vy,1.])
vp=np.cross(ll,lr); vp=vp/vp[2]; dc=Kinv@vp; dc/=np.linalg.norm(dc)
print('corridor VP',np.round(vp[:2],1),'dir',np.round(dc,4))
nb=np.load('n_fit_711.npy')[:3]; ns=np.load('n_seams.npy')
print('n_board . dc =',round(float(nb@dc),4),' (deg off perpendicular',round(float(np.degrees(np.arcsin(abs(nb@dc)))),2),')')
print('n_seams . dc =',round(float(ns@dc),4),' (deg',round(float(np.degrees(np.arcsin(abs(ns@dc)))),2),')')
np.save('dc.npy',dc); np.save('lines_lr.npy',np.array([ll,lr]))
