import sys, pickle, re
sys.path.insert(0,'/home/user/quantiphy-challenge')
import pandas as pd, numpy as np
R='/home/user/quantiphy-challenge'; SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
S=pickle.load(open(SP+'/merge/S3/sg_state.pkl','rb')); t=S['t']; ti=t.set_index('qid')
v3=pd.read_csv(R+'/submissions/trackA_v3_best_per_category.csv').set_index('id').parsed_value
p4=pd.read_csv(SP+'/hyp/final/S3_split_full_depthfix.csv').set_index('id').parsed_value
df=pd.read_csv(SP+'/hyp/S3/variants_labdirect/S3p3_direct_full.csv').set_index('id').parsed_value
sf=pd.read_csv(SP+'/hyp/S3/variants_labdirect/S3p3_split_full.csv').set_index('id').parsed_value
specs=pickle.load(open(SP+'/hyp/S3/work/specs.pkl','rb'))
s3=ti.index[ti.category=='S3']
kind=pd.Series({q:(specs[q].target.kind if q in specs else '?') for q in s3})
print('tkind vs specs kind agree:', (kind==ti.loc[s3,'tkind']).mean())
d=s3[~np.isclose(p4[s3],df[s3],rtol=1e-9)]
print('P4 vs direct_full differ:',len(d), ti.loc[d,'video_source'].value_counts().to_dict(), kind[d].value_counts().to_dict())
d2=s3[~np.isclose(p4[s3],sf[s3],rtol=1e-9)]
print('P4 vs split_full (depthfix rows):',list(d2), [ (sf[q],p4[q]) for q in d2])
c=s3[~np.isclose(df[s3],v3[s3],rtol=1e-9)]
print('direct_full vs v3:',len(c), ti.loc[c,'video_source'].value_counts().to_dict())
lab=s3[ti.loc[s3,'video_source']=='lab']
print('S3 lab kinds', kind[lab].value_counts().to_dict())
sz=[q for q in lab if kind[q]=='size']
print('S3 lab size qs', len(sz))
for q in sz:
    if re.search('ping|white ball|ball',ti.loc[q,'question'],re.I): print(q, ti.loc[q,'video_id'], ti.loc[q,'question'], v3[q], p4[q])
