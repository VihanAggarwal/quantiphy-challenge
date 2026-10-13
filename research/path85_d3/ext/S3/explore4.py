import sys, pickle
sys.path.insert(0,'/home/user/quantiphy-challenge')
import pandas as pd, numpy as np
from qp.parse import canonical_unit, _UNITS
R='/home/user/quantiphy-challenge'; SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
S=pickle.load(open(SP+'/merge/S3/sg_state.pkl','rb'))
t=S['t']; ti=t.set_index('qid'); G=S['groups']
v3=pd.read_csv(R+'/submissions/trackA_v3_best_per_category.csv').set_index('id').parsed_value
p4=pd.read_csv(R+'/submissions/trackA_probe4_s2twin_d2refineoff_s3split_d3fixes.csv').set_index('id').parsed_value
p4s3=pd.read_csv(SP+'/hyp/final/S3_split_full_depthfix.csv').set_index('id').parsed_value
tl=pd.read_csv(SP+'/big/scene_graph/S3_T_LABfix.csv').set_index('id').parsed_value
run=pd.read_csv(R+'/runs/test_v1_high_854/test.csv').set_index('id')
# check p4 S3 rows == p4s3 S3 rows
s3=ti.index[ti.category=='S3']
print('P4 file S3 == S3_split_full_depthfix:', np.allclose(p4[s3],p4s3[s3]))
d3=ti.index[ti.category=='D3']
print('P4 D3 vs v3 changed:', (~np.isclose(p4[d3],v3[d3])).sum())
def usc(q):
    cu=canonical_unit(ti.loc[q,'target_unit'] or 'm') or 'm'
    return _UNITS[cu][0] if cu in _UNITS else 1.0
for k,qs in G.items():
    g=ti.loc[qs]
    objs=sorted({x.lower().strip() for o in g.tobj for x in str(o).split('|')})
    print('=== GROUP',objs,g.tdim.iloc[0],'n',len(qs),'bases',sorted(set(g.base)))
    for q in sorted(qs,key=lambda q:(ti.loc[q,'base'],ti.loc[q,'video_id'])):
        u=usc(q)*100
        print(f"  {q} {ti.loc[q,'video_id']:16s} {ti.loc[q,'category']} {ti.loc[q,'tunit']!s:4s} v3={v3[q]*u:8.2f} P4={p4[q]*u:8.2f} TL={tl[q]*u:8.2f} geo={run.loc[q,'geo_value']*u:9.2f} dir={run.loc[q,'direct_value']*u:7.2f} {run.loc[q,'method'][:22]:22s} | {ti.loc[q,'question'][:60]} | {str(ti.loc[q,'prior'])[:40]}")
