import sys; sys.path.insert(0,'/home/user/quantiphy-challenge')
import numpy as np, pandas as pd
from qp.mra import item_scores
m=pd.read_pickle('/home/user/quantiphy-challenge/research/r86/loss_audit/master.pkl')
m['raw']=m.r_parsed_value.where(~((m.category.isin(['S3','D3']))&(m.srcg=='sim')),m.dmed)
# labelled pool: val rows (combo3 vs val) + fact rows (raw vs fact)
A=m[m.val.notna()][['category','srcg','kg','combo3','val']].rename(columns={'combo3':'p','val':'g'}); A['src']='val'
B=m[m.fact.notna()][['category','srcg','kg','raw','fact']].rename(columns={'raw':'p','fact':'g'}); B['src']='fact'
L=pd.concat([A,B]); L=L[(L.p>0)&(L.g>0)]
cs=np.exp(np.linspace(-0.3,0.3,61))
rows=[]
for (c,s,k),d in L.groupby(['category','srcg','kg']):
    if len(d)<8: continue
    base=item_scores(d.p.values,d.g.values).mean()
    sc=[item_scores(d.p.values*x,d.g.values).mean() for x in cs]
    i=int(np.argmax(sc))
    # leave-one-out estimate of c*
    loo=[]
    for j in range(len(d)):
        dd=d.drop(d.index[j]) if False else d.iloc[[t for t in range(len(d)) if t!=j]]
        sc2=[item_scores(dd.p.values*x,dd.g.values).mean() for x in cs]
        xj=cs[int(np.argmax(sc2))]
        loo.append(item_scores([d.p.values[j]*xj],[d.g.values[j]])[0]-item_scores([d.p.values[j]],[d.g.values[j]])[0])
    rows.append(dict(cell=f'{c}:{s}:{k}',n=len(d),base=round(base,3),cstar=round(cs[i],3),insample_gain=round(sc[i]-base,3),loo_gain=round(np.mean(loo),3),medlr=round(np.median(np.log(d.p/d.g)),3)))
print(pd.DataFrame(rows).to_string())
