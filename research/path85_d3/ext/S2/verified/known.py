import sys, importlib.util, numpy as np, pandas as pd
sys.path.insert(0,'/home/user/quantiphy-challenge')
from qp.data import load_split
from qp.mra import item_scores
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
spec=importlib.util.spec_from_file_location('segtwin_rule', SP+'/hyp/S2/t2/segtwin.py')
seg=importlib.util.module_from_spec(spec); spec.loader.exec_module(seg)
tt=seg.t
v=load_split('val')
v['twin']=v.video_id.str.replace('_segmented','',regex=False)
v['nq']=v.question.map(seg.normq)
gt=v.set_index(['twin','nq'])
gt=gt[~gt.index.duplicated()]
d=pd.read_csv(SP+'/merge/S2/decisions.csv')
v3=pd.read_csv('/home/user/quantiphy-challenge/submissions/trackA_v3_best_per_category.csv').set_index('id').parsed_value
m=pd.read_csv(SP+'/merge/S2/S2_merged.csv').set_index('id').parsed_value
e=tt[tt.category=='S2'].set_index('qid')
rows=[]
for q in e.index:
    k=(e.twin[q],e.nq[q])
    if k in gt.index:
        g=gt.loc[k]
        rows.append((q,e.video_id[q],g.video_id,g.answer,v3[q],m[q],q in set(d.qid)))
r=pd.DataFrame(rows,columns=['qid','test_vid','val_vid','g','v3','merged','changed'])
r['s_v3']=item_scores(r.v3.values,r.g.values); r['s_m']=item_scores(r.merged.values,r.g.values)
pd.set_option('display.width',200)
print(r.to_string())
print(r[['s_v3','s_m']].mean())
