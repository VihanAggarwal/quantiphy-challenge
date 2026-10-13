from pool import *
from qp.mra import item_scores
t=pd.read_pickle(W+'/T.pkl'); ti=t.set_index('qid')
def S(r): return item_scores(np.exp(np.asarray(r,float)),np.ones(len(r)))
eq=groups(t,cats=('S2','D2'))
G=[]
for c in comps_of(eq):
    g=ti.loc[c]; kind=g.tkind.iloc[0]
    if kind not in ('size','speed','acceleration','displacement'): continue
    per={}
    for q,r in g.iterrows(): per.setdefault(r.base,[]).append(np.log(to_si(ti,q,r.p5)))
    bl={b:np.mean(v) for b,v in per.items()}
    nrows={b:len(v) for b,v in per.items()}
    G.append(dict(grp=c[0],kind=kind,cat=g.category.iloc[0],bl=bl,nrows=nrows,spread=max(bl.values())-min(bl.values())))
def agg(vals,stat):
    v=np.asarray(vals)
    if stat=='median': return np.median(v)
    if stat=='mean': return np.mean(v)
    if stat=='trim':  # mean after dropping farthest-from-median if n>=4
        if len(v)>=4:
            m=np.median(v); v=v[np.argsort(np.abs(v-m))][:-1]
        return np.mean(v)
def evaluate(cap, stat, minb=3, w=0.0):
    rows=[]
    for gr in G:
        bl=gr['bl']
        if len(bl)<minb: continue
        if gr['spread']>cap: continue
        for j in bl:
            oth={b:v for b,v in bl.items() if b!=j}
            if len(oth)<2: continue
            pv=agg(list(oth.values()),stat)
            for i,ai in oth.items():
                rows.append(dict(kind=gr['kind'],grp=gr['grp'],e_raw=ai-bl[j],e_pool=w*ai+(1-w)*pv-bl[j],wt=gr['nrows'][i]))
    R=pd.DataFrame(rows)
    if not len(R): return None
    R['d']=(S(R.e_pool)-S(R.e_raw))
    return R
print('pseudo-truth LOO (truth = a held-out base), D2+S2 groups with >=3 bases; d = mean score change per pair')
for cap in (0.15,0.25,0.4,0.7,10):
    for stat in ('median','mean','trim'):
        R=evaluate(cap,stat)
        out={k:(round(g.d.mean(),4),len(g)) for k,g in R.groupby('kind')}
        print(f'cap {cap:5} {stat:6} all {R.d.mean():+.4f} n={len(R)}', out)
