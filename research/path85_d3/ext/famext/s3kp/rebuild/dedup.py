from build_s3 import *
Rg=pd.read_pickle(W+'/work/aligned.pkl')
print(Rg.columns.tolist(), len(Rg))
print(Rg.head(3).to_string()[:1500])
res,allch=pickle.load(open(OUT+'/build_res.pkl','rb'))
pairs={}
for r in Rg.itertuples():
    pairs[(r.a,r.b)]=r; pairs[(r.b,r.a)]=r
for q in allch['S3_PK_DS']:
    per=per_base_values(ti,eq,q,include_self=True)
    vids=[ti.loc[p,'video_id'] for b,(rk,vv,p) in per.items()]
    hits=[(a[-14:],b[-14:],round(float(max(pairs[(a,b)].mad_aligned)),3),round(float(min(pairs[(a,b)].ncc_aligned)),4)) for i,a in enumerate(vids) for b in vids[i+1:] if (a,b) in pairs]
    if hits: print(q, ti.loc[q,'video_id'][-14:], ti.loc[q,'tobj'], ti.loc[q,'tdim'], hits)
