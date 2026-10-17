# expected item score of the three distance rows (one shared label) under interpretation I (from t=1.0) vs II (from the start)
import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0029/scripts')
from frames import frames
import json
THR=np.array([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95])
def mra(a,L): return ((np.abs(a-L)/L)[...,None]<1-THR).mean(-1).mean()
rng=np.random.default_rng(0)
LI=np.concatenate([rng.normal(28.9,0.3,10000),rng.normal(30.7,1.8,10000)])   # chord / noisy path-sum variants
LII=rng.normal(68.0,3.0,20000)
opts={'current (30.0/43.2/43.2)':(30.024,43.2,43.2),'all 30.0':(30.024,)*3,'all 43.2':(43.2,)*3,'all 68':(68.,)*3,'all 36':(36.,)*3}
print('%-26s'%'answer set'+''.join('  p(I)=%.1f'%p for p in [0.2,0.3,0.4,0.5,0.6,0.7]))
for nm,a in opts.items():
    sI=np.mean([mra(v,LI) for v in a]); sII=np.mean([mra(v,LII) for v in a])
    print('%-26s'%nm+''.join('  %8.3f'%(p*sI+(1-p)*sII) for p in [0.2,0.3,0.4,0.5,0.6,0.7]), '   (s_I %.2f, s_II %.2f)'%(sI,sII))
