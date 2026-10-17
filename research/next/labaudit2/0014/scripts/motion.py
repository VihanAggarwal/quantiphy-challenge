import numpy as np, json, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0014/scripts')
from geo import *
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0014/track_bgdiff.json'))
def cen(k,key='wcen'):
    a=np.array(T['x'][k][key]); b=np.array(T['s'][k][key]); return (a+b)/2
cap=lambda k: k+(k>=12)+(k>=36)
B=board_plane()
n=B['n']
for anchor in ['far','near','mid']:
  for r in [0.0300,0.0325,0.0350]:
    c={'far':n@B['Pf'],'near':n@B['Pn'],'mid':(n@B['Pf']+n@B['Pn'])/2}[anchor]
    Cs={}; Ls={}
    for k in range(10,17):
        u,v=cen(k)
        Cb=inter(u,v,n,c+r)  # ball center
        Cs[k]=Cb; Ls[k]=(np.linalg.norm(Cb)-r)*ray(u,v)
    st=[100*np.linalg.norm(Cs[k+1]-Cs[k]) for k in range(12,16)]
    stL=[100*np.linalg.norm(Ls[k+1]-Ls[k]) for k in range(12,16)]
    rng={k:round(np.linalg.norm(Ls[k]),4) for k in (12,13,14,15,16)}
    print(f'{anchor:4s} r={r:.4f} center steps 12..16 {np.round(st,2)} label steps {np.round(stL,2)}  v(14->15)*25={stL[2]*25:.1f}  a2nd={(stL[3]-stL[2])*625/100:.2f} m/s2  surf ranges {rng}')
# stated-range variants
r=0.0325; c=n@B['Pf']
u0,v0=cen(0); u14,v14=cen(14); u15,v15=cen(15)
print('centres f0',np.round(cen(0),1),'f14',np.round(cen(14),1),'f15',np.round(cen(15),1),'f16',np.round(cen(16),1))
