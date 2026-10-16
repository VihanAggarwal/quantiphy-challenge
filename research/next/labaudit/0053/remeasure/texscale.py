import cv2,numpy as np
f=711.;cx=640.;cy=360.
O=np.load('captured_0053.npy'); X=np.load('captured_0053x.npy'); T=np.load('bin_track_x.npy')
def mask(i):
    x=X[i].astype(int); b,g,r=x[...,0],x[...,1],x[...,2]
    m=(~((g>200)&(r<80)&(b<80))).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=np.argmin([np.hypot(*(cen[j]-T[i,1:3])) if j>0 else 1e9 for j in range(n)])
    return (lab==k).astype(np.uint8)
def rayn(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return d/np.linalg.norm(d)
def planeZ(i,pd,hc):
    p=np.radians(pd); U=np.array([0,-np.cos(p),-np.sin(p)])
    h=0.125-2.73*(U@rayn(T[10,1],T[10,2]))
    d=rayn(T[i,1],T[i,2]); return ((hc-h)/(U@d))*d
def ecc_scale(i,j):
    # warp crop of frame j onto frame i, similarity-ish via affine; return scale of j relative to i
    gi=cv2.cvtColor(O[i],cv2.COLOR_BGR2GRAY).astype(np.float32); gj=cv2.cvtColor(O[j],cv2.COLOR_BGR2GRAY).astype(np.float32)
    mi=mask(i); 
    # init: translate centroid, scale by bbox ratio
    s0=np.sqrt(T[j,7]/T[i,7])
    W=np.array([[s0,0,T[j,1]-s0*T[i,1]],[0,s0,T[j,2]-s0*T[i,2]]],np.float32)  # maps i coords -> j coords
    crit=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,500,1e-7)
    try:
        cc,W=cv2.findTransformECC(gi,gj,W,cv2.MOTION_AFFINE,crit,cv2.erode(mi,np.ones((5,5),np.uint8)),5)
    except cv2.error as e:
        return None
    A=W[:,:2]; sv=np.linalg.svd(A,compute_uv=False)
    return cc,np.sqrt(abs(np.linalg.det(A))),sv
pairs=[(10,22),(22,34),(34,47),(10,34),(10,47),(22,47)]
for i,j in pairs:
    r=ecc_scale(i,j)
    if r is None: print(i,j,'ECC failed'); continue
    cc,s,sv=r
    line='frames %d->%d: ECC cc %.3f texture scale (j/i) %.3f sv %s | size ratio Zj/Zi needed %.3f | plane Zi/Zj: '%(i,j,cc,s,np.round(sv,3),1/s)
    for pd in [35.6,42,48]:
        zi=planeZ(i,pd,0.11)[2]; zj=planeZ(j,pd,0.11)[2]
        line+=' p%.0f %.3f'%(pd,zj/zi)
    print(line)
