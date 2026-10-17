"""Spherical pendulum fit, first period only (video 0-31 = capture 0-32; hand steady: string lines meet at
(640.3,234.1) with 0.42 px rms).  Pivot projection held to that point (sigma 0.5 px).
Variants: scale from g=9.8 only / from stated anchors (g fixed or free) / from D=7 cm sizes."""
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0010/scripts')
from common import *
from lm import least_squares
B='/home/user/quantiphy-challenge/research/next/labaudit2/0010/'
T=json.load(open(B+'track.json')); S=json.load(open(B+'size_s.json'))
K1=int(sys.argv[1]) if len(sys.argv)>1 else 31
kk=np.arange(K1+1); n=np.array([cap(i) for i in kk])
u=np.array([T['s'][i]['u'] for i in kk]); v=np.array([T['s'][i]['v'] for i in kk]); w=np.array([S[i]['wh'] for i in kk])
PIV=(640.3,234.1)
ANCH=[(8,1.706),(15,1.344),(23,1.4605),(30,1.784),(38,1.717),(45,1.350)]   # capture frame, stated surface range (half-up rounding)
SUB=4; NMAX=int(n.max())+3
def unpack(p):
    d0,L,a,b,th,ph,w1,w2,gam,gm,D=p
    gh=np.array([a,1.0,b]); gh/=np.linalg.norm(gh)
    q0=d0*ray(*PIV)+0*gh
    return q0,L,gh,th,ph,w1,w2,gam,gm,D
def basis(gh):
    e1=np.cross(gh,[0,0,1.0]); e1/=np.linalg.norm(e1); e2=np.cross(gh,e1); return e1,e2
def integrate(p, nmax=None):
    q0,L,gh,th,ph,w1,w2,gam,gm,D=unpack(p)
    g=gm*gh; e1,e2=basis(gh)
    x=L*(np.cos(th)*gh+np.sin(th)*(np.cos(ph)*e1+np.sin(ph)*e2))
    t1=np.cross(x,gh); t1/=np.linalg.norm(t1); t2=np.cross(x,t1); t2/=np.linalg.norm(t2)
    vv=w1*t1+w2*t2
    def f(x,vv):
        lam=(x@g+vv@vv)/(x@x); return vv, g-lam*x-gam*vv
    h=1/(25*SUB); N=(nmax or NMAX)*SUB+1
    X=np.zeros((N,3)); Vv=np.zeros((N,3)); X[0]=x; Vv[0]=vv
    for j in range(1,N):
        k1x,k1v=f(x,vv); k2x,k2v=f(x+h/2*k1x,vv+h/2*k1v); k3x,k3v=f(x+h/2*k2x,vv+h/2*k2v); k4x,k4v=f(x+h*k3x,vv+h*k3v)
        x=x+h/6*(k1x+2*k2x+2*k3x+k4x); vv=vv+h/6*(k1v+2*k2v+2*k3v+k4v)
        x=x/np.linalg.norm(x)*L; vv=vv-(vv@x)/(x@x)*x
        X[j]=x; Vv[j]=vv
    return q0[None,:]+X, Vv
def proj(C): return CX+F*C[:,0]/C[:,2], CY+F*C[:,1]/C[:,2], np.linalg.norm(C,axis=1)
def resid(p,mode,su=0.7,sw=1.2,sa=0.02):
    q0,L,gh,th,ph,w1,w2,gam,gm,D=unpack(p)
    C,V=integrate(p); Ck=C[n*SUB]; uu,vv,R=proj(Ck)
    r=[(uu-u)/su,(vv-v)/su]
    if 'nosize' not in mode: r.append((F*D/R-w)/sw)
    if 'anch' in mode:
        r.append(np.array([(np.linalg.norm(C[c*SUB])-0.035-s)/sa for c,s in ANCH if c<=n.max()]))
    pri=[]
    if 'gfix' in mode: pri.append((gm-9.8)/1e-4)
    if 'Dfix' in mode: pri.append((D-0.07)/1e-5)
    r.append(np.array(pri+[0.0]))
    return np.concatenate(r)
def fit(mode,p0=None):
    best=None
    starts=[p0] if p0 is not None else [np.array([1.52,0.35,0.0,0.3,th0,ph0,0,0,0.0,9.8,0.07]) for th0 in (0.7,0.85) for ph0 in (np.pi/2,-np.pi/2,0,np.pi)]
    for pp in starts:
        r=least_squares(lambda q: resid(q,mode),pp,iters=80)
        if best is None or r.cost<best.cost: best=r
    return least_squares(lambda q: resid(q,mode),best.x,iters=300)
def summary(name,p):
    q0,L,gh,th,ph,w1,w2,gam,gm,D=unpack(p)
    C,V=integrate(p,nmax=52); Ck=C[n*SUB]; uu,vv,R=proj(Ck)
    pitch=np.degrees(np.arcsin(gh[2])); roll=np.degrees(np.arctan2(gh[0],gh[1]))
    print(f"== {name}: rms u {np.sqrt(np.mean((uu-u)**2)):.2f} v {np.sqrt(np.mean((vv-v)**2)):.2f} w {np.sqrt(np.mean((F*D/R-w)**2)):.2f}  d0 {np.linalg.norm(q0):.4f} L {L:.4f} g {gm:.3f} D {D*100:.2f} gam {gam:.3f} pitch {pitch:.1f} roll {roll:.1f}")
    Cc=C[::SUB]; Vc=V[::SUB]; Rc=np.linalg.norm(Cc,axis=1)
    print('   anchors (model surf - stated, cm):',' '.join(f"c{c}:{(Rc[c]-0.035-s)*100:+.1f}" for c,s in ANCH))
    # turning points: speed minima
    sp=np.linalg.norm(V,axis=1); tt=np.arange(len(sp))/(25*SUB)
    mins=[tt[i]*25 for i in range(1,len(sp)-1) if sp[i]<sp[i-1] and sp[i]<sp[i+1]]
    print('   turning (capture frame):',np.round(mins,2),' max speed',np.round(sp.max(),3))
    out={}
    for c0 in (7,8,15):
        fd=25*np.linalg.norm(Cc[c0+1]-Cc[c0]); inst=np.linalg.norm(Vc[c0])
        a_fd=625*np.linalg.norm(Cc[c0+2]-2*Cc[c0+1]+Cc[c0]); a_inst=np.linalg.norm(25*(Vc[c0+1]-Vc[c0-1])/2)
        dR=(Rc[c0+1]-Rc[c0])*100
        print(f"   c{c0}: FD {fd:.3f} inst {inst:.3f}  aFD {a_fd:.2f} a_inst {a_inst:.2f}  dR {dR:+.2f}cm  dR2 {(Rc[c0+2]-Rc[c0+1])*100:+.2f}  R {Rc[c0]:.4f}")
        out[c0]=dict(fd=fd,inst=inst,afd=a_fd,ainst=a_inst,dR=dR)
    return dict(p=p.tolist(),R=Rc.tolist(),C=Cc.tolist(),V=Vc.tolist(),stats=out)
if __name__=='__main__':
    modes=sys.argv[2].split(',') if len(sys.argv)>2 else ['gfix','gfix+anch','anch','Dfix','gfix+anch+nosize']
    res={}; prev=None
    for m in modes:
        r=fit(m,p0=prev); prev=r.x.copy(); res[m]=summary(m,r.x)
    json.dump(res,open(B+f'pend3d_v2_{K1}.json','w'))
