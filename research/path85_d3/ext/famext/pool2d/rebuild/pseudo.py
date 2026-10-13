from pool import *
from qp.mra import item_scores
t=pd.read_pickle(W+'/T.pkl'); ti=t.set_index('qid')
def S(r): return item_scores(np.exp(np.asarray(r)),np.ones(len(r)))
def run(col='p5', cats=('S2','D2'), minb=3, kinds=('size','speed','acceleration','displacement'), stat='median'):
    eq=groups(t,cats=cats)
    rows=[]
    for c in comps_of(eq):
        g=ti.loc[c]
        kind=g.tkind.iloc[0]
        if kind not in kinds: continue
        per={}
        for q,r in g.iterrows(): per.setdefault(r.base,[]).append(np.log(to_si(ti,q,r[col])))
        bl={b:np.mean(v) for b,v in per.items()}
        if len(bl)<minb: continue
        cat=g.category.iloc[0]
        for j in bl:
            oth={b:v for b,v in bl.items() if b!=j}
            pv=np.median(list(oth.values())) if stat=='median' else np.mean(list(oth.values()))
            for i,ai in oth.items():
                rows.append(dict(grp=c[0],kind=kind,cat=cat,nb=len(bl),e_raw=ai-bl[j],e_pool=pv-bl[j],e_half=0.5*ai+0.5*pv-bl[j]))
    R=pd.DataFrame(rows)
    R['s_raw']=S(R.e_raw); R['s_pool']=S(R.e_pool); R['s_half']=S(R.e_half)
    return R
if __name__=='__main__':
    for stat in ('median','mean'):
        R=run(stat=stat)
        print('stat',stat)
        print(R.groupby(['cat','kind']).agg(pairs=('grp','size'),groups=('grp','nunique'),raw=('s_raw','mean'),pool=('s_pool','mean'),half=('s_half','mean')).round(4))
        # weight each group equally
        G=R.groupby('grp')[['s_raw','s_pool','s_half']].mean()
        print('group-weighted',G.mean().round(4).to_dict())
