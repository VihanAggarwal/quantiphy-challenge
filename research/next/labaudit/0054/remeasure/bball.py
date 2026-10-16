import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure')
from geom import *
R=0.116
for v,near0 in [('bx',(716,536)),('ax',(343,607))]:
    print(v)
    near=near0
    for i in range(8,41):
        cs=comps(v,i)
        cand=[c for c in cs if c['bgr'][2]>c['bgr'][0]+50 and c['A']>800]
        if not cand: continue
        c=min(cand,key=lambda c: np.hypot(*(c['c']-np.array(near))))
        near=c['c']
        n,th,sd,npts=cone_fit(c['mask'])
        P,r=centre3d(n,th,R)
        x,y,w,h=c['bbox']
        print(i, 'c=(%.1f,%.1f) bbox=%dx%d A=%d  angdiam=%.3fdeg  r_centre=%.3f  r_surf=%.3f fitsd=%.3fdeg'%(c['c'][0],c['c'][1],w,h,c['A'],2*np.degrees(th),r,r-R,sd), 'P=',P.round(3))
