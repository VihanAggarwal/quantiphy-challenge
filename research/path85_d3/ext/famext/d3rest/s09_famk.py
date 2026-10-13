"""Does a family-level K (from stated facts answered in OTHER clips of the family) help a clip with no facts of its own?
LOFO on D3 stated facts: predict v3 * exp(K_fam_other), where K_fam_other = median over other clips' fact log-ratios (+0)."""
import sys
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
W=SP+'/big/scenegraph/work'; EXT=SP+'/ext/d3rest'
sys.path.insert(0,'/home/user/quantiphy-challenge'); sys.path.insert(0,W)
import numpy as np, pandas as pd
from qp.mra import item_scores
def mra(p,g): return float(item_scores([p],[g])[0])
t=pd.read_pickle(EXT+'/work/TS_ext.pkl'); ti=t.set_index('qid')
A=pd.read_pickle(EXT+'/work/transfers_ext.pkl'); A=A[~A.conflict].copy()
A['lk']=np.log(A.value/A.v3); A['kind']=ti.loc[A.qid,'tkind'].values; A['method']=ti.loc[A.qid,'method'].values
A['fam']=ti.loc[A.qid,'fam'].values; A['base']=ti.loc[A.qid,'base'].values
A=A[A.kind.isin(('size','speed'))&(A.method=='direct')]
rows=[]
for r in A.itertuples():
    g=A[(A.fam==r.fam)&(A.base!=r.base)]
    if not len(g): continue
    kc=g.groupby('video_id').lk.median()       # one value per other clip
    for shrink in (True,False):
        K=float(np.median(np.r_[kc.values,0.0])) if shrink else float(np.median(kc.values))
        rows.append(dict(cat=r.cat,qid=r.qid,shrink=shrink,nclips=len(kc),raw=mra(r.v3,r.value),famK=mra(r.v3*np.exp(K),r.value),corr=np.sign(K)==np.sign(r.lk)))
R=pd.DataFrame(rows)
print(R.groupby(['cat','shrink'])[['raw','famK']].agg(['mean','size']).round(3))
print(R[R.shrink].groupby(['cat',R.nclips.clip(upper=4)])[['raw','famK']].mean().round(3))
