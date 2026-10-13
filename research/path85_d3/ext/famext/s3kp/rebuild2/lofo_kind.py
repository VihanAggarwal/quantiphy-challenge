"""Leave-one-fact-out of per-kind K and series pooling P on S3 and D3 stated facts (test inputs only)."""
from common import *
A['method']=ti.loc[A.qid,'method'].values
A['lk']=np.log(A.value/A.v3)
A['fact']=A.line.str.strip().str.lower()+'|'+A.value.round(6).astype(str)
SIZEK={'size','distance','displacement','path_length'}
def kgroup(kind):
    if kind in SIZEK: return 'size'
    if kind=='speed': return 'speed'
    return kind
def is_direct_row(q):
    return str(ti.loc[q,'method'])=='direct'
_clipcache={}
def clipK(v, excl, mode, kind):
    """mode: 'all' (size+speed facts, as probe 5 D3), 'kind' (same kind group facts only), 'none'"""
    if mode=='none': return 0.0
    g=A[(A.video_id==v)&~A.fact.isin(excl)]
    if mode=='all': g=g[g.kind.isin(['size','speed'])]
    elif mode=='kind': g=g[g.kind.map(kgroup)==kgroup(kind)]
    elif mode=='size_only':
        if kgroup(kind)!='size': return 0.0
        g=g[g.kind=='size']
    elif mode=='speed_only':
        if kgroup(kind)!='speed': return 0.0
        g=g[g.kind=='speed']
    if not len(g): return 0.0
    return float(np.median(np.r_[g.lk.values,0.0]))
KAPPLY={'all':('size','speed'),'kind':('size','speed','distance'),'size_only':('size','distance'),'speed_only':('speed',),'none':()}
def corr(p, excl, kmode_s3, kmode_d3):
    r=ti.loc[p]; val=v3[p]
    mode=kmode_s3 if r.category=='S3' else kmode_d3
    if is_direct_row(p) and r.video_id.startswith('simulation') and r.tkind in KAPPLY[mode]:
        val=val*np.exp(clipK(r.video_id, excl, mode, r.tkind))
    return val
def predict(q, excl, kmode_s3='none', kmode_d3='none', pool=False, minb=3, kself=True):
    if not pool:
        return corr(q,excl,kmode_s3,kmode_d3) if kself else v3[q]
    per=per_base_values(ti,eq,q,include_self=True)
    if len(per)<minb: return corr(q,excl,kmode_s3,kmode_d3) if kself else v3[q]
    vals=[]
    for b,(rank,val,p) in per.items():
        vals.append((corr(p,excl,kmode_s3,kmode_d3) if (p!=q or kself) else v3[p])*usc(p))
    return gmed(vals)/usc(q)
def run(configs, cats=('S3','D3')):
    rows=[]
    for fact,g in A.groupby('fact'):
        ex={fact}
        for r in g.itertuples():
            if r.cat not in cats or r.method!='direct': continue
            d=dict(cat=r.cat,qid=r.qid,vid=r.video_id,kind=r.kind,V=r.value,v3=r.v3,fact=fact)
            for name,cfg in configs.items():
                p=predict(r.qid,ex,**cfg); d['p_'+name]=p; d[name]=m1(p,r.value)
            rows.append(d)
    return pd.DataFrame(rows)
CONF={
 'raw':dict(),
 'Kall':dict(kmode_s3='all',kmode_d3='all'),
 'Kkind':dict(kmode_s3='kind',kmode_d3='kind'),
 'Ksize':dict(kmode_s3='size_only',kmode_d3='size_only'),
 'Kspd':dict(kmode_s3='speed_only',kmode_d3='speed_only'),
 'P':dict(pool=True),
 'P_Kall':dict(pool=True,kmode_s3='all',kmode_d3='all'),
 'P_Kkind':dict(pool=True,kmode_s3='kind',kmode_d3='kind'),
 'P_Kd3all_s3kind':dict(pool=True,kmode_s3='kind',kmode_d3='all'),
 'P_Kd3all_s3none':dict(pool=True,kmode_s3='none',kmode_d3='all'),
 'P_Kd3all_s3size':dict(pool=True,kmode_s3='size_only',kmode_d3='all'),
}
if __name__=='__main__':
    pd.set_option('display.width',250); pd.set_option('display.max_rows',300)
    R_=run(CONF)
    R_.to_pickle(OUT+'/lofo_rows.pkl')
    names=list(CONF)
    print('ROW MEAN by cat'); print(R_.groupby('cat')[names].mean().round(3).to_string())
    print('ROW MEAN by cat,kind'); print(R_.groupby(['cat','kind'])[names].agg('mean').round(3).assign(n=R_.groupby(['cat','kind']).size()).to_string())
    R_['fk']=R_.fact.str.split('|').str[0]
    print('FACT-EQUAL by cat'); print(R_.groupby(['cat','fk'])[names].mean().groupby('cat').mean().round(3).to_string())
    s=R_[R_.cat=='S3']
    print(s[['qid','vid','kind','V','v3','p_Kall','p_Kkind','p_P','p_P_Kall','p_P_Kkind','p_P_Kd3all_s3none','raw','P','P_Kall','P_Kd3all_s3none']].round(3).to_string())
