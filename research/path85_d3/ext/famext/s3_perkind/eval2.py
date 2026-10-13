"""All S3 candidate rules evaluated on (a) LOFO facts, (b) known rows, (c) family-known proxies. Measurement only."""
from eval_famknown import *
def d3share(q):
    m=[p for p in eq[q] if p!=q and ti.loc[p,'category']=='D3' and ti.loc[p,'video_id'].startswith('simulation')]
    if not m: return v3[q]
    return gmed([p5[p]*usc(p) for p in m])/usc(q)
CF2={
 'raw':lambda q,ex: v3[q],
 'Ksz':lambda q,ex: corr(q,ex,'size_only','all'),
 'Kspd':lambda q,ex: corr(q,ex,'speed_only','all'),
 'Kkind':lambda q,ex: corr(q,ex,'kind','all'),
 'Kall':lambda q,ex: corr(q,ex,'all','all'),
 'P':lambda q,ex: pool_val(q,ex,'none','all')[0],
 'P_noK':lambda q,ex: pool_val(q,ex,'none','none')[0],
 'P_Kkind':lambda q,ex: pool_val(q,ex,'kind','all')[0],
 'P_Ksz':lambda q,ex: pool_val(q,ex,'size_only','all')[0],
 'P_Kall':lambda q,ex: pool_val(q,ex,'all','all')[0],
 'P_Kkind_d3kind':lambda q,ex: pool_val(q,ex,'kind','kind')[0],
 'D3share':lambda q,ex: d3share(q),
}
def ev(rows):
    out=[]
    for (q,V,ex,src) in rows:
        if ti.loc[q,'category']!='S3': continue
        d=dict(qid=q,vid=ti.loc[q,'video_id'],kind=ti.loc[q,'tkind'],V=V,src=src,v3=v3[q],p5=p5[q])
        for n,f in CF2.items():
            p=f(q,ex); d['p_'+n]=p; d[n]=m1(p,V)
        d['p5m']=m1(p5[q],V)
        out.append(d)
    return pd.DataFrame(out)
if __name__=='__main__':
    pd.set_option('display.width',260); pd.set_option('display.max_rows',300)
    rows=[]
    A_=A[(A.method=='direct')&(A.cat=='S3')]
    for r in A_.itertuples(): rows.append((r.qid,r.value,{r.fact},'lofo'))
    for q,V in known.items():
        r=ti.loc[q]
        if r.category=='S3' and r.video_id.startswith('simulation') and str(r.method)=='direct' and q not in set(A_.qid): rows.append((q,V,set(),'known'))
    rows+=famknown_rows(('S3',))
    E=ev(rows); E['sz']=E.kind.map(lambda k:'size' if k in SIZEK else k)
    names=list(CF2)+['p5m']
    print(E.groupby(['src','sz'])[names].mean().round(3).assign(n=E.groupby(['src','sz']).size()).to_string())
    print('ALL S3 rows:'); print(E.groupby('sz')[names].mean().round(3).assign(n=E.groupby('sz').size()).to_string())
    E.to_pickle(OUT+'/eval2.pkl')
    ch=E[[not all(np.isclose(r['p_'+n],r['v3']) for n in CF2) for _,r in E.iterrows()]]
    print(ch[['qid','vid','kind','src','V','v3','p5','p_Ksz','p_P','p_P_noK','p_P_Ksz','p_D3share','raw','p5m','Ksz','P','P_noK','P_Ksz','D3share']].round(3).to_string())
