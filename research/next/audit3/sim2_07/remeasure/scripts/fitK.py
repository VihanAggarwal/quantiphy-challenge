import json, numpy as np, sys
exec(open('scripts/fitPB.py').read().split('D_C=')[0])
k=float(sys.argv[1]); D_C=float(sys.argv[2])
best=None
for sinf in np.arange(14000,40001,250):
    for t0 in np.linspace(-0.15,0.1,101):
        e,info=fit_fixed(sinf,k,t0)
        if best is None or e<best[0]: best=(e,sinf,t0,info)
e,sinf,t0,info=best
# refine
for it in range(3):
    for s2 in np.linspace(sinf-300,sinf+300,25):
        for t2 in np.linspace(t0-0.005,t0+0.005,21):
            e2,info2=fit_fixed(s2,k,t2)
            if e2<e: e,sinf,t0,info=e2,s2,t2,info2
Sc,M=info[1]; t37=37/24; U37=Sworld(k,t0,t37); dsdU=M/(Sc+U37)**2
a0=dsdU/(0.9918*D_C/0.17)
Vb=lambda tq: a0*(Sworld(k,t0,tq)-Sworld(k,t0,tq-1/24))*24
Ab=lambda tq: (Vb(tq)-Vb(tq-1/24))*24
Ai=lambda tq: a0*np.exp(-k*max(tq-t0,0))
print(f'k={k} D_C={D_C}: VP s_inf={sinf:.0f} t0={t0:+.4f} rms={np.sqrt(e/len(t)):.3f} | a0={a0:.3f} vb(.5)={Vb(.5):.3f} vb(1)={Vb(1):.3f} vb(1.5)={Vb(1.5):.3f} vb(1.75)={Vb(1.75):.3f} a(.5)={Ai(.5):.3f}/{Ab(.5):.3f} a(1)={Ai(1):.3f}/{Ab(1):.3f} a(1.5)={Ai(1.5):.3f}')
