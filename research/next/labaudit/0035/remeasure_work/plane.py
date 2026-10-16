import numpy as np
W='/home/user/quantiphy-challenge/research/next/labaudit/0035/remeasure_work/'
M=np.load(W+'captured_0035bx_mask.npy')  # i,ex,ey,area,eqd,minor,major,wr,wt,wp,wm
f=711.; cx,cy=640,360; D=0.232; R=D/2
def ray(x,y):
    v=np.array([x-cx,y-cy,f]); return v/np.linalg.norm(v)
good=[i for i in range(len(M)) if i<=9 or (14<=i<=23) or (28<=i<=44)]
pts=[]
for i in good:
    _,x,y,area,eqd,mi,ma,*_=M[i]
    u=ray(x,y); c=u[2]
    rc=f*D/(eqd*c**1.5)
    pts.append((i,x,y,eqd,rc,*(rc*u)))
P=np.array(pts)
for r in P: print('%2d (%.1f,%.1f) eqd=%.1f rc=%.3f X=(%.3f,%.3f,%.3f)'%tuple(r))
# fit plane to moving frames 14..44 plus stationary
sel=P[:,0]>=14
X=P[sel,5:8]
c0=X.mean(0); U,S,Vt=np.linalg.svd(X-c0); n=Vt[2]
if n@c0<0: n=-n  # n points away from camera toward plane (downward-ish)
h=n@c0
res=(X-c0)@Vt[2]
print('normal',n,'dist cam->centre-plane',h,'rms resid',res.std(),'sing',S)
# stationary point distance to plane
for r in P[P[:,0]<=9][:1]:
    print('stationary centre height offset from plane (m):', n@r[5:8]-h)
np.save(W+'plane_size.npy',np.r_[n,h])
