import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure')
import numpy as np, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import route2_a as r2
from pts import aW,aG
from vel import orig
vext={'W':{25:16.5,26:17.1,27:16.9,28:17.8},'G':{25:15.8,26:15.8,27:16.6,28:17.6}}
for nm,tr,ks in [('W',aW,list(range(25,38))),('G',aG,list(range(25,37)))]:
    p,rms,model,tau=r2.fit(tr,ks,25)
    P0=p[:3];V0=p[3:6]
    for k in [25,26,27,28]:
        t=(orig(k)-orig(25))/25; P=P0+V0*t+0.5*r2.gvec*t*t; r=np.linalg.norm(P)
        print(f'{nm} frame {k}: range(route2) {r:.3f} m, vext {vext[nm][k]} px -> D = {vext[nm][k]*r/711*100:.2f} cm')
