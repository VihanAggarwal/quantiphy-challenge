import sys, numpy as np, pandas as pd
sys.path.insert(0,'/home/user/quantiphy-challenge')
from qp.mra import item_scores
t=pd.read_pickle('research/r86/loss_audit/master.pkl')
o=pd.read_pickle('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/objsize.pkl')
t=t.join(o[['prior_px','target_px']])
t['minpx']=t[['prior_px','target_px']].min(axis=1)
t['key']=t.video_id+'|'+t.question.str.strip()
v=pd.read_pickle('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/valruns.pkl')
m=t.drop_duplicates('key').set_index('key')
v['minpx']=m.minpx.reindex(v.key).values
v['grp']=np.where(v.category.str[1]=='2','2D',np.where(v.video_source=='lab','lab','3Dsim'))
v['small']=v.minpx<40
for g in ['2D','3Dsim','lab']:
    for s in [True,False]:
        sub=v[(v.grp==g)&(v.small==s)]
        r={nm:np.nanmean(item_scores(sub[nm+'_d'],sub.answer)) for nm in ['o854','om','om2','hr1','hr2','hr2m']}
        rg={nm+'g':np.nanmean(item_scores(sub[nm+'_g'],sub.answer)) for nm in ['o854','hr1','hr2']}
        print(g,'small' if s else 'big', len(sub), {k:round(x,3) for k,x in {**r,**rg}.items()})
