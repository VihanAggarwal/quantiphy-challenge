import cv2, numpy as np, sys

class _Sol: pass
def least_squares(fun,p0,x_scale=None):
    p=np.array(p0,float); lam=1e-3
    r=fun(p); cost=(r**2).sum()
    for it in range(300):
        J=np.empty((len(r),len(p)))
        for k in range(len(p)):
            dp=np.zeros_like(p); dp[k]=1e-6*max(1,abs(p[k]))
            J[:,k]=(fun(p+dp)-r)/dp[k]
        A=J.T@J; g=J.T@r
        while True:
            step=np.linalg.solve(A+lam*np.diag(np.diag(A)),-g)
            pn=p+step; rn=fun(pn); cn=(rn**2).sum()
            if np.isfinite(cn) and cn<cost:
                p,r,cost=pn,rn,cn; lam=max(lam/3,1e-9); break
            lam*=5
            if lam>1e9: break
        if lam>1e9 or np.abs(step).max()<1e-10: break
    o=_Sol(); o.x=p; o.fun=r; return o

fr=int(sys.argv[1]) if len(sys.argv)>1 else 0
ffix=float(sys.argv[2]) if len(sys.argv)>2 else 0
c=cv2.VideoCapture('data/QuantiPhy/internet_0054.mp4')
c.set(cv2.CAP_PROP_POS_FRAMES,fr); ok,f=c.read()
X0,Y0=1100,1250
cr=f[Y0:1600,X0:2600].astype(int)
hsv=cv2.cvtColor(f[Y0:1600,X0:2600],cv2.COLOR_BGR2HSV)
m=((cr.min(2)>165)&(hsv[...,1]<60)).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
m[:,650:820]=0
n,lab,st,cen=cv2.connectedComponentsWithStats(m)
idx=[j for j in range(1,n) if st[j,4]>500]
outer=[j for j in idx if st[j,3]>150]; inner=[j for j in idx if 40<st[j,3]<=150]
def edges_for(mm):
    to=[];ti=[];bi=[];bo=[]
    for x in range(mm.shape[1]):
        ys=np.nonzero(mm[:,x])[0]
        if len(ys)==0: continue
        br=np.nonzero(np.diff(ys)>1)[0]
        s=np.r_[ys[0],ys[br+1]]; e=np.r_[ys[br],ys[-1]]
        if len(s)!=2: continue
        to.append((x,s[0]-0.5)); ti.append((x,e[0]+0.5)); bi.append((x,s[1]-0.5)); bo.append((x,e[1]+0.5))
    return [np.array(a,float)+[X0,Y0] for a in (to,ti,bi,bo)]
sets=[]
R_out=6*0.3048; R_in=2*0.3048; w=2*0.0254
for comps,R in ((outer,R_out),(inner,R_in)):
    to,ti,bi,bo=edges_for(np.isin(lab,comps).astype(np.uint8))
    sets.append((np.r_[to,bo],R)); sets.append((np.r_[ti,bi],R-w))
cx,cy=1920.,1080.
def rays(P,fl,th,ph):
    x=(P[:,0]-cx)/fl; y=(P[:,1]-cy)/fl
    d=np.stack([x,y,np.ones_like(x)],1)
    # camera to world: roll about z, then pitch about x (camera looks down by th)
    cr_,sr=np.cos(ph),np.sin(ph); Rz=np.array([[cr_,-sr,0],[sr,cr_,0],[0,0,1]])
    ct,stt=np.cos(th),np.sin(th); Rx=np.array([[1,0,0],[0,ct,-stt],[0,stt,ct]])
    # camera y down. world: X right, Y down, Z forward(level). pitch down th: rotate
    Rw=np.array([[1,0,0],[0,ct,stt],[0,-stt,ct]])@Rz
    return d@Rw.T
def resid(p):
    if ffix: fl=ffix; th,ph,h,Xc,Zc=p
    else: fl,th,ph,h,Xc,Zc=p
    out=[]
    for P,R in sets:
        d=rays(P,fl,th,ph)
        t=h/d[:,1]   # ground at Y=+h (camera y down)
        X=t*d[:,0]; Z=t*d[:,2]
        r=np.hypot(X-Xc,Z-Zc)
        out.append((r-R)*fl/Z)
    return np.concatenate(out)
if ffix: p0=[0.08,0.0,1.5,0,9]
else: p0=[2800,0.08,0.0,1.5,0,9]
sol=least_squares(resid,p0,x_scale='jac')
p=sol.x
if ffix: fl=ffix; th,ph,h,Xc,Zc=p
else: fl,th,ph,h,Xc,Zc=p
rms=np.sqrt((sol.fun**2).mean())
import itertools
k0=0
for (P,R) in sets:
    n=len(P); rr=sol.fun[k0:k0+n]; k0+=n; print('  set R=%.3f n=%d mean resid %.2f rms %.2f'%(R,n,rr.mean(),rr.std()))
yh=lambda x: cy - fl*np.tan(th) + (x-cx)*np.tan(ph)  # approx for small roll
print('f=%.0f pitch=%.2fdeg roll=%.3fdeg h=%.3f Xc=%.2f Zc=%.2f rms=%.2fpx  horizon y@1000=%.1f @1920=%.1f @2900=%.1f'%(fl,np.degrees(th),np.degrees(ph),h,Xc,Zc,rms,yh(1000),yh(1920),yh(2900)))
np.save if False else None
# metric: px per metre for horizontal ground segment at image row y (x~2300): f*cos(th)/h*(y-yh)
for y in (1085,1092,1126,1152):
    print('row',y,'px/m(horiz, ground)= %.1f'%(np.cos(th)/h*(y-yh(2300))), ' m/px=%.5f'%(h/(np.cos(th)*(y-yh(2300)))), ' depth Z=%.2f'%(fl*h/np.cos(th)/(y-yh(2300))))
