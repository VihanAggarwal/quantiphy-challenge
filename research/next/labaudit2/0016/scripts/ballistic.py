# Image-only ballistic fit on the 25 fps capture clock, |g|=9.8, gravity direction free or fixed;
# optional depth anchor (surface range 1.402 at c37 or c38). Reports v and label-style FD.
import numpy as np
import sys; sys.path.insert(0,"/home/user/quantiphy-challenge/research/next/labaudit2/0016/scripts"); from lm import least_squares
f=711.; cx0,cy0=640.,360.
cent={33:(640.8,198.8),34:(688.7,156.0),35:(735.2,121.1),36:(812.2,77.2),37:(844.7,70.3),38:(872.3,70.5),39:(894.5,77.3),40:(913.1,90.6)}
def cap(k): return k+(k>=12)+(k>=36)
R=0.09
def model(p,t):
    P0=p[0:3]; V0=p[3:6]; th,ph=p[6],p[7]
    g=9.8*np.array([np.cos(th)*np.sin(ph),np.cos(th)*np.cos(ph),np.sin(th)])
    return P0[None]+V0[None]*t[:,None]+0.5*g[None]*t[:,None]**2, g
def proj(X): return np.c_[cx0+f*X[:,0]/X[:,2], cy0+f*X[:,1]/X[:,2]]
def run(frames,anchor=None,gfix=None,w_anchor=200.):
    t=np.array([cap(k) for k in frames])/25.-1.5
    obs=np.array([cent[k] for k in frames])
    def res(p):
        pp=p.copy()
        if gfix is not None: pp=np.r_[p[:6],gfix]
        X,g=model(pp,t); r=(proj(X)-obs).ravel()
        if anchor is not None:
            n,val=anchor; Xa,_=model(pp,np.array([n/25.-1.5])); r=np.r_[r,w_anchor*(np.linalg.norm(Xa)-R-val)]
        return r
    best=None
    for th0 in np.radians([20,35,50]):
      for ph0 in np.radians([-20,0,20]):
        for z in [1.2,1.6,2.0]:
          p0=np.r_[0.2,-0.4,z,1,-0.5,1,th0,ph0]
          if gfix is not None: p0=p0[:6]
          s=least_squares(res,p0)
          if best is None or s.cost<best.cost: best=s
    p=best.x if gfix is None else np.r_[best.x,gfix]
    return p,best
def report(p,tag,rms):
    tt=lambda n: np.array([n/25.-1.5])
    X=lambda n: model(p,tt(n))[0][0]
    V=p[3:6]+model(p,np.array([0.]))[1]*0  # dummy
    g=model(p,np.array([0.]))[1]
    vel=lambda n: p[3:6]+g*(n/25.-1.5)
    Q=lambda P: P/np.linalg.norm(P)*(np.linalg.norm(P)-R)
    th,ph=p[6],p[7]
    print('%-28s rms %.2f px | pitch %.1f roll %.1f | surf c37 %.3f c38 %.3f c39 %.3f | |v| c37.5 %.2f c38 %.2f | FD c37->38 %.2f c38->39 %.2f (label-style %.2f / %.2f)'%(
        tag,rms,np.degrees(th),np.degrees(ph),np.linalg.norm(X(37))-R,np.linalg.norm(X(38))-R,np.linalg.norm(X(39))-R,
        np.linalg.norm(vel(37.5)),np.linalg.norm(vel(38)),25*np.linalg.norm(X(38)-X(37)),25*np.linalg.norm(X(39)-X(38)),
        25*np.linalg.norm(Q(X(38))-Q(X(37))),25*np.linalg.norm(Q(X(39))-Q(X(38)))))
for frames in [list(range(36,41)),list(range(34,41)),list(range(33,41))]:
    for anc in [None,(37,1.402),(38,1.402)]:
        p,s=run(frames,anc)
        rms=np.sqrt(np.mean(s.fun[:2*len(frames)]**2))
        report(p,'%d-%d anchor=%s'%(frames[0],frames[-1],anc),rms)
# gravity fixed to size-route direction (-0.28,0.80,0.54)
gd=np.array([-2.58,7.29,4.91]); gd/=np.linalg.norm(gd)
th=np.arcsin(gd[2]); ph=np.arctan2(gd[0],gd[1])
print('size-route gravity: pitch %.1f roll %.1f'%(np.degrees(th),np.degrees(ph)))
for frames in [list(range(36,41)),list(range(33,41))]:
    for anc in [None,(37,1.402),(38,1.402)]:
        p,s=run(frames,anc,gfix=np.r_[th,ph]); rms=np.sqrt(np.mean(s.fun[:2*len(frames)]**2))
        report(p,'gfix %d-%d anchor=%s'%(frames[0],frames[-1],anc),rms)
