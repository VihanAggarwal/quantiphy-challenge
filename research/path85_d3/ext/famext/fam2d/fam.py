from tab import *
F=json.load(open(SP+'/big/scenegraph/families.json'))
def fammap():
    m={}
    for k,v in F['series_families'].items():
        for b in v['bases']: m[b]=k
    return m
def scenmap():
    m={}
    for k,v in F['scenarios'].items():
        for vid in v: m[vid]=k
    return m
if __name__=='__main__':
    t=pd.read_pickle(W+'/T.pkl')
    fm=fammap(); t['fam']=t.base.map(fm)
    sm=scenmap(); t['scen']=t.video_id.map(sm)
    t.to_pickle(W+'/T.pkl')
    t2=t[t.category.isin(['S2','D2'])]
    print('2D q in families', t2.fam.notna().sum(), 'of', len(t2))
    g=t[t.fam.notna()].groupby('fam')
    for k,gg in g:
        c=gg.category.value_counts().to_dict()
        if not (c.get('S2',0)+c.get('D2',0)): continue
        print(k, c, sorted(gg.video_id.unique()))
