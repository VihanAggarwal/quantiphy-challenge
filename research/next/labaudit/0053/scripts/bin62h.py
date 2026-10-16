import sys, numpy as np; sys.path.insert(0,'scripts')
from models import M
def proj(m,X):
    return np.array([640+m.f*X[0]/X[2], 360+m.f*X[1]/X[2]])
for m in M:
    for (ub,vb),(ut,vt) in [((343,203),(340,132.5)),((310,200),(292,125)),((374,199),(379,127))]:
        X0=m.fp(ub,vb,0.0)
        # find h such that projection of X0 - h*dn has v = vt
        hs=np.linspace(0,0.8,8001)
        vs=np.array([proj(m,X0-h*m.dn)[1] for h in hs])
        h=hs[np.argmin(np.abs(vs-vt))]
        print('%-26s bottom (%d,%d) top v %.1f -> range %.2f h=%.3f'%(m.name,ub,vb,vt,np.linalg.norm(X0),h))
