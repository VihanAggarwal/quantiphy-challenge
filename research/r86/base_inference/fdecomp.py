import sys, re, json, glob, math, numpy as np, pandas as pd
sys.path.insert(0,'/home/user/quantiphy-challenge'); sys.path.insert(0,'/home/user/quantiphy-challenge/scripts')
from qp.data import load_test
from qp import claude_annotate as ca
from qp.geometry import solve
import run_claude as rc
df=load_test()
recs=rc.load_records(__import__('pathlib').Path('runs/test_3dnl_v2_high/test/records'))
sub=df[df.video_id.isin(recs.keys())]
records=rc.prepare_records(sub, recs)
anns=ca.load_annotations(records)
F=re.compile(r"f\s*[~=≈]\s*~?\s*(\d+(?:\.\d+)?)\s*px", re.I)
rows=[]
for r in sub.itertuples():
    a=anns.get(int(r.qid)); rec=records[r.video_id]
    if a is None: continue
    q=[x for x in rec['parsed']['questions'] if x['qid']==int(r.qid)]
    der=q[0].get('derivation','') if q else ''
    m=F.search(der or '')
    sc=float(rec['meta'].get('scale') or 1.0)
    fcl=float(m.group(1))/sc if m else np.nan
    try:
        ans=solve(a.spec,a.tracks,tuple(rec['meta']['image_size']),float(rec['meta']['fps']),seen_scale=sc)
        fg=ans.debug.get('f_px'); geo=ans.value; meth=ans.method; fl=';'.join(sorted(ans.flags))
    except Exception as e:
        fg=np.nan; geo=np.nan; meth='err'; fl=str(e)
    rows.append(dict(qid=int(r.qid),video_id=r.video_id,W=rec['meta']['image_size'][0],scale=sc,f_claude=fcl,f_geo=fg,geo=geo,method=meth,flags=fl,direct=a.direct_answer,der=der,kind=a.spec.target.kind, pkind=a.spec.prior.kind))
R=pd.DataFrame(rows).set_index('qid')
R.to_pickle('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/fdecomp.pkl')
print(len(R), R.f_claude.notna().sum(), R.f_geo.notna().sum())
print(R.method.value_counts())
