import sys, re, numpy as np, pandas as pd
sys.path.insert(0,'/home/user/quantiphy-challenge')
from qp.mra import item_scores
v=pd.read_pickle('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/valruns.pkl')
def kind(q):
    q=q.lower()
    if 'acceleration' in q: return 'acc'
    if re.search(r'veloc|speed',q): return 'speed'
    if re.search(r'displacement|travel|distance',q): return 'dist'
    return 'size'
v['kind']=v.question.map(kind); v['motion']=v.kind.isin(['speed','acc'])
v['src']=v.video_source.replace({'segmentation':'simulation'})
s2=v[v.category=='S2'].copy()
print(pd.crosstab(s2.src,s2.motion))
def rule(sub,run):
    g=sub[run+'_g'].where(sub[run+'_g']>0); d=sub[run+'_d']
    gm=np.sqrt(g*d).fillna(d)
    out=np.where(sub.src=='internet', d, np.where(sub.motion, gm, g.fillna(d)))
    return pd.Series(out,index=sub.index)
rng=np.random.default_rng(1)
for run in ['o854','om','om2','hr1','hr2','hr2m']:
    p=rule(s2,run); s=pd.Series(item_scores(p,s2.answer),index=s2.index)
    print(run,'S2 rule %.3f'%s.mean(), 'internet %.3f'%s[s2.src=='internet'].mean(),'sim motion %.3f'%s[(s2.src!='internet')&s2.motion].mean(),'sim static %.3f'%s[(s2.src!='internet')&~s2.motion].mean())
    s2[run+'_rule']=s
# bootstrap hr1 vs o854
for a,b in [('o854','hr1'),('o854','hr2'),('om','hr1')]:
    dd=(s2[b+'_rule']-s2[a+'_rule']).groupby(s2.video_id).agg(['sum','count']); vids=dd.index.values
    bs=[dd.loc[rng.choice(vids,len(vids))].pipe(lambda x:x['sum'].sum()/x['count'].sum()) for _ in range(2000)]
    print(a,'->',b,'%.3f'%(dd['sum'].sum()/dd['count'].sum()),np.percentile(bs,[5,95]).round(3),'clips',len(vids))
