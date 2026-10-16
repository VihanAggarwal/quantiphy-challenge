import sys; sys.path.insert(0,'.')
import numpy as np, pandas as pd
from qp.mra import item_scores
pd.set_option('display.width',250)
f=pd.read_pickle('research/next/nlres/fact.pkl')
def sc(p,g): return np.nan_to_num(item_scores(np.asarray(p,float),np.asarray(g,float)))
for c in ['agent','c1','best','sol','raw','combo3','dmed']:
    f['s_'+c]=np.where(f[c].notna(), sc(f[c].fillna(-1),f['gt']), np.nan)
f['lr']=np.log(f.agent/f['gt'])
nl=f[(f.ctype!='lab')&f.agent.notna()]
print(len(nl), nl.scored.sum())
agg=dict(n=('fact','size'),agent=('s_agent','mean'),best=('s_best','mean'),c1=('s_c1','mean'),raw=('s_raw','mean'),dmed=('s_dmed','mean'),sol=('s_sol','mean'),medlr=('lr','median'),mad=('lr',lambda x: x.abs().median()))
print(nl.groupby(['ctype']).agg(**agg).round(3))
print(nl.groupby(['ctype','qkind']).agg(**agg).round(3))
print(nl.groupby(['ctype','category']).agg(**agg).round(3))
w=nl.sort_values('s_agent')[['video_id','video_type','category','qkind','question','prior','fact','agent','raw','dmed','sol','s_agent','s_raw']]
w['question']=w.question.str[:70]; w['prior']=w.prior.str[:45]
print(w[w.s_agent<0.9].to_string())
print((nl.best==nl.fact).sum(), 'best == fact')
