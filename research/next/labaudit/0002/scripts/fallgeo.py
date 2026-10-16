import numpy as np, sys
sys.path.insert(0,'scripts')
from tablegeo import geo
for f in [711,730]:
    K,n,h,ray=geo(f)
    P=lambda p,off=0.0: ray(p)*(h-off)/(n@ray(p))
    proj=lambda X: (K@X)[:2]/X[2]
    bb=P((612,420)); fe=P((605,488.5))
    d=np.linalg.norm(fe-bb); print('f',f,'board-bottom to front edge on table: %.3f m'%d, '-> speed if 5 frames: %.2f m/s, if 4.5: %.2f'%(d/(5/24),d/(4.5/24)))
    up=-n  # unit up (toward camera side)
    dirn=(fe-bb)/d
    for v in [1.2,1.5,1.8]:
        for k,wpx in [(41,27.8),(42,None),(43,29.3),(44,31.7)]:
            t=(k-41)/24.0
            C=fe+up*0.029+dirn*v*t - up*0.5*9.8*t*t
            R=np.linalg.norm(C); u=proj(C)
            s='' if wpx is None else ' size %.1f mm'%(wpx*R/f*1000)
            print('   v=%.1f frame %d: proj (%.0f,%.0f) range %.3f%s'%(v,k,u[0],u[1],R,s))
