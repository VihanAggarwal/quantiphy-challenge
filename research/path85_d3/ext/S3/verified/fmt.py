import sys
sys.path.insert(0,'/home/user/quantiphy-challenge')
import numpy as np, pandas as pd
from qp.data import load_split
R='/home/user/quantiphy-challenge'; SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
t=load_split('test').set_index('qid')
v3=pd.read_csv(R+'/submissions/trackA_v3_best_per_category.csv')
tmpl=None
import glob
print(glob.glob(R+'/data/QuantiPhy/*.csv')[:5], glob.glob(R+'/submissions/*templ*'))
for f in sys.argv[1:]:
    d=pd.read_csv(f)
    print(f.split('/')[-1], d.shape, list(d.columns))
    assert list(d.columns)==list(v3.columns)
    assert list(d.id)==list(v3.id), 'id order'
    v=d.parsed_value.astype(float).values
    print(' finite', np.isfinite(v).all(), 'pos', (v>0).all(), 'nunique id', d.id.nunique())
    ch=~np.isclose(v, v3.parsed_value.values, rtol=1e-9, atol=0)
    cats=t.loc[d.id[ch],'category'].value_counts().to_dict()
    print(' changed', ch.sum(), cats, 'median ratio', np.median(v[ch]/v3.parsed_value.values[ch]))
    S3=(t.loc[d.id,'category']=='S3').values
    print(' S3 rows', S3.sum())
