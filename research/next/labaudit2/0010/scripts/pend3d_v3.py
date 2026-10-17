"""Variants of the first-period pendulum fit: anchor weight, size weight, fit window, pivot pixel.
Reports the label-relevant quantities at c15 (t=0.6) and c8/c7 (t=0.3)."""
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0010/scripts')
import pend3d_v2 as P
from common import *
from lm import least_squares
def run(K1, mode, sa=0.02, sw=1.2, piv=(640.3,234.1), anch=None):
    P.PIV=piv
    kk=np.arange(K1+1); P.n=np.array([cap(i) for i in kk]); P.u=P.u_all[kk]; P.v=P.v_all[kk]; P.w=P.w_all[kk]
    P.NMAX=int(P.n.max())+3
    if anch is not None: P.ANCH=anch
    f=lambda q: P.resid(q,mode,sw=sw,sa=sa)
    best=None
    for th0 in (0.7,0.85):
        for ph0 in (np.pi/2,-np.pi/2,0,np.pi):
            r=least_squares(f,np.array([1.52,0.35,0.0,0.3,th0,ph0,0,0,0.0,9.8,0.07]),iters=80)
            if best is None or r.cost<best.cost: best=r
    r=least_squares(f,best.x,iters=300)
    p=r.x; q0,L,gh,th,ph,w1,w2,gam,gm,D=P.unpack(p)
    C,V=P.integrate(p,nmax=52); Cc=C[::P.SUB]; Vc=V[::P.SUB]; Rc=np.linalg.norm(Cc,axis=1)
    Ck=C[P.n*P.SUB]; uu,vv,R=P.proj(Ck)
    ru=np.sqrt(np.mean((uu-P.u)**2)); rv=np.sqrt(np.mean((vv-P.v)**2)); rw=np.sqrt(np.mean((F*D/R-P.w)**2))
    an=' '.join(f"c{c}:{(Rc[c]-0.035-s)*100:+.1f}" for c,s in P.ANCH)
    sp=np.linalg.norm(V,axis=1); tt=np.arange(len(sp))/(25*P.SUB)
    mins=[tt[i]*25 for i in range(1,len(sp)-1) if sp[i]<sp[i-1] and sp[i]<sp[i+1]]
    res={}
    for c0 in (7,8,15):
        res[c0]=dict(fd=25*np.linalg.norm(Cc[c0+1]-Cc[c0]),inst=float(np.linalg.norm(Vc[c0])),afd=625*np.linalg.norm(Cc[c0+2]-2*Cc[c0+1]+Cc[c0]),
                     dR1=(Rc[c0+1]-Rc[c0])*100,dR2=(Rc[c0+2]-Rc[c0+1])*100)
    print(f"K1={K1} {mode:18s} sa={sa} sw={sw} piv={piv}: rms u{ru:.2f} v{rv:.2f} w{rw:.2f} L{L:.3f} g{gm:.2f} D{D*100:.2f} turn {np.round(mins[:2],2)} | {an}")
    print("     "+'  '.join(f"c{c0}: fd {d['fd']:.3f} inst {d['inst']:.3f} aFD {d['afd']:.2f} dR {d['dR1']:+.2f}/{d['dR2']:+.2f}" for c0,d in res.items()))
    return dict(p=p.tolist(),C=Cc.tolist(),R=Rc.tolist(),res=res)
if __name__=='__main__':
    B=P.B
    k=np.arange(49); P.u_all=np.array([P.T['s'][i]['u'] for i in k]); P.v_all=np.array([P.T['s'][i]['v'] for i in k]); P.w_all=np.array([P.S[i]['wh'] for i in k])
    out={}
    out['a07']=run(31,'gfix+anch',sa=0.007)
    out['a07nos']=run(31,'gfix+anch+nosize',sa=0.007)
    out['a07gfree']=run(31,'anch',sa=0.007)
    out['K24']=run(24,'gfix+anch')
    out['K36']=run(36,'gfix+anch')
    out['piv230']=run(31,'gfix+anch',piv=(639.5,230.7))
    out['piv226']=run(31,'gfix+anch',piv=(639.5,226.0))
    out['a07_c7']=run(31,'gfix+anch',sa=0.007,anch=[(7,1.706),(15,1.344),(23,1.4605),(30,1.784)])
    out['a07_c22']=run(31,'gfix+anch',sa=0.007,anch=[(8,1.706),(15,1.344),(22,1.4605),(30,1.784)])
    json.dump(out,open(B+'pend3d_v3.json','w'))
