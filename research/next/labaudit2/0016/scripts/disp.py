# Displacement 1.0 s -> 1.5 s, label-style: click at video 24 (capture 25) at range r24; click at 1.5 s at the stated 1.402.
import numpy as np
f=711.; pp=np.array([640.,360.])
def ray(p): v=np.array([p[0]-pp[0],p[1]-pp[1],f]); return v/np.linalg.norm(v)
c24=(285.,597.)
for lab,c15 in [('A: 1.5 s = video 36 (c38)',(812.2,77.2)),('B: 1.5 s = c37 (interp.)',(775.,96.))]:
    s=[]
    for r24 in [1.45,1.50,1.55,1.60,1.65,1.70]:
        s.append('r24=%.2f: %.1f'%(r24,100*np.linalg.norm(1.402*ray(c15)-r24*ray(c24))))
    print(lab,' | '.join(s))
# r24 routes: edge-fit tangential diameter at video 24 (b=40.7-43.3 px) vs video 37 (b=43.6, o render), and matte route at c38
f_=711.
for b24 in [40.7,41.4,42.2,43.3]:
    th=np.arctan(np.hypot(285-640,597-360)/f_)
    for D in [0.170,0.177,0.181]:
        sn=b24*np.cos(th)/np.sqrt(f_*f_+b24*b24); d=D/2/sn
        print('  b24=%.1f D=%.3f -> surface range %.3f'%(b24,D,d-D/2),end=';')
    print()
