import sys, re, numpy as np, pandas as pd
sys.path.insert(0,'/home/user/quantiphy-challenge')
from qp.mra import item_scores
v=pd.read_pickle('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/valruns.pkl')
t=pd.read_pickle('research/r86/loss_audit/master.pkl')
t['key']=t.video_id+'|'+t.question.str.strip()
m=t.drop_duplicates('key').reset_index().set_index('key')
for c in ['combo3','prov','r_direct_value','r_parsed_value','kind','category']:
    v['t_'+c]=m[c].reindex(v.key).values
lab=v[(v.video_source=='lab')&v.t_combo3.notna()].copy()
# factor applied by pipeline over raw direct (test run = o854-like on hires? test run is v1 854 on test videos)
lab['fac']=lab.t_combo3/lab.t_r_direct_value
pd.set_option('display.width',250)
print(lab[['video_id','t_kind','answer','t_combo3','t_r_direct_value','t_r_parsed_value','t_prov','o854_d','v2v_d','hr2_d','fac']].round(3).to_string())
mot=lab.t_kind.isin(['speed','acc','path','avgspeed'])
for nm,sub in [('motion',lab[mot]),('dist',lab[lab.t_kind=='dist']),('size',lab[lab.t_kind=='size'])]:
    r={'n':len(sub),'combo3':np.mean(item_scores(sub.t_combo3,sub.answer))}
    for c in ['v2v_d','hr2_d','o854_d']:
        r[c+'*fac']=np.mean(item_scores(sub[c]*sub.fac,sub.answer))
        r[c]=np.mean(item_scores(sub[c],sub.answer))
    print(nm,{k:round(x,3) for k,x in r.items()})
