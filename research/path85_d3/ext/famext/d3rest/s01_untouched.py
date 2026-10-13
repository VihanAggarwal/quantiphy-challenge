import sys, re, json, numpy as np, pandas as pd
R='/home/user/quantiphy-challenge'; sys.path.insert(0,R)
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
from qp.data import load_split
t=load_split('test').set_index('qid')
v3=pd.read_csv(R+'/submissions/trackA_v3_best_per_category.csv').set_index('id')
p5=pd.read_csv(R+'/submissions/trackA_probe5_families_merged.csv').set_index('id').parsed_value
run=pd.read_csv(R+'/runs/test_v1_high_854/test.csv').set_index('id')
print(run.columns.tolist())
D3=t[t.category=='D3'].copy()
D3['v3']=v3.parsed_value.reindex(D3.index); D3['p5']=p5.reindex(D3.index)
D3['changed']=~np.isclose(D3.v3,D3.p5,rtol=1e-9)
print(D3.changed.sum(), len(D3))
dec=pd.read_csv(SP+'/merge/D3/decisions.csv').set_index('qid')
D3['src']=dec.chosen_source.reindex(D3.index).fillna('v3')
D3['kind']=dec.kind.reindex(D3.index)
fam=json.load(open(SP+'/big/scenegraph/families.json'))
print(type(fam), (list(fam.keys())[:5] if isinstance(fam,dict) else fam[:2]))
D3.to_pickle(SP+'/ext/d3rest/D3.pkl')
u=D3[~D3.changed]
print(u.video_source.value_counts())
print(D3.groupby('video_source').changed.agg(['sum','count']))
