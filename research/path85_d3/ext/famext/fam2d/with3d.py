from rule import *
t=pd.read_pickle(W+'/T.pkl')
G=build_groups(t,unit='cam',cats=('S2','D2','S3','D3'))
ti=t.set_index('qid')
ws=lambda g: np.average(g.d,weights=g.wt)
rows=[]
for gr in G:
    # split units into 2D-only and 3D-only units (unit = camera; a camera cluster can't mix 2D and 3D clips? check)
    cat_of={}
    for u,mem in gr['members'].items():
        cs=set(ti.loc[[q for q,_ in mem],'category'])
        cat_of[u]='2D' if cs<= {'S2','D2'} else ('3D' if cs<={'S3','D3'} else 'mix')
    u2=[u for u in gr['ul'] if cat_of[u]=='2D']; u3=[u for u in gr['ul'] if cat_of[u]=='3D']
    if len(u2)<2: continue
    for j in u2:
        o2=[u for u in u2 if u!=j]
        for mode in ('2d','2d3d'):
            us=o2+(u3 if mode=='2d3d' else [])
            pv=pooled_value([gr['ul'][u] for u in us],0.15,0.25,'trimmed')
            for i in o2:
                ai=gr['ul'][i]
                rows.append(dict(mode=mode,kind=gr['kind'],wt=len(gr['members'][i]),e_raw=ai-gr['ul'][j],e_pool=(pv if pv is not None else ai)-gr['ul'][j],n3=len(u3)))
R=pd.DataFrame(rows); R['d']=S(R.e_pool)-S(R.e_raw)
for m,g in R.groupby('mode'):
    print(m, f'{ws(g):+.4f}', int(g.wt.sum()), {k:round(ws(x),4) for k,x in g.groupby('kind')}, ' rows with 3D votes available:', int(g[g.n3>0].wt.sum()), f'{ws(g[g.n3>0]):+.4f}')
