import pandas as pd, numpy as np, glob, sys
sys.path.insert(0,'/home/user/quantiphy-challenge')
from qp.data import load_split
R='/home/user/quantiphy-challenge'
t=load_split('test').set_index('qid')
tmpl=glob.glob(R+'/data/submission_template/*')
print(tmpl)
T=pd.read_csv([f for f in tmpl if f.endswith('.csv')][0])
print(T.columns.tolist(), len(T))
P5=pd.read_csv(R+'/submissions/trackA_probe5_families_merged.csv')
for f in sorted(glob.glob('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ext/s3_perkind/S3_*.csv')):
    d=pd.read_csv(f)
    ok_cols=list(d.columns)==['id','parsed_value']
    ids_ok=list(d.id)==list(T.iloc[:,0]) or set(d.id)==set(T.iloc[:,0])
    v=pd.to_numeric(d.parsed_value,errors='coerce').values
    fin=np.isfinite(v).all() and (v>0).all()
    m=d.merge(P5,on='id',suffixes=('','_p5'))
    ch=m[~np.isclose(m.parsed_value,m.parsed_value_p5,rtol=1e-12,atol=0)]
    cats=t.loc[ch.id,'category'].value_counts().to_dict()
    src=t.loc[ch.id,'video_source'].value_counts().to_dict()
    print(f.split('/')[-1], ok_cols, len(d), d.id.is_unique, ids_ok, fin, len(ch), cats, src, 'exact-diff', int((m.parsed_value!=m.parsed_value_p5).sum()))
