from tab import *
import sys
t=pd.read_pickle(W+'/T.pkl').set_index('qid')
K=pd.read_pickle(W+'/known.pkl').set_index('qid')
K['cat']=t.loc[K.index,'category']
K=K[K.cat.isin(['S2','D2'])]
p5=pd.read_csv(R+'/submissions/trackA_probe5_families_merged.csv').set_index('id').parsed_value
for name in sys.argv[1:]:
    for cat in ('S2','D2'):
        f=f'{W}/{name}_{cat}.csv'
        if not os.path.exists(f): continue
        s=pd.read_csv(f).set_index('id').parsed_value
        k=K[K.cat==cat]
        a=item_scores(p5.loc[k.index],k.answer); b=item_scores(s.loc[k.index],k.answer)
        ch=~np.isclose(p5.loc[k.index],s.loc[k.index])
        print(name,cat,'known rows',len(k),'p5 %.4f -> %.4f'%(a.mean(),b.mean()),'changed',int(ch.sum()), [(q,round(p5[q],4),round(s[q],4),k.loc[q,'answer']) for q in k.index[ch]])
