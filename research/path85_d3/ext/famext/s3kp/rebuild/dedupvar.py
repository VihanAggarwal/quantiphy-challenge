from build_s3 import *
from eval_famknown import known
res,allch=pickle.load(open(OUT+'/build_res.pkl','rb'))
S=pd.read_pickle('viewsim.pkl')
same={}
for (a,b),s in S.items():
    if s>=0.95: same.setdefault(a,set()).add(b); same.setdefault(b,set()).add(a)
def comp(v,vs):
    out={v}; st=[v]
    while st:
        x=st.pop()
        for y in same.get(x,()):
            if y in vs and y not in out: out.add(y); st.append(y)
    return frozenset(out)
def pooled_dd(q, excl=frozenset(), s3mode='kind', minb=3, gfac=1.6, gshare=1/3):
    per=per_base_values(ti,eq,q,include_self=True)
    mv={ti.loc[p,'video_id']:member_val(p,excl,s3mode)*usc(p) for b,(rk,vv,p) in per.items()}
    vs=set(mv); groups=set(comp(v,vs) for v in vs)
    vals=np.array([gmed([mv[v] for v in g]) for g in groups])
    if len(vals)<minb: return None,'few_views'
    gm=gmed(vals); n=len(vals); hi=(vals>gm*gfac).sum(); lo=(vals<gm/gfac).sum()
    if max(hi,lo)>=max(2,gshare*n): return None,'bimodal'
    return gm/usc(q),'pool'
rows=[]
for q,v in allch['S3_PK_DS'].items():
    w=None
    if q in TW: o=TW[q]; nv,w=pooled_dd(o) if o in allch['S3_PK_DS'] else (None,None)
    else: nv,w=pooled_dd(q)
    if q==1162: nv,w=v,'DS'
    V=known.get(q)
    if V is None:
        kv=[known[p] for p in eq[q] if p!=q and p in known]
        V=float(np.median(kv)) if kv and max(kv)/min(kv)<=1.05 else None
    rows.append(dict(qid=q,vid=ti.loc[q,'video_id'][-14:],obj=str(ti.loc[q,'tobj'])[:12],dim=ti.loc[q,'tdim'],p5=p5[q],pk=v,dd=nv if nv else p5[q],w=w,V=V,
                     d_pk=(m1(v,V)-m1(p5[q],V)) if V else np.nan, d_dd=(m1(nv if nv else p5[q],V)-m1(p5[q],V)) if V else np.nan))
R=pd.DataFrame(rows); pd.set_option('display.width',250)
print(R.round(3).to_string()); print(R[['d_pk','d_dd']].sum(), R.d_pk.count())
