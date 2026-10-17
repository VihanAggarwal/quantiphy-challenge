# v(1.4) route B: direction of travel from the vanishing point (image track line meets the horizon), X35 from the stated
# range 0.738 m (+2 cm to the centre), X36 = point of that 3D line closest to the c36 click ray. No table size / camera height.
import numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0033/scripts')
from geo import *
for R in ['x','s']:
  T=load_track(R); Cp=json.load(open(BASE+'capsule_%s.json'%R)); inv={cap(k):k for k in T}
  for key in ['mid','centroid']:
    get=(lambda c: np.array(Cp[str(inv[c])]['mid'])) if key=='mid' else (lambda c: np.array([T[inv[c]]['cx'],T[inv[c]]['cy']]))
    for f in [711,740]:
      P=pose(f); n=P['n']
      for span in ([(30,36),(31,36),(33,36)] if R=="x" else [(31,36),(33,36)]):
        cs=range(span[0],span[1]+1); pts=np.array([get(c) for c in cs])
        A=np.vstack([pts[:,0],np.ones(len(pts))]).T; m,b=np.linalg.lstsq(A,pts[:,1],rcond=None)[0]  # v = m u + b
        # horizon: image of directions perpendicular to n: points with n.(K^-1 [u,v,1]) = 0
        # n0 (u-640)/f + n1 (v-360)/f + n2 = 0 ; intersect with v = m u + b
        a1=n[0]/f+n[1]/f*m; c1=n[1]/f*(b-360)-n[0]*640/f+n[2]
        u_vp=-c1/a1; v_vp=m*u_vp+b
        d=np.array([(u_vp-640)/f,(v_vp-360)/f,1.]); d/=np.linalg.norm(d)
        X35=(73.8+2.0)*ray(*get(35),f)
        def closest(rr):  # point on line X35 + s d closest to ray rr (through origin)
            # minimise |X35 + s d - t rr|
            M=np.array([[d@d,-d@rr],[d@rr,-rr@rr]]); rhs=np.array([-(X35@d),-(X35@rr)])
            s,t=np.linalg.solve(M,rhs); return X35+s*d, np.linalg.norm(X35+s*d-t*rr)
        X36,miss=closest(ray(*get(36),f)); X34,_=closest(ray(*get(34),f)); X33,_=closest(ray(*get(33),f))
        v=np.linalg.norm(X36-X35)*25; vb=np.linalg.norm(X35-X33)*25/2
        # label-style surface ranges
        print('%s %-8s f%d c%d-%d VP (%.0f,%.1f) dX/dZ %.3f | c35->36 %.0f cm/s (miss %.2f cm), range36 %.1f | c33->35 mean %.0f'%(R,key,f,span[0],span[1],u_vp,v_vp,d[0]/d[2],v,miss,np.linalg.norm(X36),vb))
