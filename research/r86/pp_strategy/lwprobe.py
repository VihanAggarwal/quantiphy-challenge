import sys,re; sys.path.insert(0,'/home/user/quantiphy-challenge')
import numpy as np, pandas as pd
from qp.mra import item_scores
m=pd.read_pickle('/home/user/quantiphy-challenge/research/r86/loss_audit/master.pkl')
m['raw']=m.r_parsed_value.where(~((m.category.isin(['S3','D3']))&(m.srcg=='sim')),m.dmed)
q=m.question.str.lower()
m['dim']=np.where(q.str.contains(r'\b(length|width|wingspan|long|wide)\b'),'LW',np.where(q.str.contains(r'\b(height|tall|high)\b'),'H','other'))
s=m[(m.category.isin(['S3','D3']))&(m.srcg=='sim')&(m.kind=='size')]
print(pd.crosstab([s.category,s.dim],[s.fact.notna()]))
for nm,p,g in [('val',s.combo3,s.val),('fact_raw',s.raw,s.fact),('fact_K?',s.combo3,s.fact)]:
    for dim in ['LW','H']:
        k=g.notna()&(s.dim==dim)&(p>0)
        if k.sum()==0: continue
        base=item_scores(p[k],g[k]).mean()
        out=' '.join(f'x{c}:{item_scores(p[k]*c,g[k]).mean()-base:+.3f}' for c in [0.95,1.05,1.08,1.12])
        print(nm,dim,'n',k.sum(),'base %.3f'%base,'medlr %+.3f'%np.median(np.log(p[k]/g[k])),out)
# rows a probe would touch: non-fact, scored, LW, 3D sim size
for c in ['S3','D3']:
    k=(s.category==c)&(s.dim=='LW')&s.fact.isna()&s.scored
    print(c,'probe rows (LW, non-fact, scored)',k.sum())
