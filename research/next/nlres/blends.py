"""Blends of the agent with other sources on validation (non-lab) and held-out stated facts (non-lab).
Item means by clip type; rows where all blend members exist."""
import sys; sys.path.insert(0,'.')
import numpy as np, pandas as pd
from qp.mra import item_scores
pd.set_option('display.width',250)
def sc(p,g): return np.nan_to_num(item_scores(np.asarray(p,float),np.asarray(g,float)))
def run(d, base, label):
    d=d.copy()
    L={k:np.log(d[k]) for k in ['agent',base,'sol','dmed']}
    C={'agent':L['agent'], base:L[base], 'gm(a,%s)'%base:(L['agent']+L[base])/2, 'a.75/%s.25'%base:.75*L['agent']+.25*L[base],
       'gm(a,sol)':(L['agent']+L['sol'])/2, 'a.75/sol.25':.75*L['agent']+.25*L['sol'], 'gm(a,dmed)':(L['agent']+L['dmed'])/2,
       'med(a,%s,sol)'%base:pd.concat([L['agent'],L[base],L['sol']],axis=1).median(axis=1)}
    m=pd.concat(L.values(),axis=1).notna().all(axis=1)
    S=pd.DataFrame({k:sc(np.exp(x[m]),d.loc[m,'gt']) for k,x in C.items()},index=d.index[m])
    S['ctype']=d.loc[m,'ctype']
    print(f'--- {label}: {int(m.sum())} rows'); print(S.groupby('ctype').mean().round(3).T.to_string()); print('all', S.drop(columns='ctype').mean().round(3).to_dict())
v=pd.read_pickle('research/next/nlres/val_conf.pkl'); v=v[v.ctype!='lab']
run(v,'combo3','VALIDATION non-lab')
f=pd.read_pickle('research/next/nlres/fact_conf.pkl'); f=f[(f.ctype!='lab')&f.agent.notna()]
f['gt']=f.fact
run(f,'raw','FACTS non-lab')
