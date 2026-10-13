from tab import *
from qp.postprocess import FrameCache, frame_similarity, _unit_rows
t=pd.read_pickle(W+'/T.pkl')
fc=FrameCache(cache_dir=W+'/ppcache')
vids=t[t.fam.notna()].drop_duplicates('video_id')[['video_id','video_path','fam','base']]
TH={}
for r in vids.itertuples():
    c=fc.thumbs(r.video_id,r.video_path)
    if c is not None: TH[r.video_id]=c
fc.save()
rows=[]
for f,g in vids.groupby('fam'):
    vs=[v for v in g.video_id if v in TH]
    for i,a in enumerate(vs):
        for b in vs[i+1:]:
            s=frame_similarity(TH[a]['th'],TH[b]['th'])
            ar=abs(TH[a]['ar']/TH[b]['ar']-1)
            rows.append(dict(fam=f,a=a,b=b,ncc=s['ncc'],ancc=s['aligned_ncc'],amad=s['aligned_mad'],ar=ar))
P=pd.DataFrame(rows); P.to_pickle(W+'/pairs_ncc.pkl')
print(len(P))
