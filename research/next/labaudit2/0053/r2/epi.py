import numpy as np, json, sys, cv2
f=711.;cx=640.;cy=360.
K=np.array([[f,0,cx],[0,f,cy],[0,0,1.]])
a,b=int(sys.argv[1]),int(sys.argv[2])
X=np.load(f'klt_{a}_{b}.npy'); x0,x1=X
def norm(x): return np.c_[(x[:,0]-cx)/f,(x[:,1]-cy)/f,np.ones(len(x))]
n0,n1=norm(x0),norm(x1)
C=np.cross(n0,n1)
rng=np.random.default_rng(0)
best=None
for it in range(3000):
    idx=rng.choice(len(C),2,replace=False)
    t=np.cross(C[idx[0]],C[idx[1]]); 
    if np.linalg.norm(t)<1e-12: continue
    t/=np.linalg.norm(t)
    # residual: distance (px) from x1 to the epipolar line through x0 and epipole
    l=np.cross(n0,np.tile(t,(len(n0),1)))  # line in normalized coords through x0 and t
    r=np.abs((l*n1).sum(1))/np.hypot(l[:,0],l[:,1])*f
    inl=r<1.0
    if best is None or inl.sum()>best[0]: best=(inl.sum(),t,inl)
k,t,inl=best
_,_,vt=np.linalg.svd(C[inl]); t=vt[-1]
l=np.cross(n0,np.tile(t,(len(n0),1))); r=np.abs((l*n1).sum(1))/np.hypot(l[:,0],l[:,1])*f
inl=r<1.0; _,_,vt=np.linalg.svd(C[inl]); t=vt[-1]
# orient t: motion direction should take points away (z increasing)
# decide sign by consistency: X1 = X0 + lam t with lam>0 and depths positive
if t[2]<0: t=-t
print(f'pure-translation epipole: inliers {inl.sum()}/{len(inl)}  t={np.round(t,4)}  epipole px=({f*t[0]/t[2]+cx:.1f},{f*t[1]/t[2]+cy:.1f})  median resid {np.median(r[inl]):.3f}px')
# essential matrix (allow rotation)
E,mask=cv2.findEssentialMat(x0,x1,K,method=cv2.RANSAC,prob=0.999,threshold=0.8)
_,R,tt,mask2=cv2.recoverPose(E,x0,x1,K,mask=mask)
ang=np.degrees(np.arccos(np.clip((np.trace(R)-1)/2,-1,1)))
w,v=np.linalg.eig(R); ax=np.real(v[:,np.argmin(np.abs(w-1))])
print(f'essential: inliers {int(mask.sum())}, rot {ang:.2f} deg axis {np.round(ax,3)}, t {np.round(tt.ravel(),4)}')
np.save(f't_{a}_{b}.npy',t)
# displacement from pure translation model
T=json.load(open('bintrack.json'))
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return d/np.linalg.norm(d)
P0=2.73*ray(T[10]['cx'],T[10]['cy'])
for tag,tv in [('pure',t),('essential',tt.ravel()*np.sign(tt.ravel()[2]))]:
    if a!=10: break
    r1=ray(T[b]['cx'],T[b]['cy'])
    # solve P0 + lam*tv = s*r1 (least squares)
    A=np.c_[tv,-r1]; sol,res,_,_=np.linalg.lstsq(A,-P0,rcond=None)
    lam,s=sol
    P1=s*r1
    print(f'  {tag}: lam {lam:.3f}  range@{b} {s:.3f}  disp {np.linalg.norm(P1-P0):.3f}  miss {np.linalg.norm(P0+lam*tv-P1)*100:.1f}cm')
    for nm,n in [('depthfit r1.4',np.array([0.0195,-0.7941,-0.6074])),('roll8',np.array([0.1111,-0.7909,-0.6018])),('vertVP',np.load('normals.npy')[1]),('horizon',np.load('normals.npy')[0])]:
        print(f'      t vs floor ({nm}) elevation {np.degrees(np.arcsin(tv@n/np.linalg.norm(tv))):.1f} deg')
