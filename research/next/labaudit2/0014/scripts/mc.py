import numpy as np, json, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0014/scripts')
from geo import *
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0014/track_bgdiff.json'))
cen=lambda k: (np.array(T['x'][k]['wcen'])+np.array(T['s'][k]['wcen']))/2
B=board_plane(); n=B['n']
rng=np.random.default_rng(0)
for anchor in ['far','near']:
  c={'far':n@B['Pf'],'near':n@B['Pn']}[anchor]; r=0.0325
  Cc={k:inter(*cen(k),n,c+r) for k in (14,15,16)}
  Rm={k:np.linalg.norm(Cc[k])-r for k in Cc}
  bias=1.7288-Rm[14]
  for sc in [0.5,1.0,2.0]:
    for sp in [1.0,2.0]:
      N=200000
      uv={k:cen(k)[None,:]+rng.normal(0,sp,(N,2)) for k in (14,15,16)}
      R={14:np.full(N,1.7288)}
      for k in (15,16): R[k]=Rm[k]+bias+rng.normal(0,sc/100,N)
      P={}
      for k in (14,15,16):
          d=np.stack([(uv[k][:,0]-CX)/F,(uv[k][:,1]-CY)/F,np.ones(N)],1); d/=np.linalg.norm(d,axis=1,keepdims=True)
          P[k]=d*R[k][:,None]
      v=np.linalg.norm(P[15]-P[14],axis=1)*2500
      v2=np.linalg.norm(P[16]-P[15],axis=1)*2500
      a_vec=np.linalg.norm(P[16]-2*P[15]+P[14],axis=1)*625
      a_spd=(v2-v)*25/100
      ok=np.abs(a_vec-4.6)<0.6; ok2=np.abs(a_spd-4.6)<0.6
      print(f'{anchor:4s} bias {100*bias:+.1f}cm ToFsd {sc}cm click {sp}px: v median {np.median(v):6.1f} mean {v.mean():6.1f} | cond a_vec~4.6 (n={ok.sum():6d}) median {np.median(v[ok]) if ok.sum() else np.nan:6.1f} | cond a_spd~4.6 (n={ok2.sum():6d}) median {np.median(v[ok2]):6.1f}')
