"""MEASUREMENT ONLY: val GT mapped onto test rows (all renders). Never used to set answers."""
import sys, pickle
sys.path.insert(0,'/home/user/quantiphy-challenge')
import numpy as np, pandas as pd
from qp.mra import item_scores
from qp.data import load_split
R='/home/user/quantiphy-challenge'; SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
K=pickle.load(open(SP+'/merge/S3/known_all.pkl','rb'))
t=load_split('test').set_index('qid')
F={'v3':R+'/submissions/trackA_v3_best_per_category.csv','P4':SP+'/hyp/final/S3_split_full_depthfix.csv',
   'TL':SP+'/big/scene_graph/S3_T_LABfix.csv','SIB':SP+'/big/priors_as_labels/S3_sibling_prior_transfer_noconflict.csv',
   'merged':SP+'/merge/S3/S3_merged.csv','nosplit':SP+'/merge/S3/S3_merged_nosplit.csv','noalias':SP+'/merge/S3/S3_merged_noalias.csv'}
V={k:pd.read_csv(f).set_index('id').parsed_value for k,f in F.items()}
q=[x for x in K if t.loc[x,'category']=='S3']
def sc(p,g): return float(np.nanmean(item_scores(np.array([p]),np.array([g]))))
rows=[]
for x in q:
    r=dict(qid=x,vid=t.loc[x,'video_id'],src=t.loc[x,'video_source'],gt=K[x])
    for k in V: r[k]=V[k][x]; r['s_'+k]=sc(V[k][x],K[x])
    rows.append(r)
D=pd.DataFrame(rows)
print('n',len(D)); print(D.groupby('src')[[c for c in D if c.startswith('s_')]].mean().round(3)); print(D[[c for c in D if c.startswith('s_')]].mean().round(4))
ch=D[~np.isclose(D.merged,D.v3)|~np.isclose(D.P4,D.v3)|~np.isclose(D.TL,D.v3)]
pd.set_option('display.width',250)
print(ch[['qid','vid','gt','v3','P4','TL','merged','nosplit','s_v3','s_P4','s_TL','s_merged','s_nosplit']].round(3).to_string())
