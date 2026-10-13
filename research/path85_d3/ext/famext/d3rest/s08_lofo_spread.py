"""LOFO for series pooling on stated facts (extended families): effect of a spread guard (skip pooling when the
per-base values span more than a factor S) and of min_bases."""
import sys, pickle
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
W=SP+'/big/scenegraph/work'; EXT=SP+'/ext/d3rest'
sys.path.insert(0,'/home/user/quantiphy-challenge'); sys.path.insert(0,W)
import numpy as np, pandas as pd
from qp.mra import item_scores
from pool2 import per_base_values, gmed
def mra(p,g): return float(item_scores([p],[g])[0])
t=pd.read_pickle(EXT+'/work/TS_ext.pkl'); ti=t.set_index('qid')
A=pd.read_pickle(EXT+'/work/transfers_ext.pkl'); A=A[~A.conflict].copy()
eq=pickle.load(open(EXT+'/work/eq_ext.pkl','rb'))
A['lk']=np.log(A.value/A.v3); A['kind']=ti.loc[A.qid,'tkind'].values; A['method']=ti.loc[A.qid,'method'].values
A['fact']=A.line.str.strip().str.lower()+'|'+A.value.round(6).astype(str)
byv={v:g for v,g in A.groupby('video_id')}
def clipK(v,ex):
    g=byv.get(v)
    if g is None: return 0.0
    g=g[~g.fact.isin(ex)&g.kind.isin(('size','speed'))]
    return float(np.median(np.r_[g.lk.values,0.0])) if len(g) else 0.0
def corr(p,ex,useK):
    rp=ti.loc[p]; val=rp.v3
    if useK and rp.method=='direct' and rp.tkind in ('size','speed'): val*=np.exp(clipK(rp.video_id,ex))
    return val
rows=[]
for fact,g in A.groupby('fact'):
    ex={fact}
    for r in g.itertuples():
        if r.method!='direct': continue
        per=per_base_values(ti,eq,r.qid,include_self=True)
        for useK in (False,True):
            vals=[corr(x[2],ex,useK) for x in per.values()]
            own=corr(r.qid,ex,useK)
            spread=max(vals)/min(vals) if len(vals) else 1
            rows.append(dict(cat=r.cat,qid=r.qid,useK=useK,nb=len(per),spread=spread,raw=mra(r.v3,r.value),own=mra(own,r.value),pool=mra(gmed(vals),r.value)))
R=pd.DataFrame(rows)
for cat in ('D3',):
  for useK in (False,True):
    X=R[(R.cat==cat)&(R.useK==useK)]
    for minb in (2,3):
        for S in (1e9,3.0,2.5,2.0):
            sel=(X.nb>=minb)&(X.spread<=S)
            val=np.where(sel,X.pool,X.own)
            print(cat,'K' if useK else '-', 'minb',minb,'spread<=',S,'n_pooled',int(sel.sum()),'of',len(X),'mean %.3f (own %.3f raw %.3f)'%(val.mean(),X.own.mean(),X.raw.mean()),
                  ' pooled rows: pool %.3f own %.3f'%(X.pool[sel].mean(),X.own[sel].mean()), ' high-spread rows (nb>=minb, spread>S): pool %.3f own %.3f n=%d'%(X.pool[(X.nb>=minb)&(X.spread>S)].mean(),X.own[(X.nb>=minb)&(X.spread>S)].mean(),((X.nb>=minb)&(X.spread>S)).sum()))
