import numpy as np
from a3cam import *
cases={'line-intersections':dict(FL=(939.4,760.9),FR=(1149.5,725.8),BL=(847.7,704.0)),
       'eyeballed tips':dict(FL=(936.0,758.5),FR=(1149.5,723.0),BL=(852.5,704.0))}
for name,C in cases.items():
    for f in (2630.,2650.,2670.):
        th,M=setup(f)
        hN=-3.593*ray(*N,f,M)[2]; hR=-5.009*ray(*R,f,M)[2]; h=(hN+hR)/2
        P={k:onplane(*p,f,M,h) for k,p in dict(N=N,R=R,L=L,F=F).items()}
        ex=(P['R']-P['N'])/np.linalg.norm(P['R']-P['N']); ey=(P['L']-P['N'])/np.linalg.norm(P['L']-P['N'])
        Q={k:onplane(*p,f,M,h) for k,p in C.items()}
        a=Q['FR']-Q['FL']; b=Q['BL']-Q['FL']
        print('%-20s f=%.0f  front (along desk length) %.3f m [u %.3f v %.3f]  left side (depth) %.3f m [u %.3f v %.3f]  angle %.1f  range FL %.3f'%(
            name,f,np.linalg.norm(a),a@ex,a@ey,np.linalg.norm(b),b@ex,b@ey,np.degrees(np.arccos(a@b/np.linalg.norm(a)/np.linalg.norm(b))),np.linalg.norm(Q['FL'])))
