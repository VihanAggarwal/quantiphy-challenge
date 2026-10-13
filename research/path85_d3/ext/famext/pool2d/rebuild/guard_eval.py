from rule import *
t=pd.read_pickle(W+'/T.pkl'); ti=t.set_index('qid')
ws=lambda g: np.average(g.d,weights=g.wt) if len(g) else np.nan
def pv_guard(vals,tau,cap2,smax,n_small=3):
    vals=list(vals)
    if len(vals)<=n_small and len(vals)>=2 and (max(vals)-min(vals))>smax: return None
    return pooled_value(vals,tau,cap2,'trimmed')
for cats,label in ((('S2','D2'),'2D votes'),(('S2','D2','S3','D3'),'2D+3D votes')):
    G=build_groups(t,unit='cam',cats=cats)
    for smax in (0.25,0.35,0.5,10):
        rows=[]
        for gr in G:
            cat_of={}
            for u,mem in gr['members'].items():
                cs=set(ti.loc[[q for q,_ in mem],'category']); cat_of[u]='2D' if cs<={'S2','D2'} else '3D'
            u2=[u for u in gr['ul'] if cat_of[u]=='2D']
            if len(u2)<2: continue
            for j in u2:    # held-out 2D camera = pseudo truth
                oth=[u for u in gr['ul'] if u!=j]
                if not [u for u in oth if cat_of[u]=='2D']: continue
                pv=pv_guard([gr['ul'][u] for u in oth],0.15,0.3,smax)
                for i in oth:
                    if cat_of[i]!='2D': continue
                    ai=gr['ul'][i]
                    rows.append(dict(kind=gr['kind'],wt=len(gr['members'][i]),e_raw=ai-gr['ul'][j],e_pool=(pv if pv is not None else ai)-gr['ul'][j],ch=pv is not None))
        Rr=pd.DataFrame(rows); Rr['d']=S(Rr.e_pool)-S(Rr.e_raw)
        print(f'{label:12} smax {smax:5}: per-row gain {ws(Rr):+.4f} (pairs wt {int(Rr.wt.sum())}, changed wt {int(Rr[Rr.ch].wt.sum())})', {k:round(ws(x),4) for k,x in Rr.groupby('kind')})
