import sys; sys.path.insert(0,'.'); sys.path.insert(0,'research/next/nlres')
import numpy as np, pandas as pd
from pathlib import Path
from conf import confidence
from qp.mra import item_scores
pd.set_option('display.width',250)
def sc(p,g): return np.nan_to_num(item_scores(np.asarray(p,float),np.asarray(g,float)))
v=pd.read_pickle('research/next/nlres/val.pkl')
C={}
for vid in v.video_id.unique():
    for q,l in confidence(Path('/tmp/blind')/vid).items(): C[(vid,q)]=l
v['conf']=[C.get((a,q),np.nan) for a,q in zip(v.video_id,v.index)]
for c in ['agent','combo3','dmed','sol']:
    v['s_'+c]=np.where(v[c].notna(), sc(v[c].fillna(-1),v['gt']), np.nan)
v['gm']=np.exp((np.log(v.agent)+np.log(v.combo3))/2); v['s_gm']=np.where(v.gm.notna(), sc(v.gm.fillna(-1),v['gt']), np.nan)
v['cb']=pd.cut(v.conf,[-1,1.5,2.5,3.5,6],labels=['<=low','low-med','med','>=med-high'])
v['cb']=v.cb.cat.add_categories('none').fillna('none')
for name,sub in [('nonlab',v[v.ctype!='lab']),('lab',v[v.ctype=='lab'])]:
    print(name, 'coverage', sub.conf.notna().mean().round(2))
    print(sub.groupby('cb',observed=True).agg(n=('answer','size'),agent=('s_agent','mean'),c3=('s_combo3','mean'),nc3=('combo3','count'),gm=('s_gm','mean'),dmed=('s_dmed','mean'),sol=('s_sol','mean')).round(3))
    m=sub[sub.combo3.notna()]
    print(' matched to combo3:'); print(m.groupby('cb',observed=True).agg(n=('answer','size'),agent=('s_agent','mean'),c3=('s_combo3','mean'),gm=('s_gm','mean'),dmed=('s_dmed','mean'),sol=('s_sol','mean')).round(3))
v.to_pickle('research/next/nlres/val_conf.pkl')
f=pd.read_pickle('research/next/nlres/fact.pkl')
C={}
for vid in f.video_id.unique():
    src=vid[:-10] if vid.endswith('_segmented') and not (Path('/tmp/blind_test')/vid/'answers.json').exists() else vid
    for q,l in confidence(Path('/tmp/blind_test')/vid).items(): C[(vid,q)]=l
f['conf']=[C.get((a,q),np.nan) for a,q in zip(f.video_id,f.index)]
for c in ['agent','c1','dmed','sol','raw']:
    f['s_'+c]=np.where(f[c].notna(), sc(f[c].fillna(-1),f['gt']), np.nan)
f['gm']=np.exp((np.log(f.agent)+np.log(f.raw))/2); f['s_gm']=np.where(f.gm.notna(), sc(f.gm.fillna(-1),f['gt']), np.nan)
f['cb']=pd.cut(f.conf,[-1,1.5,2.5,3.5,6],labels=['<=low','low-med','med','>=med-high'])
f['cb']=f.cb.cat.add_categories('none').fillna('none')
nl=f[(f.ctype!='lab')&f.agent.notna()]
print('FACTS nonlab coverage', nl.conf.notna().mean().round(2))
print(nl.groupby('cb',observed=True).agg(n=('fact','size'),agent=('s_agent','mean'),raw=('s_raw','mean'),gm=('s_gm','mean'),dmed=('s_dmed','mean'),sol=('s_sol','mean')).round(3))
f.to_pickle('research/next/nlres/fact_conf.pkl')
