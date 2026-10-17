# 3D centres from matte centroid + perpendicular-extent size route; quadratic fit on 25 fps capture clock.
import cv2, numpy as np, sys
FR='/home/user/quantiphy-challenge/research/next/labaudit/0016/frames/fx_%02d.png'
f=711.; cx0,cy0=640.,360.
def cap(k): return k+(k>=12)+(k>=36)
def comps(i,prev):
    im=cv2.imread(FR%i); b,g,r=[im[...,j].astype(int) for j in range(3)]
    m=(~((g>150)&(g>r+60)&(g>b+60))).astype(np.uint8); m[680:,1000:]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    best=min([k for k in range(1,n) if 2000<st[k,4]<20000],key=lambda k:np.hypot(*(cen[k]-prev)))
    ys,xs=np.nonzero(lab==best); return xs.astype(float),ys.astype(float)
def axes(d,R,c):
    x,y=c[0]-cx0,c[1]-cy0; rr=np.hypot(x,y); th=np.arctan(rr/f); s=R/d
    den=np.cos(th)**2-s*s; a=f*s*np.sqrt(1-s*s)/den; b=f*s/np.sqrt(den)
    ur=np.array([x,y])/rr; return a,b,ur,th
frames=list(range(33,41)); prev=np.array([641.,199.]); C={};P={}
for i in frames:
    xs,ys=comps(i,prev); c=np.array([xs.mean(),ys.mean()]); C[i]=c; P[i]=(xs,ys); prev=c
R=0.09
rows=[]
for i in frames:
    j0=i-1 if i-1 in C else i; j1=i+1 if i+1 in C else i
    mv=C[j1]-C[j0]; mv/=np.linalg.norm(mv); nv=np.array([-mv[1],mv[0]])
    xs,ys=P[i]; p=(xs-C[i][0])*nv[0]+(ys-C[i][1])*nv[1]; e4=4*p.std()
    lo,hi=0.3,6
    for _ in range(60):
        mid=(lo+hi)/2; a,b,ur,th=axes(mid,R,C[i]); ut=np.array([-ur[1],ur[0]])
        if 2*np.sqrt(a*a*(nv@ur)**2+b*b*(nv@ut)**2)>e4: lo=mid
        else: hi=mid
    # silhouette-centre offset: ellipse centre lies outward of projected sphere centre
    a,b,ur,th=axes(mid,R,C[i]); al=np.arcsin(R/mid)
    rc=f*(np.tan(th+al)+np.tan(th-al))/2; r0=np.hypot(C[i][0]-cx0,C[i][1]-cy0)
    # projected centre is at radius f*tan(th0) where ellipse centre radius = rc(th0) ~ r0
    th0=th
    for _ in range(20):
        rc=f*(np.tan(th0+al)+np.tan(th0-al))/2; th0+= (r0-rc)/f*np.cos(th0)**2
    cc=np.array([cx0,cy0])+ur*f*np.tan(th0)
    ray=np.array([cc[0]-cx0,cc[1]-cy0,f]); ray/=np.linalg.norm(ray)
    rows.append((i,cap(i),C[i],cc,e4,mid,ray))
print('video cap  centroid  ext  d_centre(D=18cm)')
for i,n,c,cc,e4,d,ray in rows: print(i,n,np.round(c,1),round(e4,1),round(d,3))
# quadratic fit in 3D with scale k on ranges
T=np.array([r[1] for r in rows])/25.
X0=np.array([r[5]*r[6] for r in rows])
use=np.array([r[0]>=36 for r in rows])
for lab_,sel in [('36-40',use),('33-40',np.ones(len(rows),bool))]:
    A=np.vstack([np.ones(sel.sum()),T[sel],T[sel]**2]).T
    coef,res,_,_=np.linalg.lstsq(A,X0[sel],rcond=None)
    acc=2*coef[2]; 
    print(lab_,'acc vec (D=.18 scale)',np.round(acc,2),'|a|=%.2f'%np.linalg.norm(acc),' rms res cm',np.round(100*np.sqrt(((A@coef-X0[sel])**2).mean(0)),2))
    k=9.8/np.linalg.norm(acc); print('  scale k for |g|=9.8: %.3f -> implied D=%.3f'%(k,0.18*k))

print('\n--- velocities (size route) ---')
sel=use
A=np.vstack([np.ones(sel.sum()),T[sel],T[sel]**2]).T
coef=np.linalg.lstsq(A,X0[sel],rcond=None)[0]
pos=lambda t: coef[0]+coef[1]*t+coef[2]*t*t
vel=lambda t: coef[1]+2*coef[2]*t
for k in [1.0,1.071]:
  for tc in [37,37.5,38,38.5]:
    t=tc/25; print('scale %.3f  cap %.1f |v|=%.2f  range_c=%.3f'%(k,tc,k*np.linalg.norm(vel(t)),k*np.linalg.norm(pos(t))))
  for n in [37,38]:
    P1=pos(n/25)*k; P2=pos((n+1)/25)*k
    print('   FD centre c%d->c%d: %.2f m/s ; surface-style %.2f'%(n,n+1,25*np.linalg.norm(P2-P1),
          25*np.linalg.norm(P2/np.linalg.norm(P2)*(np.linalg.norm(P2)-0.09*k)-P1/np.linalg.norm(P1)*(np.linalg.norm(P1)-0.09*k))))
# rescale to stated anchor 1.402 at c38 or c37
for n in [37,38]:
    r=np.linalg.norm(pos(n/25)); s=(1.402+0.09)/r  # centre range = surface+R  (R scaled approx)
    # solve s so that s*r - 0.09*s = 1.402  (D scales with s)
    s=1.402/(r-0.09)
    P1=pos(n/25)*s; P2=pos((n+1)/25)*s
    Q=lambda P:P/np.linalg.norm(P)*(np.linalg.norm(P)-0.09*s)
    print('anchor at c%d: scale %.3f (D=%.3f) |a|=%.2f  label FD c%d->%d = %.2f  phys v(c%d)=%.2f v(c37.5)=%.2f'%(n,s,0.18*s,s*np.linalg.norm(2*coef[2]),n,n+1,25*np.linalg.norm(Q(P2)-Q(P1)),n,s*np.linalg.norm(vel(n/25)),s*np.linalg.norm(vel(1.5))))
