# Perpendicular-to-motion extent of the ball matte (x render) and sphere-model range.
import cv2, numpy as np, sys
FR='/home/user/quantiphy-challenge/research/next/labaudit/0016/frames/f%s_%02d.png'
f=711.; cx0,cy0=640.,360.
rend=sys.argv[1] if len(sys.argv)>1 else 'x'
def cap(k): return k+(k>=12)+(k>=36)
def ballmask(im,prev):
    b,g,r=[im[...,i].astype(int) for i in range(3)]
    if rend=='x':
        m=~((g>150)&(g>r+60)&(g>b+60))
    else:
        raise SystemExit
    m=m.astype(np.uint8); m[680:,1000:]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    best=None
    for k in range(1,n):
        if st[k,4]<2000 or st[k,4]>20000: continue
        d=np.hypot(*(cen[k]-prev))
        if best is None or d<best[0]: best=(d,k)
    return lab==best[1]
prev=np.array([587.,256.])
C={}
masks={}
for i in range(32,41):
    im=cv2.imread(FR%(rend,i)); m=ballmask(im,prev)
    ys,xs=np.nonzero(m); c=np.array([xs.mean(),ys.mean()]); C[i]=c; prev=c; masks[i]=(xs,ys)
def sphere_axes(d,R,u):
    # u: image point of centre (approx direction); return semi-axes (a radial, b tangential) px
    x,y=u[0]-cx0,u[1]-cy0; rr=np.hypot(x,y); th=np.arctan(rr/f)
    s=R/d; ca=np.sqrt(1-s*s)
    den=np.cos(th)**2-s*s
    a=f*s*ca/den; b=f*s/np.sqrt(den)
    ur=np.array([x,y])/rr if rr>0 else np.array([1.,0.])
    return a,b,ur
print('k cap  cx     cy     ext4sd  extpct  motion_ang')
for i in range(32,41):
    xs,ys=masks[i]
    j0,j1=(i-1,i+1)
    if j0 not in C: j0=i
    if j1 not in C: j1=i
    mv=C[j1]-C[j0]; mv/=np.linalg.norm(mv); nv=np.array([-mv[1],mv[0]])
    p=(xs-C[i][0])*nv[0]+(ys-C[i][1])*nv[1]
    q=(xs-C[i][0])*mv[0]+(ys-C[i][1])*mv[1]
    e4=4*p.std(); ep=np.percentile(p,99.5)-np.percentile(p,0.5)
    l4=4*q.std()
    # solve centre range d for D: extent along n = 2 sqrt(a^2 (n.ur)^2 + b^2 (n.ut)^2)
    def ext(d,R=0.09):
        a,b,ur=sphere_axes(d,R,C[i]); ut=np.array([-ur[1],ur[0]])
        return 2*np.sqrt(a*a*(nv@ur)**2+b*b*(nv@ut)**2)
    # d such that ext(d)=e4, for R=0.09
    lo,hi=0.3,5
    for _ in range(60):
        mid=(lo+hi)/2
        if ext(mid)>e4: lo=mid
        else: hi=mid
    print(i,cap(i),'%.1f %.1f  %.1f %.1f  along=%.1f  ang=%.0f  d(R=.09)=%.3f surf=%.3f'%(C[i][0],C[i][1],e4,ep,l4,np.degrees(np.arctan2(mv[1],mv[0])),mid,mid-0.09))
