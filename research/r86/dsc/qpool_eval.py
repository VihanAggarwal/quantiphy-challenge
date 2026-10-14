"""Evaluate the same-question static pooling rule on labelled rows: validation rows (evaluation only) and test
stated-fact rows (the fact value as label; the row's own answer before facts is not available here, so fact rows
are evaluated as 'would pooling move a correct answer away')."""
import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/r86/dsc')
from common import *
W='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ext/d3rest/verified/rebuild/work/'
t=pd.read_pickle(W+'TS_ext.pkl')
d=load().set_index('qid')
t['cur']=t.qid.map(d.pred)
t=t[t.video_id.str.startswith('simulation')]
v=loadval()
key=v.groupby(['video_id','question']).y.first()
t['y']=[key.get((a,b),np.nan) for a,b in zip(t.video_id,t.question)]
t['nq']=t.question.str.lower().str.replace(r'[^a-z0-9.]','',regex=True)
static=~t.question.str.contains(r'speed|veloc|accel|displace|\bat\s*[\d.]+\s*s|t=|time|travel|walked|path',case=False)
t=t[static]
for OUT,AGREE in [(1.2,1.3),(1.3,1.3),(1.5,1.3),(1.3,1.5)]:
    res=[]
    for (f,q),g in t.groupby(['fam','nq']):
        per=g.groupby('base').cur.median()
        if len(per)<3: continue
        for _,r in g.iterrows():
            if not np.isfinite(r.y): continue
            oth=per.drop(r.base)
            if len(oth)<2 or oth.max()/oth.min()>AGREE: continue
            m=float(np.exp(np.log(oth).mean()))
            trig=abs(np.log(r.cur/m))>np.log(OUT)
            res.append(dict(vid=r.video_id,q=r.question[:60],y=r.y,cur=r.cur,new=m,trig=trig,s0=mra(r.cur,r.y),s1=mra(m,r.y)))
    R=pd.DataFrame(res)
    T=R[R.trig]
    print(f'OUT {OUT} AGREE {AGREE}: val rows eligible {len(R)}, triggered {len(T)}, score {T.s0.sum():.1f} -> {T.s1.sum():.1f}; all-eligible pooled {R.s0.mean():.3f}->{R.s1.mean():.3f}')
    if OUT==1.3 and AGREE==1.3: print(T.to_string())
