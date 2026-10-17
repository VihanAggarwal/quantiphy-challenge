# Per-frame centre range of the white ball: plane route vs size route (exact silhouette, prop model, c fitted over 36..48)
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/scripts')
from common import *
from geo import plane, X_on
from sil import extents
TB=json.load(open(D+'topbot.json'))
n,Ki,_=plane(711.)
def rayu(p): r=Ki@np.array([p[0],p[1],1.]); return r/np.linalg.norm(r)
for rr in ['x','o']:
    U={k:np.array([(TB[rr][str(k)]['left']+TB[rr][str(k)]['right'])/2,(TB[rr][str(k)]['top']+TB[rr][str(k)]['bot'])/2]) for k in range(33,49)}
    W={k:TB[rr][str(k)]['right']-TB[rr][str(k)]['left'] for k in U}
    Xu={k:X_on(U[k],n,Ki,1.0) for k in U}; s=1.373/np.linalg.norm(Xu[36])
    print('render',rr)
    rows=[]
    for k in range(33,49):
        RP=np.linalg.norm(Xu[k])*s
        u=rayu(U[k]); C=u*RP; wp=extents(C,0.02)[0]
        rows.append((k,RP,wp,W[k]))
    rat=np.array([r[3]/r[2] for r in rows if r[0]>=36])
    print('  measured/predicted width ratio (36..48): mean %.3f sd %.3f'%(rat.mean(),rat.std()))
    t=np.array([cap(r[0]) for r in rows if r[0]>=36]); 
    pp=np.polyfit(t,rat,1); print('  trend of ratio per capture frame: %.4f  (%.1f%% over 12 frames)'%(pp[0],100*pp[0]*12/rat.mean()))
    for k,RP,wp,wm in rows: print('  v%2d c%2d  R_plane %.3f  w_pred %.2f  w_meas %.2f  ratio %.3f'%(k,cap(k),RP,wp,wm,wm/wp))
