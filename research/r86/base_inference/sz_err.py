import sys, numpy as np, pandas as pd
sys.path.insert(0,'/home/user/quantiphy-challenge')
from qp.mra import item_scores
t=pd.read_pickle('research/r86/loss_audit/master.pkl')
o=pd.read_pickle('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/objsize.pkl')
t=t.join(o[['prior_px','target_px','W_sent','conf']])
t['minpx']=t[['prior_px','target_px']].min(axis=1)
t['grp']=np.where(t.category.str[1]=='2','2D',np.where(t.srcg=='lab','lab','3Dsim'))
# labelled evaluation: fact rows scored on raw (non-family) answer; val rows scored on raw parsed
t['raw']=np.where((t.grp=='3Dsim')&t.dmed.notna(), t.dmed, t.r_parsed_value)
lab=pd.concat([t[t.fact.notna()].assign(gtv=lambda x:x.fact, src='fact'), t[t.val.notna()].assign(gtv=lambda x:x.val, src='val')])
lab['sc']=item_scores(lab.raw, lab.gtv)
lab['ale']=np.abs(np.log(lab.raw/lab.gtv))
bins=[0,15,30,60,120,2000]
lab['pb']=pd.cut(lab.minpx,bins)
print(lab.groupby(['grp','pb']).agg(n=('sc','size'),sc=('sc','mean'),med_ale=('ale','median')).round(3).to_string())
# distribution over test scored rows
t['pb']=pd.cut(t.minpx,bins)
print(pd.crosstab(t[t.scored].grp, t[t.scored].pb))
print(pd.crosstab(t[t.scored].category, t[t.scored].pb))
print('---- 3D sim fact rows by target px (sent pixels) and prior px')
f=lab[(lab.grp=='3Dsim')&(lab.src=='fact')].copy()
f['tb']=pd.cut(f.target_px,[0,20,40,80,2000]); f['pb2']=pd.cut(f.prior_px,[0,20,40,80,2000])
print(f.groupby('tb').agg(n=('sc','size'),sc=('sc','mean'),ale=('ale','median')).round(3))
print(f.groupby('pb2').agg(n=('sc','size'),sc=('sc','mean'),ale=('ale','median')).round(3))
print(f.groupby('kind').agg(n=('sc','size'),sc=('sc','mean'),ale=('ale','median')).round(3))
t3=t[(t.grp=='3Dsim')&t.scored]
print('test 3Dsim scored rows target_px<30:',(t3.target_px<30).sum(),' <20:',(t3.target_px<20).sum(), 'of',len(t3))
print(pd.crosstab(t3.category, pd.cut(t3.target_px,[0,20,40,80,2000])))
