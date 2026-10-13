import pandas as pd, numpy as np
T=pd.read_csv('/home/user/quantiphy-challenge/data/submission_template/quantiphy_submission_template.csv')
v3=pd.read_csv('/home/user/quantiphy-challenge/submissions/trackA_v3_best_per_category.csv')
print(T.shape, list(T.columns))
for f in ['../S3_merged.csv','../S3_merged_nosplit.csv','../S3_merged_noalias.csv']:
    d=pd.read_csv(f)
    print(f, list(d.id)==list(T.id), set(d.id)==set(T.id))
    for c in T.columns:
        if c=='parsed_value': continue
        same=(d[c].astype(str)==T[c].astype(str)).all()
        if not same: print('  col differs from template', c, (d[c].astype(str)!=T[c].astype(str)).sum())
    for c in v3.columns:
        if c=='parsed_value': continue
        if not (d[c].astype(str)==v3[c].astype(str)).all(): print('  col differs from v3', c)
    print('  dtype', d.parsed_value.dtype, d.parsed_value.min(), d.parsed_value.max())
