import sys; sys.path.insert(0,'.')
import numpy as np, pandas as pd
from qp.mra import item_scores
pd.set_option('display.width',250)
v=pd.read_pickle('research/next/nlres/val.pkl')
def sc(p,g): return np.nan_to_num(item_scores(np.asarray(p,float),np.asarray(g,float)))
for c in ['agent','agent2','combo3','dmed','sol','pipe']:
    v['s_'+c]=np.where(v[c].notna(), sc(v[c].fillna(-1),v['gt']), np.nan)
v['lr']=np.log(v.agent/v['gt'])
nl=v[v.ctype!='lab']
print(nl.groupby(['ctype']).agg(n=('answer','size'),agent=('s_agent','mean'),c3=('s_combo3','mean'),nc3=('combo3','count'),dmed=('s_dmed','mean'),sol=('s_sol','mean'),medlr=('lr','median'),mad=('lr',lambda x: x.abs().median())).round(3))
print(nl.groupby(['ctype','kind']).agg(n=('answer','size'),agent=('s_agent','mean'),c3=('s_combo3','mean'),dmed=('s_dmed','mean'),sol=('s_sol','mean'),medlr=('lr','median'),mad=('lr',lambda x: x.abs().median())).round(3))
print(nl.groupby(['ctype','category']).agg(n=('answer','size'),agent=('s_agent','mean'),c3=('s_combo3','mean'),dmed=('s_dmed','mean'),sol=('s_sol','mean'),medlr=('lr','median')).round(3))
print(nl.groupby(['kind']).agg(n=('answer','size'),agent=('s_agent','mean'),c3=('s_combo3','mean'),dmed=('s_dmed','mean'),sol=('s_sol','mean'),medlr=('lr','median'),mad=('lr',lambda x: x.abs().median())).round(3))
print()
w=nl.sort_values('s_agent')[['video_id','video_type','category','kind','question','prior','gt','agent','agent2','combo3','dmed','sol','s_agent','s_combo3']]
w['question']=w.question.str[:80]; w['prior']=w.prior.str[:50]
print(w[w.s_agent<0.8].to_string())
