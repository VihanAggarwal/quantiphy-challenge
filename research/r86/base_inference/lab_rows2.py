import sys, re, pandas as pd, numpy as np
sys.path.insert(0,'/home/user/quantiphy-challenge')
from qp.data import load_validation
from qp.mra import item_scores
v = load_validation().set_index('qid')
def kind(q):
    q=q.lower()
    if 'acceleration' in q: return 'acc'
    if re.search(r'veloc|speed',q): return 'speed'
    if re.search(r'displacement|travel|distance',q): return 'dist'
    return 'size'
v['kind']=v.question.map(kind)
t=pd.read_pickle('research/r86/loss_audit/master.pkl')
t2=t[t.val.notna()].copy()
t2['key']=t2.video_id+'|'+t2.question.str.strip()
v['key']=v.video_id+'|'+v.question.str.strip()
m=t2.reset_index().set_index('key')
v['combo3']=m.combo3.reindex(v.key).values
v['test_qid']=m['qid'].reindex(v.key).values if 'qid' in m else m['index'].reindex(v.key).values
runs = {'o854':'runs/val_opus_high/val.csv','om':'runs/val_opus_med/val.csv','om2':'runs/val_opus_med2/val.csv',
        'v2v':'runs/val_v2_high/val.csv','hr1':'runs/val_hr_v1_high/val_hires.csv','hr2':'runs/val_hr_v2_high/val_hires.csv','hr2m':'runs/val_hr_v2_med/val_hires.csv'}
for nm,p in runs.items():
    d=pd.read_csv(p).set_index('id')
    v[nm+'_d']=d.direct_value.reindex(v.index); v[nm+'_g']=d.geo_value.reindex(v.index); v[nm+'_p']=d.parsed_value.reindex(v.index)
v.to_pickle('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/valruns.pkl')
v['grp']=np.where(v.category.str[1]=='2','2D',np.where(v.video_source=='lab','lab','3Dsim'))
print('combo3 available', v.combo3.notna().sum())
res=[]
for (g,k),sub in v.groupby(['grp','kind']):
    r={'grp':g,'kind':k,'n':len(sub),'combo3':np.nanmean(item_scores(sub.combo3,sub.answer))}
    for nm in runs:
        for c in ('_d','_g'):
            r[nm+c]=np.nanmean(item_scores(sub[nm+c],sub.answer))
    res.append(r)
pd.set_option('display.width',300)
print(pd.DataFrame(res).round(3).to_string())
