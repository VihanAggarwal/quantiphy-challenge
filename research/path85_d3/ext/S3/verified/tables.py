import sys, pickle, re
sys.path.insert(0,'/home/user/quantiphy-challenge')
import pandas as pd, numpy as np
from qp.data import load_split
R='/home/user/quantiphy-challenge'; SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
t=load_split('test').set_index('qid')
K=pickle.load(open(SP+'/merge/S3/known_all.pkl','rb'))
v3=pd.read_csv(R+'/submissions/trackA_v3_best_per_category.csv').set_index('id').parsed_value
P4=pd.read_csv(R+'/submissions/trackA_probe4_s2twin_d2refineoff_s3split_d3fixes.csv').set_index('id').parsed_value
M=pd.read_csv(SP+'/merge/S3/S3_merged.csv').set_index('id').parsed_value
TL=pd.read_csv(SP+'/big/scene_graph/S3_T_LABfix.csv').set_index('id').parsed_value
run=pd.read_csv(R+'/runs/test_v1_high_854/test.csv').set_index('id')
pat=sys.argv[1]
x=t[(t.video_source=='lab')&t.question.str.contains(pat,case=False)]
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',60); pd.set_option('display.max_rows',400)
out=pd.DataFrame(dict(vid=x.video_id,cat=x.category,q=x.question.str[:55],prior=x.prior.str[:40],v3=v3[x.index],P4=P4[x.index],TL=TL[x.index],M=M[x.index],
   geo=run.loc[x.index,'geo_value'] if 'geo_value' in run else np.nan, direct=run.loc[x.index,'direct_value'] if 'direct_value' in run else np.nan,
   gt=[K.get(q,np.nan) for q in x.index]))
print(out.round(3).to_string())
