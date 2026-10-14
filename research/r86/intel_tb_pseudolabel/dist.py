import runpy, sys, io, contextlib, warnings, numpy as np, pandas as pd, re
warnings.filterwarnings('ignore'); sys.argv=['x']
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/pl/pseudo_tb.py')
test, val, fit, T, V, mra, lmed, mat, apply_sets, V3 = (g[k] for k in ['test','val','fit','T','V','mra','lmed','mat','apply_sets','V3'])
sub = pd.read_csv('/home/user/quantiphy-challenge/submissions/trackB_v3_catmedian_famrules.csv').set_index('id')['parsed_value']
isdist = lambda q: bool(re.search(r'distance|how far|away from the camera|from the camera', str(q), re.I))
for nm, d in [('test-fit', fit), ('val', val)]:
    d = d.copy(); d['dist'] = d['question'].map(isdist); d['cam'] = d['question'].str.contains('camera', case=False)
    print(nm, d.groupby(['category','dist']).size().unstack(fill_value=0).to_string())
    print(nm, 'camera-distance rows by cat:', d[d['cam'] & d['dist']].groupby('category').size().to_dict())
f = fit.copy(); f['dist'] = f['question'].map(isdist); f['tb'] = f['qid'].map(sub).astype(float)
for c in ['S3','D3']:
    for dd in [True, False]:
        m = (f['category']==c)&(f['dist']==dd)
        print(c, 'dist' if dd else 'other', int(m.sum()), 'TrackB v3 pseudo-MRA vs TrackA', round(mra(f.loc[m,'tb'].values, f.loc[m,'pl'].values).mean(),3))
v = val.copy(); v['dist']=v['question'].map(isdist)
pa = apply_sets(v, V, V3); s = mra(pa, v['answer'].values)
print('val TrackB v3-sets raw item mean, dist rows by cat:', pd.Series(s[v['dist'].values]).groupby(v.loc[v['dist'],'category'].values).agg(['mean','size']).round(3).to_dict())
