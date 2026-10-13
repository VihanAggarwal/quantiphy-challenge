"""LOFO: clip-K split by whether the remaining facts are about the same object as the held-out question."""
import sys, os, pickle
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
A['fact']=A.line.str.strip().str.lower()+'|'+A.value.round(6).astype(str)
A=A[A.kind.isin(('size','speed'))]
def same(a,b): return max(name_score(x,y) for x in a.split('|') for y in b.split('|'))>=0.6
rows=[]
for r in A.itertuples():
    if r.method!='direct': continue
    g=A[(A.video_id==r.video_id)&(A.fact!=r.fact)]
    if not len(g): continue
    so=g[[same(o,r.obj) for o in g.obj]]; oo=g[[not same(o,r.obj) for o in g.obj]]
    def K(gg,shrink=True): return float(np.median(np.r_[gg.lk.values,0.0] if shrink else gg.lk.values)) if len(gg) else 0.0
    rows.append(dict(qid=r.qid,cat=r.cat,v=r.video_id,obj=r.obj,kind=r.kind,lk=r.lk,nsame=len(so),nother=len(oo),
        raw=mra(r.v3,r.value),K_all=mra(r.v3*np.exp(K(g)),r.value),K_same=mra(r.v3*np.exp(K(so)),r.value) if len(so) else np.nan,
        K_other=mra(r.v3*np.exp(K(oo)),r.value) if len(oo) else np.nan,
        K_same_ns=mra(r.v3*np.exp(K(so,False)),r.value) if len(so) else np.nan,
        K_other_ns=mra(r.v3*np.exp(K(oo,False)),r.value) if len(oo) else np.nan,
        K_all_ns=mra(r.v3*np.exp(K(g,False)),r.value)))
R=pd.DataFrame(rows)
pd.set_option('display.width',250)
for cat in ('D3','S3'):
    X=R[R.cat==cat]
    print(cat,'n',len(X))
    print(' all rows:',X[['raw','K_all','K_all_ns']].mean().round(3).to_dict())
    xs=X[X.nsame>0]; print(' rows with same-object facts n=%d'%len(xs), xs[['raw','K_all','K_same','K_same_ns']].mean().round(3).to_dict())
    xo=X[X.nother>0]; print(' rows with other-object facts n=%d'%len(xo), xo[['raw','K_all','K_other','K_other_ns']].mean().round(3).to_dict())
    xb=X[(X.nother>0)&(X.nsame>0)]; print(' rows with both n=%d'%len(xb), xb[['raw','K_same','K_other','K_all']].mean().round(3).to_dict())
    print(' by number of video', X.v.nunique())
R.to_pickle(EXT+'/work/kobj.pkl')
