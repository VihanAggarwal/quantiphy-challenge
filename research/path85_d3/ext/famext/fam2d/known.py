from tab import *
def norm(q):
    q=re.sub(r'(\d+)\.0+(?!\d)',r'\1',str(q).lower()); return re.sub(r'[^a-z0-9.]','',q)
def known(t):
    v=load_split('val_hires')
    v['k']=v.video_id+'|'+v.question.map(norm)+'|'+v.prior.map(norm)
    t=t.copy(); t['k']=t.video_id+'|'+t.question.map(norm)+'|'+t.prior.map(norm)
    m=t.merge(v[['k','answer','qid']].rename(columns={'qid':'vqid'}),on='k',how='inner')
    return m
if __name__=='__main__':
    t=pd.read_pickle(W+'/T.pkl')
    m=known(t)
    print(len(m), m.category.value_counts().to_dict())
    m[['qid','vqid','answer']].to_pickle(W+'/known.pkl')
    m2=m[m.category.isin(['S2','D2'])]
    for c in ['S2','D2']:
        g=m2[m2.category==c]
        print(c, len(g), 'p5', item_scores(g.p5,g.answer).mean().round(4), 'fam', g.fam.notna().sum())
    print(m2[m2.fam.notna()][['qid','vqid','video_id','category','question','prior','p5','answer']].to_string())
