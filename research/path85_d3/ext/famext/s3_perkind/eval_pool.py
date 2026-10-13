"""Pooling variants on S3/D3 sim size+speed rows: LOFO on stated facts + known (validation-on-test) rows."""
from lofo_kind import *
known=known_rows2()
SUSPECT_T={139}  # measurement only (verifier note); validation-suspect qids are validation ids, not test ids
def pool_val(q, excl, kmode_s3, kmode_d3, minb=3, guard=None, tau=None, kself=True):
    """guard: None | 'skip_outlier' (keep own when own deviates > tau from pool-of-others: different object?)
               | 'replace_outlier' (use pool only when own deviates > tau)"""
    own=corr(q,excl,kmode_s3,kmode_d3) if kself else v3[q]
    per=per_base_values(ti,eq,q,include_self=True)
    if len(per)<minb: return own, False
    vals=[]; oth=[]
    for b,(rank,val,p) in per.items():
        x=(corr(p,excl,kmode_s3,kmode_d3) if (p!=q or kself) else v3[p])*usc(p)
        vals.append(x)
        if p!=q: oth.append(x)
    pv=gmed(vals)/usc(q)
    if guard and oth:
        go=gmed(oth)/usc(q); dev=abs(np.log(v3[q]/go))
        if guard=='skip_outlier' and dev>np.log(tau): return own, False
        if guard=='replace_outlier' and dev<=np.log(tau): return own, False
    return pv, True
CFGS={
 'raw':None,
 'P':dict(kmode_s3='none',kmode_d3='all'),
 'P_skip1.6':dict(kmode_s3='none',kmode_d3='all',guard='skip_outlier',tau=1.6),
 'P_skip1.3':dict(kmode_s3='none',kmode_d3='all',guard='skip_outlier',tau=1.3),
 'P_repl1.15':dict(kmode_s3='none',kmode_d3='all',guard='replace_outlier',tau=1.15),
 'P_repl1.3':dict(kmode_s3='none',kmode_d3='all',guard='replace_outlier',tau=1.3),
 'P_repl1.6':dict(kmode_s3='none',kmode_d3='all',guard='replace_outlier',tau=1.6),
 'P_noK':dict(kmode_s3='none',kmode_d3='none'),
 'P_minb4':dict(kmode_s3='none',kmode_d3='all',minb=4),
 'P_minb5':dict(kmode_s3='none',kmode_d3='all',minb=5),
}
def evaluate(rows):
    out=[]
    for (q,V,excl,src) in rows:
        d=dict(qid=q,vid=ti.loc[q,'video_id'],cat=ti.loc[q,'category'],kind=ti.loc[q,'tkind'],V=V,src=src,v3=v3[q])
        for n,c in CFGS.items():
            p=v3[q] if c is None else pool_val(q,excl,**c)[0]
            d[n]=m1(p,V); d['p_'+n]=p
        out.append(d)
    return pd.DataFrame(out)
if __name__=='__main__':
    pd.set_option('display.width',260); pd.set_option('display.max_rows',300)
    rows=[]
    A_=A[(A.method=='direct')&A.cat.isin(['S3','D3'])]
    for r in A_.itertuples(): rows.append((r.qid,r.value,{r.fact},'lofo'))
    for q,V in known.items():
        if q in SUSPECT_T: continue
        r=ti.loc[q]
        if r.category in ('S3','D3') and r.video_id.startswith('simulation') and str(r.method)=='direct' and q not in set(A_.qid):
            rows.append((q,V,set(),'known'))
    E=evaluate(rows)
    E.to_pickle(OUT+'/eval_pool.pkl')
    names=list(CFGS)
    E['sz']=E.kind.map(lambda k:'size' if k in SIZEK else k)
    print(E.groupby(['src','cat','sz'])[names].mean().round(3).assign(n=E.groupby(['src','cat','sz']).size()).to_string())
    # rows where any pool config differs from raw
    ch=E[[not np.isclose(r['p_P'],r['v3']) for _,r in E.iterrows()]]
    print(ch[['qid','vid','cat','kind','src','V','v3','p_P','p_P_skip1.6','p_P_repl1.3','raw','P','P_skip1.6','P_repl1.3','P_repl1.15']].round(3).to_string())
