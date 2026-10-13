"""val GT mapped onto test rows (all renders) for MEASUREMENT only. Writes known_lab.pkl {test qid: gt}."""
import sys, re, pickle
sys.path.insert(0,'/home/user/quantiphy-challenge')
import pandas as pd
from qp.data import load_split
def base_of(v): return re.sub(r"(captured_\d+[ab]?)[sxX]?$", r"\1", v)
def normq(q): return re.sub(r"[^a-z0-9.]", "", str(q).lower())
t=load_split('test'); v=load_split('val')
t['base']=t.video_id.map(base_of); v['base']=v.video_id.map(base_of)
t['nq']=t.question.map(normq); v['nq']=v.question.map(normq)
out={}
for r in v.itertuples():
    m=t[(t.base==r.base)&(t.nq==r.nq)&(t.category==r.category)]
    for q in m.qid: out[int(q)]=float(r.answer)
pickle.dump(out,open('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/merge/S3/known_all.pkl','wb'))
tt=t.set_index('qid')
k=pd.Series(out); print(len(k)); print(tt.loc[k.index].groupby(['category','video_source']).size())
