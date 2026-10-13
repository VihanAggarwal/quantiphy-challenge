"""Single-fact K: for clips with >=2 stated facts, use ONE fact as the K source and score another held-out fact.
Pairs split by same object vs other object; K = full log-ratio, half (= median with 0, what K does for one fact), or none."""
import sys
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
W=SP+'/big/scenegraph/work'; EXT=SP+'/ext/d3rest'
sys.path.insert(0,'/home/user/quantiphy-challenge'); sys.path.insert(0,W)
import numpy as np, pandas as pd
from qp.mra import item_scores
from qp.geometry import name_score
def mra(p,g): return float(item_scores([p],[g])[0])
t=pd.read_pickle(EXT+'/work/TS_ext.pkl'); ti=t.set_index('qid')
A=pd.read_pickle(EXT+'/work/transfers_ext.pkl'); A=A[~A.conflict].copy()
A['lk']=np.log(A.value/A.v3); A['kind']=ti.loc[A.qid,'tkind'].values; A['method']=ti.loc[A.qid,'method'].values
A['obj']=ti.loc[A.qid,'tobj'].values
A=A[A.kind.isin(('size','speed'))&(A.method=='direct')]
def same(a,b): return max(name_score(x,y) for x in a.split('|') for y in b.split('|'))>=0.6
rows=[]
for v,g in A.groupby('video_id'):
    if len(g)<2: continue
    for s in g.itertuples():
        for r in g.itertuples():
            if s.qid==r.qid or s.line==r.line: continue
            rows.append(dict(v=v,cat=r.cat,same=same(s.obj,r.obj),skind=s.kind,rkind=r.kind,raw=mra(r.v3,r.value),
                full=mra(r.v3*np.exp(s.lk),r.value),half=mra(r.v3*np.exp(s.lk/2),r.value),slk=abs(s.lk)))
R=pd.DataFrame(rows)
pd.set_option('display.width',200)
for cat in ('D3','S3'):
    X=R[R.cat==cat]
    print(cat, 'pairs',len(X),'clips',X.v.nunique())
    print(X.groupby('same')[['raw','half','full']].agg(['mean','size']).round(3))
    print(X.groupby(['skind','rkind'])[['raw','half','full']].mean().round(3))
    # weight per clip equally
    print(' clip-weighted', X.groupby(['same','v'])[['raw','half','full']].mean().groupby('same').mean().round(3).to_dict('index'))
    print(' by |source lk| > log1.3', X.groupby(X.slk>np.log(1.3))[['raw','half','full']].agg(['mean','size']).round(3))
if __name__=='__main__':
    rows=[]
    for v,g in A.groupby('video_id'):
        for s in g.itertuples():
            for r in g.itertuples():
                if s.qid==r.qid or s.line==r.line or not same(s.obj,r.obj): continue
                rows.append(dict(v=v,cat=r.cat,src=ti.loc[s.qid,'question'][:45],src_ratio=np.exp(s.lk),tgt=ti.loc[r.qid,'question'][:45],tgt_ratio=np.exp(r.lk),raw=mra(r.v3,r.value),full=mra(r.v3*np.exp(s.lk),r.value)))
    print(pd.DataFrame(rows).to_string())
