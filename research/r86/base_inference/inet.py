import sys, re, numpy as np, pandas as pd
sys.path.insert(0,'/home/user/quantiphy-challenge')
from qp.mra import item_scores
v=pd.read_pickle('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/valruns.pkl')
v['src']=v.video_source.replace({'segmentation':'simulation'})
v['d2']=v.category.str[1]=='2'
rng=np.random.default_rng(0)
def boot(sub,a,b,n=2000):
    vids=sub.video_id.unique(); diffs=[]
    da=pd.Series(item_scores(sub[a],sub.answer),index=sub.index); db=pd.Series(item_scores(sub[b],sub.answer),index=sub.index)
    g=(db-da).groupby(sub.video_id).agg(['sum','count'])
    for _ in range(n):
        s=g.loc[rng.choice(vids,len(vids))]; diffs.append(s['sum'].sum()/s['count'].sum())
    return np.mean(db-da), np.percentile(diffs,[5,95])
for nm,mask in [('2D internet',v.d2&(v.src=='internet')),('2D sim',v.d2&(v.src=='simulation')),('lab',v.src=='lab')]:
    sub=v[mask]
    print('==',nm,len(sub),'clips',sub.video_id.nunique())
    print({c:round(np.nanmean(item_scores(sub[c],sub.answer)),3) for c in ['o854_d','om_d','om2_d','hr1_d','hr2_d','hr2m_d','v2v_d','o854_g','hr1_g','hr2_g']})
    for a,b in [('o854_d','hr1_d'),('o854_d','hr2_d'),('o854_d','v2v_d'),('o854_g','hr1_g')]:
        m,ci=boot(sub,a,b); print('  ',a,'->',b,'%.3f'%m, ci.round(3))
lab=v[v.src=='lab'].copy()
lab['gm12']=np.sqrt(lab.o854_d*lab.v2v_d); lab['gm12h']=np.sqrt(lab.o854_d*lab.hr2_d)
print('lab gm v1854*v2v',round(np.nanmean(item_scores(lab.gm12,lab.answer)),3),'gm v1854*hr2',round(np.nanmean(item_scores(lab.gm12h,lab.answer)),3))
