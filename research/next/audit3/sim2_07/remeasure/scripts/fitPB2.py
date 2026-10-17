import json, numpy as np, sys
exec(open('scripts/fitPB.py').read().split('D_C=')[0])
def run(sinf,kfix=None,D_C=24.0,quiet=False):
    best=None
    ks=[kfix] if kfix is not None else np.linspace(0,0.5,251)
    for k in ks:
        for t0 in np.linspace(-0.2,0.2,161):
            e,info=fit_fixed(sinf,k,t0)
            if best is None or e<best[0]: best=(e,k,t0,info)
    e,k,t0,info=best
    t37=37/24; Sc,M=info[1]; U37=Sworld(k,t0,t37); dsdU=M/(Sc+U37)**2
    sig=0.991*D_C/0.17; a0=dsdU/sig
    Vb=lambda tq: a0*(Sworld(k,t0,tq)-Sworld(k,t0,tq-1/24))*24
    Ab=lambda tq: (Vb(tq)-Vb(tq-1/24))*24
    Ai=lambda tq: a0*np.exp(-k*max(tq-t0,0))
    print(f'sinf={sinf:6.0f} k={k:.3f} t0={t0:+.4f} rms={np.sqrt(e/len(t)):.3f} D_C={D_C} | a0={a0:.3f} vb(.5)={Vb(.5):.3f} vb(1)={Vb(1):.3f} vb(1.5)={Vb(1.5):.3f} vb(1.75)={Vb(1.75):.3f} a(.5)={Ai(.5):.3f}/{Ab(.5):.3f} a(1)={Ai(1):.3f}/{Ab(1):.3f}')
for sinf in (19000.,21700.,24000.):
    run(sinf)
    run(sinf,kfix=0.0408)
    run(sinf,kfix=0.0593)
