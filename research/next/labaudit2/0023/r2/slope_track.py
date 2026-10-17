import numpy as np, json
from geo import *
T=json.load(open(D+'cover_track.json'))
def cap(k): return k if k<=11 else (k+1 if k<=35 else k+2)
H=0.0146
for route in ['stated','ruler']:
    M=board_model(route); p0=M['B']+M['n']*H
    print('==',route)
    for pre in ['x','o']:
        P={}
        for k in range(18,32):
            t=T[pre][k]; X=hit_plane(p0,M['n'],t['cx'],t['cy']); P[k]=X
        s={k:(P[k]-M['B'])@M['u']*100 for k in P}
        rows=[]
        for k in range(18,31):
            c=cap(k); dc=cap(k+1)-c
            v=np.linalg.norm(P[k+1]-P[k])*25/dc*100
            rows.append((k,c,np.linalg.norm(P[k]),s[k],v))
        print(pre,' '.join('v%d/c%d r%.3f s%.1f v%.0f'%r for r in rows))
        # constant-accel fit of s vs capture time over k=21..30 (motion)
        ks=np.arange(22,31); tc=np.array([cap(k)/25 for k in ks]); ss=np.array([s[k] for k in ks])
        p=np.polyfit(tc,ss,2); a=2*p[0]; 
        res=ss-np.polyval(p,tc)
        v12=np.polyval(np.polyder(p),1.2); v122=np.polyval(np.polyder(p),1.22)
        print('   quad fit k22-30: a=%.1f cm/s2 (%.2f m/s2), v(1.2)=%.1f v(1.22)=%.1f, resid sd %.2f cm, t0(v=0)=%.3f'%(a,a/100,-v12,-v122,res.std(),-p[1]/(2*p[0])))
