"""Twin averaging check: for S3/D3 sim twin pairs (original + pixel-aligned segmented re-render, two independent
Claude reads), compare original answer / segmented's own answer / geometric mean on known + family-known proxies."""
from expect import *
from qp.data import load_split
pairs=[]
for cat in ['S3','D3']:
    for q in ti.index:
        r=ti.loc[q]
        if r.category!=cat or not r.video_id.endswith('_segmented') or not r.video_id.startswith('simulation'): continue
        nq=lambda s: re.sub(r'\s+',' ',str(s).strip().lower()).rstrip('?. ')
        c=t[(t.video_id==r.base)&(t.question.map(nq)==nq(r.question))&(t.prior==r.prior)&(t.depth_info==r.depth_info)&(t.target_unit==r.target_unit)]
        if len(c)!=1: continue
        o=int(c.qid.iloc[0])
        if str(ti.loc[o,'method'])!='direct' or str(r.method)!='direct': continue
        pairs.append((cat,o,q))
print(len(pairs), pd.Series([p[0] for p in pairs]).value_counts().to_dict())
rows=[]
for cat,o,s in pairs:
    for q in (o,s):
        V,src=proxy(q)
        if V is None: continue
        gm=float(np.sqrt(v3[o]*v3[s]))
        rows.append(dict(cat=cat,q=q,role='orig' if q==o else 'seg',src=src,V=V,orig=v3[o],seg=v3[s],gm=gm,p5=p5[q],
                         m_orig=m1(v3[o],V),m_seg=m1(v3[s],V),m_gm=m1(gm,V),m_p5=m1(p5[q],V)))
R_=pd.DataFrame(rows)
pd.set_option('display.width',250); pd.set_option('display.max_rows',200)
print(R_.groupby(['cat','src'])[['m_orig','m_seg','m_gm','m_p5']].mean().round(3).assign(n=R_.groupby(['cat','src']).size()))
# twin disagreement in S3 overall
d=pd.DataFrame([dict(cat=c,lr=abs(np.log(v3[o]/v3[s]))) for c,o,s in pairs])
print(d.groupby('cat').lr.describe())
