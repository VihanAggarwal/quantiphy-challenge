import sys; sys.path.insert(0,'scripts')
from geo import *
pts=[('book',666.4,617.9,2.082,0.018),('cup',564.3,424.0,2.516,0.06),('ball',985.8,369.6,3.041,0.116),
     ('wb62',705.4,415.3,2.815,0.008),('bag62',837.3,329.1,3.307,0.01)]
X=np.array([P(u,v,r) for _,u,v,r,_ in pts]); z=np.array([p[4] for p in pts])
def nvec(a,b): return np.array([np.sin(b)*np.cos(a), np.cos(b)*np.cos(a), np.sin(a)])
A=np.radians(np.arange(25,45,0.05)); B=np.radians(np.arange(-20,10,0.05))
for sel,name in [([0,1,2,3,4],'all5'),([0,1,2],'0053 only'),([0,1,3,4],'no ball'),([0,3,4],'flat: book,wb,bag')]:
    best=None
    for a in A:
        for b in B:
            n=nvec(a,b); h=X[sel]@n+z[sel]; H=h.mean(); r=((h-H)**2).sum()
            if best is None or r<best[0]: best=(r,a,b,H)
    r,a,b,H=best; n=nvec(a,b)
    vp=(CX+F*n[0]/n[1]*0+F*n[0]/n[2], CY+F*n[1]/n[2])
    print('%-18s pitch(axis-down) %.1f roll %.1f H %.3f'%(name,90-np.degrees(np.arccos(n[2])),np.degrees(b),H),'resid cm',np.round((H-X@n-z)*100,1),'vertVP',np.round(vp,0))
n=DOWN_ROLL
print('VP roll model: resid cm with H=1.689',np.round((1.689-X@n-z)*100,1), 'roll %.1f'%np.degrees(np.arctan2(n[0],n[1])))
