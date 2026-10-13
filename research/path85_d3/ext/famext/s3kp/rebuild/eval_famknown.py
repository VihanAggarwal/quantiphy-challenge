"""Family-known evaluation: a row's truth proxy = validation answer of an EQUIVALENT row (same object and quantity,
same scene family; eq3 groups) on another test clip. Measurement only."""
from eval_pool import *
def famknown_rows(cats=('S3','D3')):
    rows=[]
    for q in ti.index:
        r=ti.loc[q]
        if r.category not in cats or not r.video_id.startswith('simulation') or str(r.method)!='direct': continue
        if q in known: continue
        kv=[known[p] for p in eq[q] if p!=q and p in known and p not in SUSPECT_T]
        if not kv: continue
        if max(kv)/min(kv)>1.05: continue
        rows.append((q,float(np.median(kv)),set(),'famknown'))
    return rows
if __name__=='__main__':
    pd.set_option('display.width',260); pd.set_option('display.max_rows',300)
    E=evaluate(famknown_rows())
    E['sz']=E.kind.map(lambda k:'size' if k in SIZEK else k)
    names=list(CFGS)
    print(E.groupby(['cat','sz'])[names].mean().round(3).assign(n=E.groupby(['cat','sz']).size()).to_string())
    E['p5']=E.qid.map(p5); E['m_p5']=[m1(a,b) for a,b in zip(E.p5,E.V)]
    print(E[['qid','vid','cat','kind','V','v3','p5','p_P','p_P_repl1.3','raw','m_p5','P','P_repl1.3','P_skip1.6']].round(3).to_string())
    E.to_pickle(OUT+'/eval_famknown.pkl')
