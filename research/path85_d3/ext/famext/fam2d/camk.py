"""Within one camera view, clips with different priors should share the metric scale of each object. Test whether a
clip's deviation from its camera-mates is a per-clip scale (shared by all its answers): leave-one-question-out."""
from pool2 import *
t=pd.read_pickle(W+'/T.pkl'); ti=t.set_index('qid')
eq=groups(t,cats=('S2','D2'))
rows=[]
for c in comps_of(eq):
    g=ti.loc[c]
    if g.tkind.iloc[0] not in ('size','speed','acceleration','displacement'): continue
    for cam,gc in g.groupby('cam'):
        if gc.video_id.nunique()<2: continue
        lv={q:np.log(to_si(ti,q,r.p5)) for q,r in gc.iterrows()}
        for q,r in gc.iterrows():
            oth=[lv[p] for p,rr in gc.iterrows() if rr.video_id!=r.video_id and pnorm(rr.prior)!=pnorm(r.prior)]
            if not oth: continue
            rows.append(dict(qid=q,video_id=r.video_id,cam=cam,cat=r.category,kind=r.tkind,d=lv[q]-np.mean(oth)))
D=pd.DataFrame(rows)
print('rows',len(D),'clips',D.video_id.nunique())
res=[]
for v,g in D.groupby('video_id'):
    if len(g)<2: continue
    for i,r in g.iterrows():
        k=np.median(np.r_[g.drop(i).d.values])
        res.append(dict(video_id=v,d=r['d'],k=k,n=len(g)))
Rr=pd.DataFrame(res)
print('rows with other shared q in same clip',len(Rr),'clips',Rr.video_id.nunique())
print('corr(d,k)',np.corrcoef(Rr.d,Rr.k)[0,1].round(3),' mean|d|',Rr.d.abs().mean().round(4),' mean|d-k|',(Rr.d-Rr.k).abs().mean().round(4), ' mean|d-k/2|',(Rr.d-Rr.k/2).abs().mean().round(4))
print('pseudo MRA (truth = camera-mates): raw',S(Rr.d).mean().round(4),' K',S(Rr.d-Rr.k).mean().round(4),' K/2',S(Rr.d-Rr.k/2).mean().round(4))
print(Rr.groupby('video_id').agg(n=('d','size'),d=('d','mean'),k=('k','mean')).round(3).sort_values('d').to_string())
