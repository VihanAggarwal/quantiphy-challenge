# Static rows: ball-ball distance at t=1.5 (label style: stated ranges x click rays; c38 and interpolated c37),
# table edges by the plane anchored on the stated ball ranges, white-ball diameter from the half-max width.
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/scripts')
from common import *
from geo import plane, X_on, C
from sil import extents
T=json.load(open(D+'track.json')); TB=json.load(open(D+'topbot.json'))
for f in [711.,770.]:
    def rayu(p): r=np.array([(p[0]-640)/f,(p[1]-360)/f,1.]); return r/np.linalg.norm(r)
    for rr in ['x','o','s']:
        y=lambda k: np.array([T[rr][str(k)]['yel']['cx'],T[rr][str(k)]['yel']['cy']])
        w=lambda k: np.array([T[rr][str(k)]['wht']['cx'],T[rr][str(k)]['wht']['cy']])
        d38=100*np.linalg.norm(1.183*rayu(y(36))-1.353*rayu(w(36)))
        d37=100*np.linalg.norm(1.183*rayu((y(35)+y(36))/2)-1.353*rayu((w(35)+w(36))/2))
        # centre-to-centre physical (add radii along rays)
        c38=100*np.linalg.norm((1.183+0.0335)*rayu(y(36))-(1.353+0.02)*rayu(w(36)))
        print('f%.0f %s distance t1.5: surface clicks c38 %.2f  c37 %.2f | centre-centre c38 %.2f'%(f,rr,d38,d37,c38))
    n,Ki,_=plane(f)
    for hh in [0.1757,0.1770]:
        P={k:X_on(v,n,Ki,hh) for k,v in C.items()}
        print('  f%.0f h=%.4f: front %.1f back %.1f left %.1f right %.1f cm'%(f,hh,100*np.linalg.norm(P['FR']-P['FL']),100*np.linalg.norm(P['BR']-P['BL']),100*np.linalg.norm(P['FL']-P['BL']),100*np.linalg.norm(P['FR']-P['BR'])))
# white ball diameter: measured half-max width vs exact silhouette at stated range, frames 36..40 (o,x)
for rr in ['x','o']:
    for k in [36,37,38]:
        q=TB[rr][str(k)]; u=np.array([(q['left']+q['right'])/2,(q['top']+q['bot'])/2])
        ray=np.array([(u[0]-640)/711,(u[1]-360)/711,1.]); ray/=np.linalg.norm(ray)
        # stated surface range at c38 (k=36); other frames via plane ratio
        R=1.373 if k==36 else None
        if R is None: continue
        wp=extents(ray*R,0.02)[0]; wm=q['right']-q['left']
        print('  %s v%d: measured w %.2f px, silhouette for D=4.0 at stated range %.2f px -> D_est %.2f cm (f711), %.2f cm (f770 equiv)'%(rr,k,wm,wp,4.0*wm/wp,4.0*wm/wp*711/770))
