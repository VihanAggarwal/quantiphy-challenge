import sys, numpy as np, pandas as pd
sys.path.insert(0,'/home/user/quantiphy-challenge')
from qp.claude_annotate import prior_si
from qp.parse import _UNITS, canonical_unit
t=pd.read_pickle('research/r86/loss_audit/master.pkl')
def si(v,u):
    cu=canonical_unit(u) if isinstance(u,str) and u else None
    if cu in _UNITS: return v*_UNITS[cu][0], _UNITS[cu][1]
    return np.nan, ''
out=[]
for q,r in t.iterrows():
    p=prior_si(r.prior)
    a,dim=si(r.combo3, r.target_unit)
    if p is None or not np.isfinite(a): continue
    out.append(dict(qid=q,vid=r.video_id,cat=r.category,unit=r.target_unit,ans=r.combo3,ans_si=a,dim=dim,prior=r.prior,p_si=p[0],p_dim=p[1],ratio=a/p[0] if p[0] else np.nan,q=r.question[:70]))
U=pd.DataFrame(out)
same=U[U.dim==U.p_dim]
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',70)
print(len(U), 'empty unit rows:', (t.target_unit.fillna('')=='').sum())
print(same[(same.ratio>30)|(same.ratio<1/30)].sort_values('ratio').to_string())
