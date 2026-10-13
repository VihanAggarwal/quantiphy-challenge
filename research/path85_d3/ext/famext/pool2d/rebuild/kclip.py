from pool import *
t=pd.read_pickle(W+'/T.pkl'); ti=t.set_index('qid')
eq=groups(t,cats=('S2','D2'))
rows=[]
for c in comps_of(eq):
    g=ti.loc[c]
    if g.tkind.iloc[0] not in ('size','speed','acceleration','displacement'): continue
    per={}
    for q,r in g.iterrows(): per.setdefault(r.base,[]).append((q,np.log(to_si(ti,q,r.p5))))
    if len(per)<3: continue
    bl={b:np.mean([x[1] for x in v]) for b,v in per.items()}
    for b,v in per.items():
        others=[bl[o] for o in bl if o!=b]
        ref=np.median(others)
        for q,lv in v:
            rows.append(dict(qid=q,video_id=ti.loc[q,'video_id'],base=b,cat=ti.loc[q,'category'],kind=ti.loc[q,'tkind'],grp=c[0],d=lv-ref,nb=len(bl)))
D=pd.DataFrame(rows)
D.to_pickle(W+'/dev.pkl')
print(len(D), D.video_id.nunique())
# within-clip LOO K
res=[]
for v,g in D.groupby('video_id'):
    if len(g)<2: continue
    for i,r in g.iterrows():
        k=np.median(g.drop(i).d)
        res.append(dict(video_id=v,cat=r['cat'],kind=r['kind'],d=r['d'],k=k,dk=r['d']-k,n=len(g)))
R=pd.DataFrame(res)
print('rows with >=1 other member in same clip',len(R))
print('mean|d| raw',R.d.abs().mean().round(4),' after K',R.dk.abs().mean().round(4))
print('corr(d,k)',np.corrcoef(R.d,R.k)[0,1].round(3))
# MRA-like: score vs pseudo-truth=pool_{-clip}
from qp.mra import item_scores
s_raw=item_scores(np.exp(R.d),np.ones(len(R))).mean(); s_k=item_scores(np.exp(R.dk),np.ones(len(R))).mean()
print('pseudo MRA raw',round(s_raw,4),'K',round(s_k,4))
for kd,g in R.groupby('kind'):
    print(kd,len(g),'|d|',g.d.abs().mean().round(4),'|d-k|',g.dk.abs().mean().round(4), 'corr',np.corrcoef(g.d,g.k)[0,1].round(3))
# variance decomposition
cl=D.groupby('video_id').d
print('between-clip var of clip means',D.groupby('video_id').d.mean().var().round(5),' total var',D.d.var().round(5), 'mean within var', cl.var().mean().round(5))
