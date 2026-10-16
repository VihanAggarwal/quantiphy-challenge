import sys; sys.path.insert(0,'.')
sys.path.insert(0,'research/next/nlres')
import numpy as np, pandas as pd
from tables import answers, col, qkind, ctype
from qp import postprocess as pp
pd.set_option('display.width',250); pd.set_option('display.max_rows',500)
t=pd.read_pickle('research/r86/loss_audit/master.pkl')
ag=answers('/tmp/blind_test')
t['agent']=[ag.get((v,i),np.nan) for v,i in zip(t.video_id,t.index)]
orig={(vv,pp.norm_question(q)):i for i,vv,q in zip(t.index,t.video_id,t.question) if not vv.endswith('_segmented')}
for i in t.index[t.agent.isna()]:
    vv,q=t.at[i,'video_id'],t.at[i,'question']
    if vv.endswith('_segmented'):
        j=orig.get((vv[:-10],pp.norm_question(q)))
        if j is not None: t.at[i,'agent']=ag.get((vv[:-10],j),np.nan)
t['best']=col('submissions/trackA_probe_agent_sim2agent.csv').reindex(t.index)
t['c1']=col('submissions/trackA_cand_C1_solS2S3.csv').reindex(t.index)
t['sol']=col('runs/test_sol_high/test.csv','direct_value').reindex(t.index)
t['qkind']=t.question.map(qkind)
t['ctype']=[ctype(a,b,c) for a,b,c in zip(t.video_type,t.srcg,t.video_id)]
t['isfact']=t.fact.notna()&np.isclose(t.best,t.fact.fillna(-1),rtol=1e-6)
t.to_pickle('research/next/nlres/test.pkl')
s=t[t.scored]
print(pd.crosstab([s.ctype,s.qkind],s.category,margins=True))
print("best==agent", pd.Series(np.isclose(s.best,s.agent),index=s.index).groupby(s.ctype).mean())
