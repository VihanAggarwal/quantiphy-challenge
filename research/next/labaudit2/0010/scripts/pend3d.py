"""3D spherical-pendulum fit on the 25 fps capture clock (video k -> capture k+(k>=12)+(k>=36)).
Observations: s-render centroid (u,v), half-max width (size); optional stated anchors.
Modes: 'dyn' : g=9.8 fixed, size scale D free (absolute scale from dynamics)
       'size': D=7cm fixed, g free (scale from ball size)
       'anch': g free, D free, scale from the stated anchors only (surface = centre range - 3.5cm)
Ball centre = pivot(t) + x(t); x: constrained Cartesian pendulum with linear damping, RK4 (8 substeps/frame)."""
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0010/scripts')
from common import *
from lm import least_squares
B='/home/user/quantiphy-challenge/research/next/labaudit2/0010/'
T=json.load(open(B+'track.json')); S=json.load(open(B+'size_s.json'))
k=np.arange(49); n=np.array([cap(i) for i in k]); tc=n/25.0
u=np.array([T['s'][i]['u'] for i in k]); v=np.array([T['s'][i]['v'] for i in k]); w=np.array([S[i]['wh'] for i in k])
STATED=[(0.3,1.7060),(0.6,1.3440),(0.9,1.4605),(1.2,1.7840),(1.5,1.7170),(1.8,1.3500)]
SUB=8; NMAX=52
def unpack(p):
    q0=p[0:3]; dq=np.r_[p[3:5],0.0]; L=p[5]; a,b=p[6],p[7]
    gh=np.array([a,1.0,b]); gh/=np.linalg.norm(gh)
    return q0,dq,L,gh,p[8],p[9],p[10],p[11],p[12],p[13],p[14]
def basis(gh):
    e1=np.cross(gh,[0,0,1.0]); e1/=np.linalg.norm(e1); e2=np.cross(gh,e1); return e1,e2
def integrate(p):
    """returns ball centre C and velocity V on a fine grid t = j/(25*SUB), j=0..NMAX*SUB"""
    q0,dq,L,gh,th,ph,w1,w2,gam,gm,D=unpack(p)
    g=gm*gh; e1,e2=basis(gh)
    x=L*(np.cos(th)*gh+np.sin(th)*(np.cos(ph)*e1+np.sin(ph)*e2))
    t1=np.cross(x,gh); t1/=np.linalg.norm(t1); t2=np.cross(x,t1); t2/=np.linalg.norm(t2)
    vv=w1*t1+w2*t2
    def f(x,vv):
        lam=(x@g+vv@vv)/(x@x); return vv, g-lam*x-gam*vv
    h=1/(25*SUB); N=NMAX*SUB+1
    X=np.zeros((N,3)); Vv=np.zeros((N,3)); X[0]=x; Vv[0]=vv
    for j in range(1,N):
        k1x,k1v=f(x,vv); k2x,k2v=f(x+h/2*k1x,vv+h/2*k1v); k3x,k3v=f(x+h/2*k2x,vv+h/2*k2v); k4x,k4v=f(x+h*k3x,vv+h*k3v)
        x=x+h/6*(k1x+2*k2x+2*k3x+k4x); vv=vv+h/6*(k1v+2*k2v+2*k3v+k4v)
        x=x/np.linalg.norm(x)*L; vv=vv-(vv@x)/(x@x)*x
        X[j]=x; Vv[j]=vv
    tt=np.arange(N)*h
    return tt, q0[None,:]+dq[None,:]*tt[:,None]+X, dq[None,:]+Vv
def at(p,ncap):
    tt,C,V=integrate(p); idx=np.round(np.asarray(ncap,float)*SUB).astype(int); return C[idx],V[idx]
def proj(C):
    return CX+F*C[:,0]/C[:,2], CY+F*C[:,1]/C[:,2], np.linalg.norm(C,axis=1)
def anchors_cap(conv):
    # capture frame (possibly fractional) of each stated time
    out=[]
    for t,s in STATED:
        x=t*25
        if conv=='treal':
            kk=int(np.round(t*24)); c=cap(kk)
        elif conv=='floor': c=np.floor(x)
        elif conv=='ceil': c=np.ceil(x)
        else: c=x   # exact (fractional)
        out.append((c,s))
    return out
def resid(p,mode,anc=None,su=0.7,sw=1.0,sa=0.02):
    q0,dq,L,gh,th,ph,w1,w2,gam,gm,D=unpack(p)
    tt,C,V=integrate(p)
    Ck=C[n*SUB]; uu,vv,R=proj(Ck)
    r=[(uu-u)/su,(vv-v)/su,(F*D/R-w)/sw]
    if anc is not None:
        for c,s in anc:
            j=c*SUB; j0=int(np.floor(j)); fr=j-j0
            Ca=C[j0]*(1-fr)+C[min(j0+1,len(C)-1)]*fr
            r.append(np.array([(np.linalg.norm(Ca)-0.035-s)/sa]))
    pri=[]
    if mode in ('dyn',): pri.append((gm-9.8)/1e-4)
    if mode=='size': pri.append((D-0.07)/1e-5)
    r.append(np.array(pri+[0.0]))
    return np.concatenate(r)
def fit(mode,anc=None,p0=None):
    best=None
    if p0 is not None: starts=[p0]
    else:
        starts=[]
        for ph0 in [np.pi/2,-np.pi/2,0,np.pi]:
            for th0 in [0.6,0.8]:
                starts.append(np.array([0.0,-0.30,1.55,0,0,0.36,0.0,0.15, th0,ph0,0.0,0.0,0.0,9.8,0.07]))
    for pp in starts:
        r=least_squares(lambda q: resid(q,mode,anc),pp,iters=150)
        if best is None or r.cost<best.cost: best=r
    r=least_squares(lambda q: resid(q,mode,anc),best.x,iters=400)
    return r
def report(name,p,anc=None):
    q0,dq,L,gh,th,ph,w1,w2,gam,gm,D=unpack(p)
    tt,C,V=integrate(p); Ck=C[n*SUB]; uu,vv,R=proj(Ck)
    print(f"== {name}: rms u {np.sqrt(np.mean((uu-u)**2)):.2f} v {np.sqrt(np.mean((vv-v)**2)):.2f} w {np.sqrt(np.mean((F*D/R-w)**2)):.2f}px")
    print(f"   pivot {np.round(q0,3)} pix ({CX+F*q0[0]/q0[2]:.1f},{CY+F*q0[1]/q0[2]:.1f}) drift/s {np.round(dq,3)} L {L:.4f} g {gm:.3f} D {D*100:.2f}cm gam {gam:.3f} ghat {np.round(gh,3)}")
    for (t,s) in STATED:
        cs=sorted(set([int(np.floor(t*25)),int(np.ceil(t*25))]))
        txt=' '.join(f"c{c}:{np.linalg.norm(C[c*SUB])-0.035:.4f}" for c in cs)
        print(f"   t={t} stated {s:.4f} model surf {txt}  c{t*25:.1f}:{np.linalg.norm(C[int(round(t*25*SUB))])-0.035:.4f}")
if __name__=='__main__':
    res={}
    for mode in ['dyn','size']:
        r=fit(mode); res[mode]=r.x.tolist(); report(mode,r.x)
    for conv in ['treal','exact','floor']:
        r=fit('anch',anchors_cap(conv),p0=np.array(res['dyn'])); res['anch_'+conv]=r.x.tolist(); report('anch_'+conv,r.x)
        print('   anchor resid (cm):',np.round(r.fun[147:153]*2,2))
    json.dump(res,open(B+'pend3d.json','w'))
