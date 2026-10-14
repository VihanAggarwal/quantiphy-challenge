import sys; sys.path.insert(0,'/home/user/quantiphy-challenge')
import numpy as np, pandas as pd
from qp.mra import item_scores
m=pd.read_pickle('/home/user/quantiphy-challenge/research/r86/loss_audit/master.pkl')
m['raw']=m.r_parsed_value.where(~((m.category.isin(['S3','D3']))&(m.srcg=='sim')),m.dmed)
A=m[m.val.notna()][['category','srcg','combo3','val']].rename(columns={'combo3':'p','val':'g'})
B=m[m.fact.notna()][['category','srcg','raw','fact']].rename(columns={'raw':'p','fact':'g'})
rng=np.random.default_rng(0)
for nm,L in [('val(combo3)',A),('facts(raw)',B)]:
    L=L[(L.p>0)&(L.g>0)]
    e1=np.log(L.p/L.g).values; g=L.g.values
    base=item_scores(L.p.values,g).mean()
    print(nm,'n',len(L),'base %.3f'%base)
    out=[]
    for s in [0.7,0.85,1.0,1.2]:
        row=[]
        for rho in [0.0,0.3,0.5,0.7,0.85]:
            gains=[];m2=[]
            for rep in range(200):
                ind=rng.permutation(e1)
                e2=s*(rho*e1+np.sqrt(1-rho**2)*ind)
                m2.append(item_scores(g*np.exp(e2),g).mean())
                eb=0.5*e1+0.5*e2
                gains.append(item_scores(g*np.exp(eb),g).mean()-base)
            row.append(f'rho{rho}: new{np.mean(m2):.3f} blend{np.mean(gains):+.3f}')
        print(' s',s,' | '.join(row))
