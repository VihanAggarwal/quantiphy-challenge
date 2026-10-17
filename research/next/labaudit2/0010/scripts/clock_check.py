"""Clock check: first-period pendulum fit (g=9.8, anchors sigma 2 cm) with the first dropped capture frame placed
before video 10..14, or no drop (pure 24 fps / 25 fps). rms of u,v tells which clock the image track follows."""
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0010/scripts')
import pend3d_v2 as P
from common import *
from lm import least_squares
k=np.arange(32); u_all=np.array([P.T['s'][i]['u'] for i in range(49)]); v_all=np.array([P.T['s'][i]['v'] for i in range(49)]); w_all=np.array([P.S[i]['wh'] for i in range(49)])
for name,nmap in [('drop@12',[i+(i>=12) for i in k]),('drop@11',[i+(i>=11) for i in k]),('drop@13',[i+(i>=13) for i in k]),('drop@14',[i+(i>=14) for i in k]),('none25',list(k)),('none24',None)]:
    if nmap is None:   # 24 fps: emulate by scaling time: use capture index = k*25/24 on a finer grid
        P.SUB=24; nn=np.array(k)*25/24.0; P.n=np.round(nn*P.SUB).astype(int)//1; P.n=np.array(k)  # placeholder
        P.SUB=4
        # integrate on 25 fps grid but sample at k/24 -> index k*25/24*SUB
        idx=np.round(np.array(k)*25/24*P.SUB).astype(int)
    else:
        P.SUB=4; idx=np.array(nmap)*P.SUB
    P.u=u_all[k]; P.v=v_all[k]; P.w=w_all[k]; P.NMAX=int(idx.max()/P.SUB)+3
    def resid(p):
        q0,L,gh,th,ph,w1,w2,gam,gm,D=P.unpack(p)
        C,V=P.integrate(p); Ck=C[idx]; uu,vv,R=P.proj(Ck)
        return np.concatenate([(uu-P.u)/0.7,(vv-P.v)/0.7,(F*D/R-P.w)/1.2,[(gm-9.8)/1e-3]])
    best=None
    for th0 in (0.7,0.85):
        for ph0 in (np.pi/2,-np.pi/2,0,np.pi):
            r=least_squares(resid,np.array([1.52,0.35,0.0,0.3,th0,ph0,0,0,0.0,9.8,0.07]),iters=80)
            if best is None or r.cost<best.cost: best=r
    r=least_squares(resid,best.x,iters=300); q0,L,gh,th,ph,w1,w2,gam,gm,D=P.unpack(r.x)
    C,V=P.integrate(r.x); uu,vv,R=P.proj(C[idx])
    print(f"{name:8s}: rms u {np.sqrt(np.mean((uu-P.u)**2)):.2f} v {np.sqrt(np.mean((vv-P.v)**2)):.2f} w {np.sqrt(np.mean((F*D/R-P.w)**2)):.2f}  L {L:.3f} D {D*100:.2f}")
