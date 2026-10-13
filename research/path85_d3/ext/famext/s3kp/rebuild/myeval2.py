from build_s3 import *
from eval_famknown import known, SUSPECT_T
pd.set_option('display.width',250); pd.set_option('display.max_rows',300)
res,allch=pickle.load(open(OUT+'/build_res.pkl','rb'))
def proxy(q):
    if q in known: return known[q],'known',q
    kp=[p for p in eq[q] if p!=q and p in known and p not in SUSPECT_T]
    kv=[known[p] for p in kp]
    if kv and max(kv)/min(kv)<=1.05: return float(np.median(kv)),'fam',tuple(sorted(kp))
    return None,None,None
print('known S3 sim rows:',sorted([q for q in known if ti.loc[q,'category']=='S3' and ti.loc[q,'video_source']!='lab']))
R=[]
for name,ch in allch.items():
    for q,v in ch.items():
        V,src,lab=proxy(q)
        R.append(dict(var=name,qid=q,vid=ti.loc[q,'video_id'][-14:],obj=str(ti.loc[q,'tobj'])[:12],dim=ti.loc[q,'tdim'],src=src,lab=str(lab),V=V,p5=p5[q],new=v,
                      d=(m1(v,V)-m1(p5[q],V)) if V else np.nan))
R=pd.DataFrame(R)
print(R[R['var']=='S3_PK_DS'].round(3).to_string())
print(R.groupby('var').agg(n=('qid','size'),nproxy=('d','count'),dsum=('d','sum')).assign(per=lambda x:x.dsum/x.nproxy).round(3))
print('by label source (S3_PK_DS):'); print(R[R['var']=='S3_PK_DS'].groupby(['obj','dim','lab']).d.agg(['count','sum']).round(2))
R.to_pickle('myeval2.pkl')
