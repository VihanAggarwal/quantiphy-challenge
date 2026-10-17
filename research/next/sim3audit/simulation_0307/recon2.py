import numpy as np,sys,cv2
c=np.array([1280.,720.])
fn=sys.argv[1]; clip=sys.argv[2]
f=float(sys.argv[3]); fps=float(sys.argv[4]); tag=sys.argv[5] if len(sys.argv)>5 else ''
T=np.load(fn)
idx=np.arange(1,T.shape[1])
def track_fit(tr,e):
    d=tr[idx]-e; rho=np.linalg.norm(d,axis=1)
    ang=np.arctan2(d[:,1],d[:,0]); a0=np.angle(np.mean(np.exp(1j*ang)))
    u=np.array([np.cos(a0),np.sin(a0)]); perp=d@np.array([-u[1],u[0]])
    W=rho; M=np.stack([np.ones(len(idx)),idx.astype(float)],1)
    A,B=np.linalg.lstsq(M*W[:,None],(1/rho)*W,rcond=None)[0]
    along=rho-1/(A+B*idx)
    return A,B,np.sqrt(np.mean(perp**2+along**2))
def total(T,e): return np.sqrt(np.mean([track_fit(tr,e)[2]**2 for tr in T]))
e=np.array([-750.,-475.])
keep=np.ones(len(T),bool)
for rnd in range(3):
    step=40.
    for it in range(7):
        best=(total(T[keep],e),e)
        for dx in (-2,-1,0,1,2):
            for dy in (-2,-1,0,1,2):
                ee=e+np.array([dx,dy])*step; s=total(T[keep],ee)
                if s<best[0]: best=(s,ee)
        e=best[1]; step/=2.5
    rr=np.array([track_fit(tr,e)[2] for tr in T])
    keep=rr<max(1.5,3*np.median(rr))
print(clip,'VP',e.round(1),'kept',keep.sum(),'/',len(T),'median rms',np.median(rr[keep]).round(2))
T=T[keep]; res=[track_fit(tr,e) for tr in T]
n=np.array([r[0]/r[1] for r in res])
v=np.array([(e[0]-c[0])/f,(e[1]-c[1])/f,1.]); vh=v/np.linalg.norm(v)
Vzf=22.16*vh[2]/fps
a=(e[1]-c[1])/f; up=np.array([0,-1,a]); up/=np.linalg.norm(up)
s=np.cross(vh,up); s/=np.linalg.norm(s); upo=np.cross(s,vh)
ref=24
x=T[:,ref]; Z=Vzf*(n+ref)
P=np.stack([(x[:,0]-c[0])/f*Z,(x[:,1]-c[1])/f*Z,Z],1)
B=np.stack([P@vh,P@s,P@upo],1)
np.save(f'B_{clip}{tag}.npy',B); np.save(f'Tk_{clip}{tag}.npy',T)
fo=B[:,0];la=B[:,1]
print('fore extent',(fo.max()-fo.min()).round(2),'lat extent',(la.max()-la.min()).round(2))
# range of points at t=1 (frame ref) 
rng=np.linalg.norm(P,axis=1)
print('range at frame',ref,'min/med/max',rng.min().round(2),np.median(rng).round(2),rng.max().round(2))
