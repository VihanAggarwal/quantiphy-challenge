import sys; sys.path.insert(0,'.')
import numpy as np, pandas as pd
from qp.mra import item_scores
pd.set_option('display.width',250)
v=pd.read_pickle('research/next/nlres/val.pkl')
def sc(p,g): return np.nan_to_num(item_scores(np.asarray(p,float),np.asarray(g,float)))
for c in ['agent','agent2','combo3','dmed','sol','pipe']:
    v['s_'+c]=np.where(v[c].notna(), sc(v[c].fillna(-1),v['gt']), np.nan)
nl=v[(v.ctype!='lab')]
d=nl[(nl.s_combo3.notna())&(nl.s_combo3!=nl.s_agent)].copy()
d['diff']=d.s_agent-d.s_combo3
w=d.sort_values('diff')[['video_id','ctype','category','kind','question','gt','agent','agent2','combo3','dmed','sol','s_agent','s_combo3','diff']]
w['question']=w.question.str[:60]
print(w.to_string())
print(d.groupby('video_id')['diff'].agg(['sum','count']))
