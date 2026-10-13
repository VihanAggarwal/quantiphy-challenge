from pool import *
from qp.mra import item_scores
def S(r): return item_scores(np.exp(np.asarray(r,float)),np.ones(len(r)))
def pnorm(p): return re.sub(r'\s+','',str(p).lower())
def unit_of(r, unit):
    if unit=='base': return r.base
    if unit=='cam': return r.cam
    if unit=='camprior': return (r.cam, pnorm(r.prior))
    if unit=='clip': return r.video_id
def build_groups(t, col='p5', cats=('S2','D2'), unit='camprior', kinds=('size','speed','acceleration','displacement')):
    ti=t.set_index('qid')
    eq=groups(t,cats=cats)
    G=[]
    for c in comps_of(eq):
        g=ti.loc[c]; kind=g.tkind.iloc[0]
        if kind not in kinds: continue
        per={}
        for q,r in g.iterrows():
            per.setdefault(unit_of(r,unit),[]).append((q,np.log(to_si(ti,q,r[col]))))
        ul={u:np.mean([x[1] for x in v]) for u,v in per.items()}
        G.append(dict(grp=c[0],kind=kind,cat=g.category.iloc[0],ul=ul,members=per,spread=max(ul.values())-min(ul.values())))
    return G
def agg(v,stat):
    v=np.asarray(v,float)
    if stat=='median': return float(np.median(v))
    if stat=='mean': return float(np.mean(v))
    if stat=='trim':
        if len(v)>=4:
            m=np.median(v); v=v[np.argsort(np.abs(v-m))][:-1]
        return float(np.mean(v))
    if stat=='hl':  # Hodges-Lehmann: median of pairwise means
        w=[(a+b)/2 for i,a in enumerate(v) for b in v[i:]]; return float(np.median(w))
def pseudo(G, stat='mean', cap=10, minu=3, w=0.0, weight_rows=True):
    rows=[]
    for gr in G:
        ul=gr['ul']
        if len(ul)<minu or gr['spread']>cap: continue
        for j in ul:
            oth={u:v for u,v in ul.items() if u!=j}
            pv=agg(list(oth.values()),stat)
            for i,ai in oth.items():
                n=len(gr['members'][i]) if weight_rows else 1
                rows.append(dict(kind=gr['kind'],grp=gr['grp'],wt=n,e_raw=ai-ul[j],e_pool=w*ai+(1-w)*pv-ul[j]))
    R=pd.DataFrame(rows)
    R['d']=S(R.e_pool)-S(R.e_raw)
    return R
if __name__=='__main__':
    t=pd.read_pickle(W+'/T.pkl')
    for unit in ('base','cam','camprior'):
        G=build_groups(t,unit=unit)
        nrows={k:sum(sum(len(m) for m in gr['members'].values()) for gr in G if gr['kind']==k and len(gr['ul'])>=2) for k in ('size','speed','acceleration','displacement')}
        print(f'=== unit {unit}: rows in groups with >=2 units', nrows)
        for stat in ('median','mean','trim','hl'):
            for cap in (0.4,10):
                R=pseudo(G,stat,cap)
                ws=lambda g: np.average(g.d,weights=g.wt)
                out={k:(round(ws(g),4),int(g.wt.sum())) for k,g in R.groupby('kind')}
                print(f'  {stat:6} cap {cap:4}: all {ws(R):+.4f}', out)
