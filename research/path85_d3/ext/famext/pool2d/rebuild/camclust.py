from tab import *
def camera_clusters(t, thr=0.6, rthr=0.95):
    P=pd.read_pickle(W+'/pairs_edge.pkl').merge(pd.read_pickle(W+'/pairs_ncc.pkl'),on=['fam','a','b'])
    parent={}
    def f(x):
        parent.setdefault(x,x)
        while parent[x]!=x:
            parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def u(a,b): parent[f(a)]=f(b)
    for v in t.video_id.unique(): f(v)
    for v in t.video_id.unique():
        if v.endswith('_segmented'):
            o=v[:-len('_segmented')]
            if o in parent: u(v,o)
    for r in P.itertuples():
        if 'segmented' in r.a or 'segmented' in r.b: continue
        if r.encc>=thr or (r.ancc>=rthr and r.amad<=3): u(r.a,r.b)
    return {v:f(v) for v in t.video_id.unique()}
if __name__=='__main__':
    t=pd.read_pickle(W+'/T.pkl')
    cc=camera_clusters(t); t['cam']=t.video_id.map(cc)
    t.to_pickle(W+'/T.pkl')
    g=t[t.fam.notna()].drop_duplicates('video_id')
    for fam,gg in g.groupby('fam'):
        cl=gg.groupby('cam').video_id.apply(lambda x: ','.join(sorted(v.replace('simulation_','s').replace('_segmented','S') for v in x)))
        if gg.category.isin(['S2','D2']).any(): print(fam, len(cl), list(cl.values))
