import numpy as np
from cam import *
P={'FL':(749,825),'FR':(1868.6,631.4),'BL':(577.5,691),'BR':(1583,549.5)}
for f,thd,h in [(2652,13.38,1.25),(2620,13.3,1.25),(2690,13.5,1.25),(2652,13.38,1.235),(2652,13.38,1.265)]:
    th=np.radians(thd); Q={k:on_plane(*v,h,f,th) for k,v in P.items()}
    d=lambda a,b: np.linalg.norm(Q[a]-Q[b])
    e1=Q['FR']-Q['FL']; e2=Q['BL']-Q['FL']
    ang=np.degrees(np.arccos(e1@e2/np.linalg.norm(e1)/np.linalg.norm(e2)))
    print(f'f={f} th={thd} h={h}: front {d("FL","FR"):.4f} back {d("BL","BR"):.4f} left {d("FL","BL"):.4f} right {d("FR","BR"):.4f} angleFL {ang:.1f}')
