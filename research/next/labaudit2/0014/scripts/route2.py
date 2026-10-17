import numpy as np, json, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0014/scripts')
from geo import *
def minimize_scalar(fn,bounds,method=None):
    import types
    a,b=bounds
    for _ in range(3):
        xs=np.linspace(a,b,2001); ys=[fn(x) for x in xs]; i=int(np.argmin(ys)); w=(b-a)/2000; a,b=xs[i]-2*w,xs[i]+2*w
    return types.SimpleNamespace(x=xs[i],fun=ys[i])
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0014/track_bgdiff.json'))
def cen(k,key='wcen',R=('x','s')):
    return np.mean([np.array(T[r][k][key]) for r in R],0)
B=board_plane(); D=(B['Pn']-B['Pf']); D/=np.linalg.norm(D)
print('slope dir (stated anchors)',np.round(D,3),' vs VP dir',np.round(B['d1'],3),' angle deg',round(np.degrees(np.arccos(D@B['d1'])),2))
for f in [680,711,740]:
  for key in ['wcen','cen']:
    P14=bp(*cen(14,key),1.7288,f)
    out=[]
    for k in [12,13,15,16]:
        # move from P14 along D by s so that projection matches centroid k (least squares)
        tgt=cen(k,key)
        res=minimize_scalar(lambda s: np.sum((proj(P14+s*D,f)-tgt)**2),bounds=(-0.3,0.3),method='bounded')
        out.append((k,res.x,np.sqrt(res.fun)))
    s={k:v for k,v,_ in out}; s[14]=0
    v=(s[15]-s[14])*2500; a=(s[16]-2*s[15]+s[14])*62500/100
    print(f'f={f} {key}: s(k) cm',{k:round(100*s[k],2) for k in sorted(s)},'resid px',[round(e,2) for *_,e in out],f' v(14->15)={v:.1f} cm/s  a={a:.2f} m/s2')
# displacement 0 -> 0.6
for f in [711]:
    for key in ['wcen','cen']:
        for c0 in [cen(0,key), np.array([543.7,295.0])]:
            P0=bp(*c0,1.818,f); P14=bp(*cen(14,key),1.7288,f)
            print('disp f',f,key,'c0',np.round(c0,1),'c14',np.round(cen(14,key),1),' |P14-P0| =',round(100*np.linalg.norm(P14-P0),2),'cm')
# radial check: model range drop between f0 and f14 vs stated -8.92
