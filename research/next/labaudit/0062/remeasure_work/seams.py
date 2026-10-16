import cv2, numpy as np
from edgefit import bilinear
g=cv2.cvtColor(cv2.imread('median_bg.png'),cv2.COLOR_BGR2GRAY).astype(np.float32)
g=cv2.GaussianBlur(g,(3,3),0)
def dark_line(p,q,half=8):
    p=np.array(p,float); q=np.array(q,float); d=q-p; L=np.linalg.norm(d); d/=L; nrm=np.array([-d[1],d[0]])
    pts=[]
    for s in np.arange(0,L,2):
        c=p+s*d; t=np.arange(-half,half+0.01,0.25)
        prof=bilinear(g,c[0]+t*nrm[0],c[1]+t*nrm[1])
        k=np.argmin(prof)
        if 2<k<len(t)-3 and (np.median(prof)-prof[k])>8:
            # parabolic refine
            y0,y1,y2=prof[k-1],prof[k],prof[k+1]; off=0.5*(y0-y2)/(y0-2*y1+y2+1e-9)
            pts.append(c+(t[k]+off*0.25)*nrm)
    pts=np.array(pts)
    vx,vy,x0,y0=cv2.fitLine(pts.astype(np.float32),cv2.DIST_HUBER,0,0.01,0.01).ravel()
    line=np.cross([x0,y0,1.],[x0+vx,y0+vy,1.])
    res=(np.c_[pts,np.ones(len(pts))]@line)/np.hypot(line[0],line[1])
    return line,len(pts),float(np.sqrt(np.mean(res**2)))
seams={'A':((985,4),(903,218)),'B':((1129,4),(992,288)),'C':((1276,110),(1109,368))}
L={}
for k,(p,q) in seams.items():
    L[k]=dark_line(p,q); print(k,L[k][1:],np.round(L[k][0]/np.linalg.norm(L[k][0][:2]),4))
f=711.;cx=640.;cy=360.
Kinv=np.linalg.inv(np.array([[f,0,cx],[0,f,cy],[0,0,1]]))
lines=np.array([L[k][0]/np.linalg.norm(L[k][0][:2]) for k in L])
# least squares VP: minimize sum (l.v)^2 with v homogeneous
u,s,vt=np.linalg.svd(lines); vp=vt[-1]; vp=vp/vp[2]
print('VP vertical (all)',np.round(vp[:2],1))
for a,b in [('A','B'),('B','C'),('A','C')]:
    X=np.cross(L[a][0],L[b][0]); X=X/X[2]; d=Kinv@X; d/=np.linalg.norm(d); d=d if d[1]>0 else -d
    print(a,b,'VP',np.round(X[:2],1),'n',np.round(d,4))
d=Kinv@vp; d/=np.linalg.norm(d); d=d if d[1]>0 else -d
print('n from seams',np.round(d,4),' board-fit n',np.round(np.load('n_fit_711.npy')[:3],4),' angle deg',round(np.degrees(np.arccos(d@np.load('n_fit_711.npy')[:3])),2))
np.save('n_seams.npy',d)
