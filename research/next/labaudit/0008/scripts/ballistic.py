# Fit 3D ballistic arcs (g=9.8 along -n) to the 2D ball centre track; scale from g and f.
import cv2, numpy as np, sys
sys.path.insert(0,"/home/user/quantiphy-challenge/research/next/labaudit/0008/scripts"); from lm import least_squares
v=sys.argv[1] if len(sys.argv)>1 else 'captured_0008'
fpx=float(sys.argv[2]) if len(sys.argv)>2 else 711.
F='/home/user/quantiphy-challenge/research/next/labaudit/0008/frames/'
n=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0008/scripts/normal.npy')
cx,cy=640.,360.
def centre(i):
    im=cv2.imread(f'{F}{v}_f{i:02d}.png'); hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    m=(((hsv[...,0]<=18)|(hsv[...,0]>=170))&(hsv[...,1]>120)&(hsv[...,2]>70)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    nn,lab,st,_=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    return x+w/2, y+h/2, w/2, h/2
T={i:centre(i) for i in range(22,49)}
for i in sorted(T): print(i, ['%.1f'%q for q in T[i]])
g=9.8*(-n)
def proj(X): return np.c_[fpx*X[:,0]/X[:,2]+cx, fpx*X[:,1]/X[:,2]+cy]
def fit(frames,t0):
    t=np.array(frames)/24.-t0; obs=np.array([T[i][:2] for i in frames])
    def model(p):
        X0=p[:3]; V=p[3:]
        return X0+np.outer(t,V)+0.5*np.outer(t**2,g)
    def res(p): return (proj(model(p))-obs).ravel()
    best=None
    for z in [1.2,1.5,1.8,2.2]:
        u,vv=obs[0]; X0=np.array([(u-cx)/fpx*z,(vv-cy)/fpx*z,z])
        r=least_squares(res,np.r_[X0,0,0,0])
        if best is None or r.cost<best.cost: best=r
    X=model(best.x); return best, X, t
# fall arc
for frames in [list(range(24,30)),list(range(23,30)),list(range(24,29))]:
    r,X,t=fit(frames,1.0)
    rng=np.linalg.norm(X,axis=1); ht=X@n
    print('FALL frames',frames[0],'-',frames[-1],'rms px %.2f'%np.sqrt(np.mean(r.fun**2)))
    for i,tt,R_,H in zip(frames,t,rng,ht): print('   f%d range %.3f  n-coord %.3f'%(i,R_,H))
    V=r.x[3:]; print('   V(t=1.0)=',np.round(V,3),'|V|=%.2f'%np.linalg.norm(V),'vertical comp %.2f'%(V@n))
    # velocity at 1.2
    V12=V+g*0.2; print('   |V(1.2)|=%.2f'%np.linalg.norm(V12))
# rebound arc
for frames in [list(range(31,41)),list(range(32,41)),list(range(31,40))]:
    r,X,t=fit(frames,1.5)
    rng=np.linalg.norm(X,axis=1); ht=X@n
    print('REB frames',frames[0],'-',frames[-1],'rms px %.2f'%np.sqrt(np.mean(r.fun**2)))
    for i,tt,R_,H in zip(frames,t,rng,ht): print('   f%d range %.3f  n-coord %.3f'%(i,R_,H))
    V=r.x[3:]; vz=V@n; print('   V(t=1.5)=',np.round(V,3),'vert %.2f'%vz)
    tap=1.5+vz/9.8; print('   apex t=%.3f'%tap)
