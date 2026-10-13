import sys
sys.path.insert(0,'/home/user/quantiphy-challenge')
import pandas as pd, numpy as np
from qp.data import load_split
R='/home/user/quantiphy-challenge'; SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
t=load_split('test'); tq=t.set_index('qid')
v3=pd.read_csv(R+'/submissions/trackA_v3_best_per_category.csv')
F={'P4':SP+'/hyp/final/S3_split_full_depthfix.csv','TL':SP+'/big/scene_graph/S3_T_LABfix.csv','SIB':SP+'/big/priors_as_labels/S3_sibling_prior_transfer_noconflict.csv'}
D={}
for k,f in F.items():
    d=pd.read_csv(f); print(k,len(d),list(d.columns), (d.id.values==v3.id.values).all())
    D[k]=d.set_index('id').parsed_value
b=v3.set_index('id').parsed_value
ch={k:set(b.index[~np.isclose(D[k].values,b.values,rtol=1e-9)]) for k in D}
for k in ch: print(k,len(ch[k]), tq.loc[sorted(ch[k]),'category'].value_counts().to_dict(), tq.loc[sorted(ch[k]),'video_source'].value_counts().to_dict())
ks=list(ch)
for i in range(3):
    for j in range(i+1,3):
        o=ch[ks[i]]&ch[ks[j]]; same=sum(np.isclose(D[ks[i]][q],D[ks[j]][q],rtol=1e-6) for q in o)
        print(ks[i],ks[j],len(o),same)
print('union',len(set.union(*ch.values())))
