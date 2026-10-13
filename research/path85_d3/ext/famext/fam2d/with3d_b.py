from rule import *
t=pd.read_pickle(W+'/T.pkl')
G=build_groups(t,unit='cam',cats=('S2','D2','S3','D3'))
ti=t.set_index('qid')
ws=lambda g: np.average(g.d,weights=g.wt)
rows=[]
for gr in G:
    cat_of={}
    for u,mem in gr['members'].items():
        cs=set(ti.loc[[q for q,_ in mem],'category'])
        cat_of[u]='2D' if cs<= {'S2','D2'} else ('3D' if cs<={'S3','D3'} else 'mix')
    u2=[u for u in gr['ul'] if cat_of[u]=='2D']; u3=[u for u in gr['ul'] if cat_of[u]=='3D']
    if len(u2)<2 or not u3: continue
    for j in u2:
        for i in u2:
            if i==j: continue
            ai=gr['ul'][i]
            for cap in (0.25,0.4,10):
                vals=[ai]+[gr['ul'][u] for u in u3]
                pv=pooled_value(vals,0.15,cap,'trimmed')
                rows.append(dict(cap=cap,kind=gr['kind'],wt=len(gr['members'][i]),e_raw=ai-gr['ul'][j],e_pool=(pv if pv is not None else ai)-gr['ul'][j],n3=len(u3)))
R=pd.DataFrame(rows); R['d']=S(R.e_pool)-S(R.e_raw)
for c,g in R.groupby('cap'): print('single 2D unit + 3D votes, cap2',c, f'{ws(g):+.4f}', int(g.wt.sum()), {k:round(ws(x),4) for k,x in g.groupby('kind')})
