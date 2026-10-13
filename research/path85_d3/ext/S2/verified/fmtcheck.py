import sys, numpy as np, pandas as pd
sys.path.insert(0,'/home/user/quantiphy-challenge')
from qp.data import load_split
R='/home/user/quantiphy-challenge'
t=load_split('test').set_index('qid')
v3=pd.read_csv(R+'/submissions/trackA_v3_best_per_category.csv')
v2=pd.read_csv(R+'/submissions/trackA_opus55_high_v2.csv')
p4=pd.read_csv(R+'/submissions/trackA_probe4_s2twin_d2refineoff_s3split_d3fixes.csv')
m=pd.read_csv(sys.argv[1])
print('cols',list(m.columns),'n',len(m),'unique',m.id.nunique())
print('same order as v3', (m.id.values==v3.id.values).all(), 'as v2',(m.id.values==v2.id.values).all())
# template? check sample_submission
import glob
print(glob.glob(R+'/data/QuantiPhy/*.csv')[:5], glob.glob(R+'/**/*sample*',recursive=False))
x=m.parsed_value.values.astype(float)
print('finite',np.isfinite(x).all(),'pos',(x>0).all(), 'dtype', m.parsed_value.dtype)
cat=t.loc[m.id.values,'category'].values
d=~np.isclose(x,v3.parsed_value.values,rtol=1e-12,atol=0)
print('diff vs v3 by cat', pd.Series(cat[d]).value_counts().to_dict())
dp=~np.isclose(x,p4.parsed_value.values,rtol=1e-12,atol=0)
print('diff vs p4 S2 rows', (dp&(cat=='S2')).sum(), m.id.values[dp&(cat=='S2')])
print('S2 total', (cat=='S2').sum())
# raw text check
raw=open(sys.argv[1]).read().splitlines()
print(raw[:3], raw[-1])
bad=[l for l in raw[1:] if l.count(',')!=1]
print('bad lines',len(bad))
