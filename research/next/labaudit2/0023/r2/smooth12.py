import numpy as np, json
from geo import *
T=json.load(open(D+'cover_track.json'))
def cap(k): return k if k<=11 else (k+1 if k<=35 else k+2)
H=0.0146
for route in ['stated','ruler']:
    M=board_model(route); p0=M['B']+M['n']*H
    for pre in ['x','o']:
        P={k:hit_plane(p0,M['n'],T[pre][k]['cx'],T[pre][k]['cy']) for k in range(18,32)}
        # path length along track (3D) from start
        s={k:-(P[k]-M['B'])@M['u']*100 for k in P}
        steps=[(cap(k),np.linalg.norm(P[k+1]-P[k])*100) for k in range(21,30)]
        for a,b in [(22,30),(24,30),(25,30),(26,30)]:
            ks=np.arange(a,b+1); tc=np.array([cap(k)/25 for k in ks]); ss=np.array([s[k] for k in ks])
            p=np.polyfit(tc,ss,2); dp=np.polyder(p)
            print(f'{route:6s} {pre} fit v{a}-v{b}: a={2*p[0]/100:.2f} m/s2  v(1.20)={np.polyval(dp,1.2):.1f}  v(1.22)={np.polyval(dp,1.22):.1f}  fwd-diff of fit c30->31 = {(np.polyval(p,1.24)-np.polyval(p,1.2))*25:.1f}')
        print('   steps (cm per capture frame):',' '.join('c%d:%.2f'%x for x in steps))
