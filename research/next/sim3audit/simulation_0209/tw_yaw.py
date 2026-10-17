# Yaw of a horizontal 3D line (typewriter base edge) relative to the desk long axis, from two image points.
import numpy as np
from a3cam import *
def yaw_of_line(p1,p2,f,M,ex,ey):
    r1=M@np.array([(p1[0]-CX)/f,(p1[1]-CY)/f,1]); r2=M@np.array([(p2[0]-CX)/f,(p2[1]-CY)/f,1])
    n=np.cross(r1,r2); d=np.cross(n,[0,0,1.]); d/=np.linalg.norm(d)
    if d@ex<0: d=-d
    return np.degrees(np.arctan2(d@ey,d@ex))
def _main():
  pass
for f in ([] if __name__!="__main__" else (2630.,2650.,2670.)):
    th,M=setup(f)
    hN=-3.593*ray(*N,f,M)[2]; hR=-5.009*ray(*R,f,M)[2]; h=(hN+hR)/2
    P={k:onplane(*p,f,M,h) for k,p in dict(N=N,R=R,L=L,F=F).items()}
    ex=(P['R']-P['N'])/np.linalg.norm(P['R']-P['N']); ey=(P['L']-P['N'])/np.linalg.norm(P['L']-P['N'])
    out=[]
    # glass take (0205/0202): base front-bottom edge, left-front corner -> right-front corner; also left side edge
    out.append(('0205 base front edge', yaw_of_line((940.,756.7),(1148.3,723.3),f,M,ex,ey)))
    out.append(('0205 base left edge (vs short axis, +90 expected)', yaw_of_line((940.,756.7),(853.3,703.3),f,M,ex,ey)))
    out.append(('0202 notes FL->FR', yaw_of_line((1003,757),(1158,706),f,M,ex,ey)))
    # typewriter take frame 0 (0209): base front-bottom edge from gridded crop
    out.append(('0209 f0 base front edge', yaw_of_line((1100.,94.),(1400.,97.5),f,M,ex,ey)))
    print('f=%.0f '%f+'  '.join('%s: %.1f'%o for o in out))
