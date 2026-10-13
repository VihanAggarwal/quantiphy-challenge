from pool2 import *
def robust(v, tau=0.2, mode='trimmed'):
    v=np.asarray(v,float)
    m=np.median(v)
    if mode=='median': return float(m)
    keep=v[np.abs(v-m)<=tau]
    return float(np.mean(keep)) if len(keep) else float(m)
def pooled_value(ul_vals, tau=0.2, cap2=0.25, mode='trimmed'):
    """None = no change"""
    v=list(ul_vals)
    if len(v)<2: return None
    if len(v)==2:
        if abs(v[0]-v[1])>cap2: return None
        return float(np.mean(v))
    return robust(v,tau,mode)
def pseudo_rule(G, tau=0.2, cap2=0.25, mode='trimmed', minu=3):
    rows=[]
    for gr in G:
        ul=gr['ul']
        if len(ul)<minu: continue
        for j in ul:
            oth={u:v for u,v in ul.items() if u!=j}
            pv=pooled_value(oth.values(),tau,cap2,mode)
            for i,ai in oth.items():
                n=len(gr['members'][i])
                e_pool=(pv if pv is not None else ai)-ul[j]
                rows.append(dict(kind=gr['kind'],grp=gr['grp'],wt=n,e_raw=ai-ul[j],e_pool=e_pool,nu=len(oth)))
    R=pd.DataFrame(rows); R['d']=S(R.e_pool)-S(R.e_raw); return R
if __name__=='__main__':
    t=pd.read_pickle(W+'/T.pkl')
    G=build_groups(t,unit='cam')
    ws=lambda g: np.average(g.d,weights=g.wt)
    for mode in ('median','trimmed'):
        for tau in (0.1,0.15,0.2,0.3,10):
            if mode=='median' and tau!=0.2: continue
            for cap2 in (0.15,0.25,0.4):
                R=pseudo_rule(G,tau,cap2,mode)
                R2=R[R.nu==2]; R3=R[R.nu>=3]
                print(f'{mode:8} tau {tau:4} cap2 {cap2}: all {ws(R):+.4f} (n={int(R.wt.sum())})  2-unit pools {ws(R2):+.4f} (n={int(R2.wt.sum())})  >=3-unit pools {ws(R3):+.4f} (n={int(R3.wt.sum())})', {k:round(ws(g),4) for k,g in R.groupby('kind')})
