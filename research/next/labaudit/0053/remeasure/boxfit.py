import cv2,numpy as np,sys
f=711.;cx=640.;cy=360.
X=np.load('captured_0053x.npy'); T=np.load('bin_track_x.npy')
FR=[int(a) for a in sys.argv[2].split(',')] if len(sys.argv)>2 else [10,22,34,47]
masks={}
for i in FR:
    x=X[i].astype(int); b,g,r=x[...,0],x[...,1],x[...,2]
    m=(~((g>200)&(r<80)&(b<80))).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=np.argmin([np.hypot(*(cen[j]-T[i,1:3])) if j>0 else 1e9 for j in range(n)])
    masks[i]=(lab==k).astype(np.uint8)
def cam(p,h):
    fc=np.array([0,np.cos(p),-np.sin(p)]); dc=np.array([0,-np.sin(p),-np.cos(p)]); rc=np.array([1.,0,0])
    return fc,dc,rc,np.array([0,0,h])
def proj(Pw,p,h):
    fc,dc,rc,C=cam(p,h); v=Pw-C
    return np.stack([f*(v@rc)/(v@fc)+cx, f*(v@dc)/(v@fc)+cy],-1)
def ground_from_pixel(u,v,p,h,z):
    fc,dc,rc,C=cam(p,h); d=fc+(u-cx)/f*rc+(v-cy)/f*dc
    t=(z-h)/d[2]; return C+t*d
def box_corners(cen,a,b,c,psi):
    xs=np.array([[sx*a/2,sy*b/2,sz*c] for sx in(-1,1) for sy in(-1,1) for sz in(0,1)])
    R=np.array([[np.cos(psi),-np.sin(psi),0],[np.sin(psi),np.cos(psi),0],[0,0,1]])
    return cen+xs@R.T
def iou(i,cen,a,b,c,psi,p,h):
    P=box_corners(cen,a,b,c,psi); q=proj(P,p,h)
    hull=cv2.convexHull(q.astype(np.float32)).astype(np.int32)
    m=np.zeros((720,1280),np.uint8); cv2.fillConvexPoly(m,hull,1)
    M=masks[i]; return (m&M).sum()/max((m|M).sum(),1)
def fit(p,seed=0,iters=3000):
    rng=np.random.default_rng(seed)
    # h anchored: bin@0.4 click range 2.73 at height ~0.125 on centroid ray
    fc,dc,rc,_=cam(p,0); d=fc+(T[10,1]-cx)/f*rc+(T[10,2]-cy)/f*dc; d/=np.linalg.norm(d)
    h=0.125-2.73*d[2]
    best=None
    par=np.array([0.40,0.28,0.28,0.5])  # a,b,c,psi
    offs={i:np.zeros(2) for i in FR}
    def score(par,offs):
        a,b,c,psi=par
        s=0
        for i in FR:
            g=ground_from_pixel(T[i,1],T[i,2],p,h,c/2); cen=np.array([g[0]+offs[i][0],g[1]+offs[i][1],0])
            s+=iou(i,cen,a,b,c,psi,p,h)
        return s/len(FR)
    cur=score(par,offs); step=np.array([0.04,0.04,0.04,0.2]); ostep=0.05
    for it in range(iters):
        if rng.random()<0.5:
            k=rng.integers(4); trial=par.copy(); trial[k]+=rng.normal()*step[k]
            if trial[:3].min()<0.05: continue
            s=score(trial,offs)
            if s>cur: par,cur=trial,s
        else:
            i=FR[rng.integers(len(FR))]; o2={k:v.copy() for k,v in offs.items()}; o2[i]+=rng.normal(size=2)*ostep
            s=score(par,o2)
            if s>cur: offs,cur=o2,s
        if it%800==799: step*=0.6; ostep*=0.6
    # displacement of centres 10->34 if both present
    a,b,c,psi=par
    cens={i:ground_from_pixel(T[i,1],T[i,2],p,h,c/2)+np.array([offs[i][0],offs[i][1],0]) for i in FR}
    per={i:round(iou(i,np.array([cens[i][0],cens[i][1],0]),a,b,c,psi,p,h),3) for i in FR}
    return cur,par,h,cens,per
pd=float(sys.argv[1])
res=[fit(np.radians(pd),seed=s) for s in range(3)]
cur,par,h,cens,per=max(res,key=lambda r:r[0])
disp=np.linalg.norm(cens[34][:2]-cens[10][:2]) if 34 in cens and 10 in cens else float('nan')
print('pitch %.1f h %.3f meanIoU %.4f dims a %.3f b %.3f c %.3f psi %.2f perframe %s disp10-34 %.3f'%(pd,h,cur,*par,per,disp))
