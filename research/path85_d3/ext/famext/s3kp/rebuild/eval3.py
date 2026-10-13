from s3pool import *
from eval_famknown import famknown_rows, known, SUSPECT_T
from eval2 import d3share
def evalset(cat):
    rows=[]
    A_=A[(A.method=='direct')&(A.cat==cat)]
    for r in A_.itertuples(): rows.append((r.qid,r.value,{r.fact},'lofo'))
    for q,V in known.items():
        r=ti.loc[q]
        if r.category==cat and r.video_id.startswith('simulation') and str(r.method)=='direct' and q not in set(A_.qid): rows.append((q,V,set(),'known'))
    rows+=famknown_rows((cat,))
    return rows
CF={'raw':lambda q,ex: v3[q]}
for s3m in ['none','kind','size_only']:
    for g in [None,'bimodal']:
        CF[f'P_{s3m}_{g}']=(lambda s3m,g: (lambda q,ex: (pooled(q,ex,s3m,guard=g)[0] or v3[q])))(s3m,g)
if __name__=='__main__':
    pd.set_option('display.width',260); pd.set_option('display.max_rows',300)
    for cat in ['S3','D3']:
        out=[]
        for (q,V,ex,src) in evalset(cat):
            d=dict(qid=q,src=src,kind='size' if ti.loc[q,'tkind'] in SIZEK else ti.loc[q,'tkind'])
            for n,f in CF.items(): d[n]=m1(f(q,ex),V)
            out.append(d)
        E=pd.DataFrame(out); names=list(CF)
        print(cat); print(E.groupby(['src','kind'])[names].mean().round(3).assign(n=E.groupby(['src','kind']).size()).to_string())
        print(E.groupby('kind')[names].mean().round(3).to_string())
    # which S3 groups the guard blocks
    s=t[(t.category.isin(['S3','D3']))&(t.video_source!='lab')]
    blk=[]
    for q in s.qid:
        if str(ti.loc[q,'method'])!='direct' or ti.loc[q,'tkind'] not in ('size','speed','distance'): continue
        v,w=pooled(q,s3mode='kind')
        if w=='bimodal': blk.append((q,ti.loc[q,'category'],ti.loc[q,'video_id'],ti.loc[q,'tobj'],ti.loc[q,'tdim'],v3[q]))
    print(pd.DataFrame(blk,columns=['qid','cat','vid','obj','dim','v3']).to_string())
