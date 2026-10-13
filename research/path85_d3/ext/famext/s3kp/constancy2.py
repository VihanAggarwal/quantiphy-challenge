"""Do stated priors of one family clip match validation answers of the same quantity on another clip? (measurement only)"""
import pandas as pd, numpy as np
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
A=pd.read_pickle(SP+'/big/scenegraph/work/transfers3.pkl')
m=pd.read_csv(SP+'/hyp/S2/val_test_map.csv').sort_values('sim').drop_duplicates('tqid',keep='last'); m=m[m.sim>=0.9]
known=dict(zip(m.tqid,m.answer))
r=A[A.qid.isin(known)].copy(); r['val']=r.qid.map(known); r['ratio']=r.value/r.val
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',50)
print(r[['qid','video_id','question','value','val','ratio','conflict','why','line']].to_string())
