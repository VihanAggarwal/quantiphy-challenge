"""Track B variant of build_famcons.py: the same model-free rules on Track B's OWN answers (no Track A output is
read): A = identical static question pooling inside the extended families (TS_ext structure = test inputs), using
Track B answers of the other clips; B/D = stated facts (test inputs). Usage: build_famcons_trackb.py [trackB.csv]"""
import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/r86/dsc')
from common import *
src=sys.argv[1] if len(sys.argv)>1 else f'{ROOT}/submissions/trackB_v3_catmedian_famrules.csv'
W='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ext/d3rest/verified/rebuild/work/'
sub=pd.read_csv(src); B=pd.Series(sub.parsed_value.values,index=sub.id.values)
t=pd.read_pickle(W+'TS_ext.pkl'); t['cur']=t.qid.map(B)
t=t[t.video_id.str.startswith('simulation')]
t['nq']=t.question.str.lower().str.replace(r'[^a-z0-9.]','',regex=True)
t=t[~t.question.str.contains(r'speed|veloc|accel|displace|\bat\s*[\d.]+\s*s|t=|time|travel|walked|path',case=False)]
new=B.copy(); log=[]
for (f,q),g in t.groupby(['fam','nq']):
    per=g.groupby('base').cur.median()
    if len(per)<3: continue
    for _,r in g.iterrows():
        oth=per.drop(r.base)
        if len(oth)<2 or oth.max()/oth.min()>1.3: continue
        m=float(np.exp(np.log(oth).mean()))
        if abs(np.log(r.cur/m))>np.log(1.3): new[r.qid]=m; log.append((r.qid,'A_qpool',r.cur,m))
for q,v in {6:1.19,1649:1.19,992:.75,1469:.75,1486:.75,1115:1.3,1689:1.3}.items():
    log.append((q,'B/D_fact',new[q],v)); new[q]=v
sub['parsed_value']=new.values
assert np.isfinite(sub.parsed_value).all() and (sub.parsed_value>0).all()
sub.to_csv(f'{ROOT}/research/r86/dsc/cand_famcons_trackB_on_v3.csv',index=False)
pd.DataFrame(log,columns=['qid','lever','old','new']).to_csv(f'{ROOT}/research/r86/dsc/changes_famcons_trackB.csv',index=False)
print(len(log),'rows changed')
