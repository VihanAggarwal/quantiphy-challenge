import pandas as pd, re, numpy as np
m=pd.read_pickle('research/r86/loss_audit/master.pkl')
def val(s):
    x=re.findall(r'=\s*([0-9]*\.?[0-9]+)',s)
    return float(x[0]) if x else np.nan
def roundtype(v):
    if not np.isfinite(v) or v<=0: return 'na'
    k=np.floor(np.log10(v)); man=v/10**k
    if abs(man-round(man))<1e-6: return '1sig'
    if abs(man*2-round(man*2))<1e-6: return 'half'
    if abs(man*10-round(man*10))<1e-6: return '2sig'
    return 'other'
p=m.drop_duplicates('video_id').copy()
p['pv']=p.prior.map(val)
p['pkind']=p.prior.str.lower().map(lambda s: 'acc' if 'acc' in s or 'gravity' in s else ('speed' if ('speed' in s or 'veloc' in s) else 'size'))
p['rt']=p.pv.map(roundtype)
for src in ['simulation','segmentation','internet','lab']:
    q=p[p.video_source==src]
    print(src); print(pd.crosstab(q.pkind,q.rt))
# validation labels and facts for sim rows
for col in ['val','fact']:
    q=m[m[col].notna() & m.video_source.isin(['simulation','segmentation'])].copy()
    q['rt']=q[col].map(roundtype)
    print(col); print(pd.crosstab(q.kind,q.rt))
