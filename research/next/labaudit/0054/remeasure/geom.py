import cv2,numpy as np
D='/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure/frames'
F=711.0; CX=640.0; CY=360.0
def ray(u,v,f=F):
    d=np.stack([np.asarray(u,float)-CX,np.asarray(v,float)-CY,np.full(np.shape(u),f)],-1)
    return d/np.linalg.norm(d,axis=-1,keepdims=True)
def fgmask(v,i):
    f=cv2.imread(f'{D}/{v}_{i:02d}.png')
    if v.endswith('x') and v.startswith('b'):
        m=(f.astype(int).sum(2)>40)
    else:
        b,g,r=[f[:,:,k].astype(int) for k in range(3)]
        m=~((g>200)&(b<60)&(r<60))
    m[690:,1000:]=False
    m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    return f,m
def comps(v,i,minA=40):
    f,m=fgmask(v,i)
    n,l,st,c=cv2.connectedComponentsWithStats(m)
    out=[]
    for k in range(1,n):
        if st[k,4]>minA:
            ys,xs=np.where(l==k); col=f[ys,xs].mean(0)
            out.append(dict(c=c[k],A=st[k,4],bbox=st[k,:4],bgr=col,mask=(l==k)))
    return out
def pick(v,i,near,maxd=60):
    cs=comps(v,i); best=None
    for c in cs:
        d=np.hypot(*(c['c']-np.array(near)))
        if d<maxd and (best is None or d<best[0]): best=(d,c)
    return None if best is None else best[1]
def cone_fit(mask,f=F,exclude_border=True):
    cnts,_=cv2.findContours(mask.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    cnt=max(cnts,key=len)[:,0,:].astype(float)
    if exclude_border:
        H,W=mask.shape
        ok=(cnt[:,0]>1)&(cnt[:,0]<W-2)&(cnt[:,1]>1)&(cnt[:,1]<H-2)
        cnt=cnt[ok]
    # boundary pixel edge at +0.5? contour pixels are inside; shift outward ~0.5px by using centroid direction
    cen=cnt.mean(0); dirv=cnt-cen; dirv/=np.linalg.norm(dirv,axis=1,keepdims=True)+1e-9
    cnt=cnt+0.5*dirv
    R=ray(cnt[:,0],cnt[:,1],f)
    # fit plane n.x = d (cone: R.c = cos th) : least squares n, d with |n|=1
    A=np.hstack([R,-np.ones((len(R),1))])
    _,_,vt=np.linalg.svd(A); s=vt[-1]; n=s[:3]; d=s[3]
    sc=np.linalg.norm(n); n/=sc; d/=sc
    if d<0: n,d=-n,-d
    th=np.arccos(np.clip(d,-1,1))
    res=R@n-d
    return n,th,np.degrees(np.std(res)) ,len(cnt)
def centre3d(n,th,Rm):
    r=Rm/np.sin(th)
    return n*r, r
