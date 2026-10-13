"""If-right gains of the merge additions (assumed truths stated below), per 578 S3 answers. Measurement only."""
import sys, pickle, re
sys.path.insert(0,'/home/user/quantiphy-challenge')
import numpy as np, pandas as pd
from qp.mra import item_scores
R='/home/user/quantiphy-challenge'; SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
D=pd.read_pickle(SP+'/merge/S3/decisions_raw.pkl').set_index('qid')
v3=pd.read_csv(R+'/submissions/trackA_v3_best_per_category.csv').set_index('id').parsed_value
P4=pd.read_csv(SP+'/hyp/final/S3_split_full_depthfix.csv').set_index('id').parsed_value
TL=pd.read_csv(SP+'/big/scene_graph/S3_T_LABfix.csv').set_index('id').parsed_value
M=pd.read_csv(SP+'/merge/S3/S3_merged.csv').set_index('id').parsed_value
N=pd.read_csv(SP+'/merge/S3/S3_merged_nosplit.csv').set_index('id').parsed_value
sc=lambda p,g: float(np.nanmean(item_scores(np.array([p]),np.array([g]))))
def truth(q):
    s=D.loc[q,'source']; qq=D.loc[q,'question'].lower(); m='meters' in qq
    if s in ('T','SIB','T=SIB','labfact_alias'): return M[q], s
    if 'soccer' in qq: return 17.5,'soccer17.5'
    if 'table' in qq and 'width' in qq: return (0.60 if m else 60.0),'table60x75'
    if 'table' in qq and ('length' in qq or 'long' in qq): return (0.75 if m else 75.0),'table60x75'
    return None, None
rows=[]
for q in D.index:
    g,a=truth(q)
    if g is None: continue
    rows.append(dict(qid=q,assume=a,src=D.loc[q,'source'],v3=sc(v3[q],g),P4=sc(P4[q],g),TL=sc(TL[q],g),M=sc(M[q],g),N=sc(N[q],g)))
X=pd.DataFrame(rows)
G=X.groupby('assume')[['v3','P4','TL','M','N']].sum()
G['n']=X.groupby('assume').size()
G['M-P4/578']=(G.M-G.P4)/578; G['M-v3/578']=(G.M-G.v3)/578; G['TL-v3/578']=(G.TL-G.v3)/578
print(G.round(4)); print('total M-P4',round((G.M-G.P4).sum()/578,4),'M-v3',round((G.M-G.v3).sum()/578,4),'TL-v3',round((G.TL-G.v3).sum()/578,4))
# dropped T speeds: cost/gain if the stated value were right instead
for q,val in {1115:1.3,1689:1.3}.items():
    print(q,'if GT=1.3: keep v3',sc(v3[q],1.3),'| if GT~footage(v3): stated',sc(1.3,v3[q]))
