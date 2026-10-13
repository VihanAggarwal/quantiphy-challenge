"""Leave-one-fact-out on stated facts with old vs extended families.
For each stated fact (a transferred T value) and each direct-routed question it answers, hold the fact out of K
and predict the question from: raw v3 / K / pool / K+pool (pool = geometric median over distinct bases of the
equivalence group, K-corrected), with min_bases B. Score with qp.mra.item_scores against the stated value."""
import sys, os, pickle
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
W=SP+'/big/scenegraph/work'; EXT=SP+'/ext/d3rest'
sys.path.insert(0,'/home/user/quantiphy-challenge'); sys.path.insert(0,W)
import numpy as np, pandas as pd
from qp.mra import item_scores
from pool2 import per_base_values, gmed
def mra(p,g): return float(item_scores([p],[g])[0])
def run(t, A, eq, minb=3, cats=('D3',), only=None, label=''):
    ti=t.set_index('qid')
    A=A[~A.conflict].copy()
    A['lk']=np.log(A.value/A.v3); A['kind']=ti.loc[A.qid,'tkind'].values; A['method']=ti.loc[A.qid,'method'].values
    A['fact']=A.line.str.strip().str.lower()+'|'+A.value.round(6).astype(str)
    byv={v:g for v,g in A.groupby('video_id')}
    def clipK(v, ex):
        g=byv.get(v)
        if g is None: return 0.0
        g=g[~g.fact.isin(ex)&g.kind.isin(('size','speed'))]
        return float(np.median(np.r_[g.lk.values,0.0])) if len(g) else 0.0
    def corr(p, ex, useK):
        rp=ti.loc[p]; val=rp.v3
        if useK and rp.method=='direct' and rp.tkind in ('size','speed'): val=val*np.exp(clipK(rp.video_id,ex))
        return val
    def pred(q, ex, useK, pool):
        if not pool: return corr(q,ex,useK)
        per=per_base_values(ti,eq,q,include_self=True)
        if len(per)<minb: return corr(q,ex,useK)
        return gmed([corr(x[2],ex,useK) for x in per.values()])
    rows=[]
    for fact,g in A.groupby('fact'):
        ex={fact}
        for r in g.itertuples():
            if r.method!='direct' or r.cat not in cats: continue
            if only is not None and r.qid not in only: continue
            rows.append(dict(cat=r.cat,qid=r.qid,kind=r.kind,V=r.value,v3=r.v3,
                m_raw=mra(r.v3,r.value), m_K=mra(pred(r.qid,ex,True,False),r.value),
                m_P=mra(pred(r.qid,ex,False,True),r.value), m_KP=mra(pred(r.qid,ex,True,True),r.value)))
    R=pd.DataFrame(rows)
    print(label, 'minb',minb,'n',len(R), R[['m_raw','m_K','m_P','m_KP']].mean().round(3).to_dict())
    return R
if __name__=='__main__':
    t_old=pd.read_pickle(W+'/TS.pkl'); A_old=pd.read_pickle(W+'/transfers3.pkl'); eq_old=pickle.load(open(W+'/eq3.pkl','rb'))
    t_ext=pd.read_pickle(EXT+'/work/TS_ext.pkl'); A_ext=pd.read_pickle(EXT+'/work/transfers_ext.pkl'); eq_ext=pickle.load(open(EXT+'/work/eq_ext.pkl','rb'))
    newq=set(A_ext.qid)-set(A_old.qid)
    for mb in (3,2):
        run(t_old,A_old,eq_old,mb,label='OLD fam, old facts')
        Rx=run(t_ext,A_ext,eq_ext,mb,label='EXT fam, all facts')
        run(t_ext,A_ext,eq_ext,mb,only=newq,label='EXT fam, NEW facts')
        run(t_ext,A_ext,eq_ext,mb,only=set(A_old.qid),label='EXT fam, old facts')
        run(t_ext,A_ext,eq_ext,mb,cats=('S3',),label='S3 EXT fam, all facts')
    R=run(t_ext,A_ext,eq_ext,3,only=newq,label='detail')
    print(R.to_string())
