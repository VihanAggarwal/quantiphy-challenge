"""Expected S3 delta vs probe 5 per variant: changed rows scored against (i) their own validation answer (known),
(ii) the validation answer of an equivalent row elsewhere in the family (famknown proxy). Measurement only."""
from build_s3 import *
from eval_famknown import known, SUSPECT_T
res,allch=pickle.load(open(OUT+'/build_res.pkl','rb'))
def proxy(q):
    if q in known: return known[q],'known'
    kv=[known[p] for p in eq[q] if p!=q and p in known and p not in SUSPECT_T]
    if kv and max(kv)/min(kv)<=1.05: return float(np.median(kv)),'famknown'
    return None,None
if __name__=='__main__':
    pd.set_option('display.width',260); pd.set_option('display.max_rows',300)
    summ={}
    rows=[]
    for name,ch in allch.items():
        d_known=[];d_fam=[];nop=0
        for q,v in ch.items():
            V,src=proxy(q)
            if V is None: nop+=1; continue
            d=m1(v,V)-m1(p5[q],V)
            (d_known if src=='known' else d_fam).append(d)
            rows.append(dict(var=name,qid=q,vid=ti.loc[q,'video_id'][-14:],obj=str(ti.loc[q,'tobj'])[:16],dim=ti.loc[q,'tdim'],src=src,V=V,p5=p5[q],new=v,d=d))
        n=len(ch); dk=np.sum(d_known); df=np.sum(d_fam)
        per=(dk+df)/max(1,len(d_known)+len(d_fam))
        summ[name]=dict(changed=n,known_n=len(d_known),known_sum=round(dk,2),fam_n=len(d_fam),fam_sum=round(df,2),no_proxy=nop,
                        per_row=round(per,3),delta_measured=round((dk+df)/578,4),delta_extrap=round(per*n/578,4))
        print(name,summ[name])
    R_=pd.DataFrame(rows)
    print(R_[R_['var']=='S3_PK_DS'].round(3).to_string())
    json.dump(summ,open(OUT+'/expect_summary.json','w'),indent=1)
