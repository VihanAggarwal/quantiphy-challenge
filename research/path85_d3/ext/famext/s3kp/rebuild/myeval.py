from build_s3 import *
from eval_famknown import known, SUSPECT_T
pd.set_option('display.width',250); pd.set_option('display.max_rows',300)
# (1) LOFO on S3 stated facts using the BUILD's pooled() (per-kind S3 members, all-kind D3 members, guard)
rows=[]
for r in A[(A.cat=='S3')].itertuples():
    q=r.qid
    if str(ti.loc[q,'method'])!='direct': continue
    fact=r.line.strip().lower()+'|'+str(round(r.value,6))
    v,w=pooled(q,frozenset({fact}),'kind')
    v0,w0=pooled(q,frozenset({fact}),'none')
    rows.append(dict(qid=q,vid=r.video_id[-14:],kind=r.kind,obj=str(ti.loc[q,'tobj'])[:14],V=r.value,v3=v3[q],pool=v,why=w,pool0=v0,
                     m_raw=m1(v3[q],r.value),m_pool=m1(v if v else v3[q],r.value),m_pool0=m1(v0 if v0 else v3[q],r.value)))
L=pd.DataFrame(rows); print(L.round(3).to_string()); print(L.groupby('kind')[['m_raw','m_pool','m_pool0']].mean().round(3), L.groupby('kind').size())
