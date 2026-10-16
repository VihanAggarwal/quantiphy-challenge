import numpy as np, sys
sys.path.insert(0,'scripts')
from conefit import conefit, rays
F=711.
def ang(p,q,f=F):
    r=rays(np.array([p,q],float),f); return np.arccos(np.clip(r[0]@r[1],-1,1))
def report(name,L,Rr,T=None,B=None,f=F):
    ah=ang(L,Rr,f); s='%s f=%d horiz 2alpha=%.4f'%(name,f,ah)
    if T is not None: av=ang(T,B,f); s+=' vert 2alpha=%.4f'%av
    print(s); return ah
for f in (690,711,730):
    a0=report('t0 (o render)',(551.5,510),(673.5,510),(612,443.5),(612,572),f)
    a1=report('t1 (o render)',(501,545),(642.5,545),(572,465),(572,622),f)
    a1x=report('t1 (x mask)',(498,540),(645,540),None,None,f)
    for r1 in (2.612,):
        for A1 in (a1,a1x):
            s1=np.sin(A1/2); R=r1*s1/(1-s1); D1=r1+R
            D0=R/np.sin(a0/2); r0=D0-R
            print('   A1=%.4f -> R=%.4f (diam %.1f cm), D1=%.3f; t0: D0=%.3f, surface range r0=%.3f; label-emul diam (A1*r1)=%.1f cm, (A1*D1)=%.1f'%(A1,R,200*R,D1,D0,r0,100*A1*r1,100*A1*D1))
