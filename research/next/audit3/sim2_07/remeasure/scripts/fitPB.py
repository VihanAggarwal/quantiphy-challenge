import json, numpy as np, sys
rows=json.load(open('diam2_simulation_0254.json'))
R={int(r[0]):r for r in rows}
fr=np.array(sorted(i for i in R if 19<=i<=46))
cx=np.array([R[i][5] for i in fr]); cy=np.array([R[i][6] for i in fr])
d=np.array([np.cos(np.radians(44.224)),np.sin(np.radians(44.224))])
s=cx*d[0]+cy*d[1]; t=fr/24.0
s37=912.34*d[0]+587.46*d[1]   # image-centre projection ~ frame 37
def Sworld(k,t0,tt):
    tau=np.maximum(tt-t0,0)
    if k<1e-9: return 0.5*tau**2   # per unit a0
    return (tau-(1-np.exp(-k*tau))/k)/k
def Vworld(k,t0,tt):
    tau=np.maximum(tt-t0,0)
    if k<1e-9: return tau
    return (1-np.exp(-k*tau))/k
# image: s = sinf - M/(Sc + a0*Sworld)   -> with sinf fixed, unknowns M, Sc, a0 (scale-redundant: set a0=1 in arbitrary units, fit M,Sc)
def fit_fixed(sinf,k,t0):
    U=Sworld(k,t0,t)
    # s = sinf - M/(Sc+U)  -> (sinf - s)(Sc+U)=M  -> linear in (Sc,M): (sinf-s)*Sc - M = -(sinf-s)*U
    if np.isinf(sinf):
        A=np.c_[np.ones_like(t),U]; c=np.linalg.lstsq(A,s,rcond=None)[0]; r=s-A@c; return (r**2).sum(),('lin',c)
    y=sinf-s
    A=np.c_[y,-np.ones_like(t)]; b=-y*U
    c=np.linalg.lstsq(A,b,rcond=None)[0]; Sc,M=c
    pred=sinf-M/(Sc+U); r=s-pred; return (r**2).sum(),('proj',(Sc,M))
D_C=float(sys.argv[1]) if len(sys.argv)>1 else 24.0
for sinf in (16200.,18988.,25000.,34000.,np.inf):
    best=None
    for k in np.linspace(0,1.0,201):
        for t0 in np.linspace(-0.3,0.2,101):
            e,info=fit_fixed(sinf,k,t0)
            if best is None or e<best[0]: best=(e,k,t0,info)
    e,k,t0,info=best
    # world conversion: local px/m at frame-37 position = 0.991*D_C/0.17 (perspective) ; ds/dU at t37
    t37=37/24
    if info[0]=='proj':
        Sc,M=info[1]; U37=Sworld(k,t0,t37); dsdU=M/(Sc+U37)**2
    else:
        dsdU=info[1][1]
    fac=0.991 if np.isfinite(sinf) else 1.0
    sig=fac*D_C/0.17   # px per metre at centre
    a0=dsdU/sig        # m/s^2 per unit U (U is in units where a0=1)
    def Vb(tq): return a0*(Sworld(k,t0,tq)-Sworld(k,t0,tq-1/24))*24
    def Ab(tq): return (Vb(tq)-Vb(tq-1/24))*24
    def Ai(tq): return a0*np.exp(-k*max(tq-t0,0))
    size_ratio=((sinf-s[-1])/(sinf-s[0])) if np.isfinite(sinf) else 1.0
    print(f'sinf={sinf:7.0f} k={k:.3f} t0={t0:+.3f} rms={np.sqrt(e/len(t)):.3f} size46/19={size_ratio:.3f} | a0={a0:.3f} v_b(0.5)={Vb(0.5):.3f} v_b(1)={Vb(1.0):.3f} a(0.5)={Ai(0.5):.3f}/{Ab(0.5):.3f} a(1.0)={Ai(1.0):.3f}/{Ab(1.0):.3f}')
