# Plane-route 3D tracks (ball centre at height r above the table plane), capture clock
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/scripts')
from common import *
from geo import plane, X_on, T, C
f=float(sys.argv[1]) if len(sys.argv)>1 else 711.
n,Ki,_=plane(f)
HS={'wht':0.1757,'yel':0.1770}
for key,rad,ks in [('wht',0.02,range(30,49)),('yel',0.0335,range(20,47))]:
    h=HS[key]
    print('====',key,'h',h)
    for r in ['x','o']:
        P={};
        for k in ks:
            t=T[r][str(k)][key]
            if t is None: continue
            P[k]=X_on((t['cx'],t['cy']),n,Ki,h-rad)
        kk=sorted(P)
        print(' render',r)
        for a,b in zip(kk[:-1],kk[1:]):
            dc=cap(b)-cap(a); d=(P[b]-P[a])/dc
            Ru=P[a]/np.linalg.norm(P[a]); rad_c=d@Ru; lat=np.linalg.norm(d-rad_c*Ru)
            print('  v%2d c%2d R=%.3f surf=%.3f  step/cap %.2f cm  -> %.1f cm/s (radial %.1f lateral %.1f)'%(a,cap(a),np.linalg.norm(P[a]),np.linalg.norm(P[a])-rad,100*np.linalg.norm(d),2500*np.linalg.norm(d),2500*rad_c,2500*lat))
