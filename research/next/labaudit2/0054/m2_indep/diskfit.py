from common import *
import numpy as np, cv2, json, sys
from lsq import least_squares
REND=sys.argv[1] if len(sys.argv)>1 else 'a'
fa=frames(REND)
M=json.load(open(OUT+'ax_moments.json'))
H=24; SS=3
yy,xx=np.mgrid[-H:H,-H:H].astype(float)
# supersampled grid
sy,sx=np.mgrid[0:2*H*SS,0:2*H*SS].astype(float)
sy=(sy+0.5)/SS-H-0.5; sx=(sx+0.5)/SS-H-0.5
def render_alpha(cx,cy,D,Lx,Ly,sig):
    # disk at (cx,cy) swept along (Lx,Ly) centred: average of K disks
    K=9; acc=np.zeros_like(sx)
    for k in range(K):
        s=(k/(K-1)-0.5) if K>1 else 0
        acc+=((sx-(cx+s*Lx))**2+(sy-(cy+s*Ly))**2<=(D/2)**2)
    acc/=K
    a=acc.reshape(2*H,SS,2*H,SS).mean((1,3))
    if sig>0.05:
        a=cv2.GaussianBlur(a,(0,0),sig)
    return a
def fit_one(i,obj):
    r=[m for m in M if m['i']==i and m['obj']==obj][0]
    X,Y=int(round(r['x'])),int(round(r['y']))
    I=fa[i][Y-H:Y+H,X-H:X+H].astype(float)
    idx=[k for k in range(len(fa)) if abs(k-i)>4]
    B=np.median(np.array([fa[k][Y-H:Y+H,X-H:X+H] for k in idx]),axis=0).astype(float)
    # init blur from moments
    L=r['L']; ang=np.radians(r['ang'])
    p0=np.r_[r['x']-X, r['y']-Y, r['Dmin'], L*np.cos(ang), L*np.sin(ang), 0.8]
    def model(p):
        a=render_alpha(*p[:6])
        # foreground colour: linear in (x,y) per channel, solved by linear LSQ given alpha
        A=a[...,None]
        # I - B = a*(F - B) ; F = c0 + cx*x + cy*y
        R=(I-B)
        cols=[]
        Xd=np.stack([a, a*xx/H, a*yy/H],-1).reshape(-1,3)
        Fp=[]
        pred=np.empty_like(I)
        for ch in range(3):
            tgt=(R[...,ch]+a*B[...,ch]).ravel()
            coef=np.linalg.lstsq(Xd,tgt,rcond=None)[0]
            F=coef[0]+coef[1]*xx/H+coef[2]*yy/H
            pred[...,ch]=a*F+(1-a)*B[...,ch]
        return pred
    def res(p):
        p=p.copy(); p[5]=abs(p[5])
        return (model(p)-I).ravel()
    s=least_squares(res,p0,iters=60,eps=1e-3)
    p=s.x; p[5]=abs(p[5])
    rms=np.sqrt((s.fun**2).mean())
    return p,rms,X,Y
out=[]
for obj,rng in (('white',range(24,36)),('green',range(25,36))):
    for i in rng:
        try:
            p,rms,X,Y=fit_one(i,obj)
        except Exception as e:
            print(i,obj,'fail',e); continue
        print('%s v%d: c=(%.1f,%.1f) D=%.2f blur=(%.1f,%.1f) |L|=%.1f psf=%.2f rms=%.1f'%(obj,i,p[0]+X,p[1]+Y,p[2],p[3],p[4],np.hypot(p[3],p[4]),p[5],rms))
        out.append(dict(i=i,obj=obj,x=p[0]+X,y=p[1]+Y,D=p[2],Lx=p[3],Ly=p[4],psf=p[5],rms=rms))
json.dump(out,open(OUT+'diskfit_%s.json'%REND,'w'))
