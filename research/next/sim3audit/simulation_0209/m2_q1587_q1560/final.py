# Final numbers for qid 1587 (letter length, 0209) and qid 1560 (typewriter width, 0202)
import numpy as np
from cam import *
ratio_frontal=0.1267   # letter X-extent / inlay X-extent at same image row (frontal clips 0203/0204/0207/0208, all rows 983-1000)
for f,thd in [(2630,13.27),(2655,13.39),(2680,13.50)]:
    th=np.radians(thd)
    h=-pt_range(704,875,3.593,f,th)[2]          # desk plane from near-corner range
    BL=on_plane(1315.78,624.35,h,f,th); FL=on_plane(1362.99,643.13,h,f,th); BR=on_plane(1442.5,607.2,h,f,th)
    I={k:on_plane(*v,h,f,th) for k,v in {'FL':(749,825),'FR':(1868.6,631.4),'BL':(577.5,691),'BR':(1583,549.5)}.items()}
    Linl=(np.linalg.norm(I['FR']-I['FL'])+np.linalg.norm(I['BR']-I['BL']))/2
    r1=np.linalg.norm(BR-BL); r2=ratio_frontal*Linl
    # typewriter 0202
    tFL=on_plane(1006.3,758.1,h,f,th); tFR=on_plane(1158.1,703.6,h,f,th)
    e=tFR-tFL; yaw_tw=np.degrees(np.arctan2(e[1],e[0])); yaw_desk=np.degrees(np.arctan2(*(I['FR']-I['FL'])[[1,0]]))
    print(f'f={f} th={thd} h={h:.3f}: letter route1(3D, BR from patch)={r1:.4f} side={np.linalg.norm(FL-BL):.4f} | inlay L={Linl:.4f} route2(frontal ratio)={r2:.4f}')
    print(f'   typewriter 0202 base front={np.linalg.norm(e):.4f} yaw rel desk={yaw_tw-yaw_desk:.1f}')
for psi in [17.5,19.5,21.0]:
    for l,w in [(0.37,0.30),(0.375,0.305),(0.38,0.31)]:
        p=np.radians(psi); print(f'psi={psi} l={l} w={w}: AABB_Y={l*np.sin(p)+w*np.cos(p):.3f} AABB_X={l*np.cos(p)+w*np.sin(p):.3f}')
