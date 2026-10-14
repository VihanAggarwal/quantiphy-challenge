import sys, pandas as pd, numpy as np
sys.path.insert(0,'/home/user/quantiphy-challenge')
from qp.data import load_validation
from qp.mra import item_scores
v = load_validation().set_index('qid')
runs = {'opus_high_854':'runs/val_opus_high/val.csv','opus_med':'runs/val_opus_med/val.csv','opus_med2':'runs/val_opus_med2/val.csv',
        'v2_high_val':'runs/val_v2_high/val.csv','fable':'runs/val_fable_high/val.csv',
        'hr_v1_high':'runs/val_hr_v1_high/val_hires.csv','hr_v2_high':'runs/val_hr_v2_high/val_hires.csv','hr_v2_med':'runs/val_hr_v2_med/val_hires.csv'}
src = v.video_source.replace({'segmentation':'simulation'})
grp = v.category.str[1] + '_' + src.where(~((v.category.str[1]=='3')&(src!='lab')),'sim')
grp = np.where(v.category.str[1]=='2', '2D', np.where(src=='lab','3Dlab','3Dsim'))
v['grp']=grp
rows=[]
for nm,p in runs.items():
    try: d=pd.read_csv(p).set_index('id')
    except Exception as e: print(nm,e); continue
    for col in ('parsed_value','direct_value','geo_value'):
        s = pd.Series(item_scores(d[col].reindex(v.index), v.answer), index=v.index)
        r={'run':nm,'col':col}
        for g in ['2D','3Dlab','3Dsim']:
            r[g]=round(s[v.grp==g].mean(),3)
        for c in ['S2','D2','S3','D3']: r[c]=round(s[v.category==c].mean(),3)
        r['n']=int(d[col].reindex(v.index).notna().sum())
        rows.append(r)
print(pd.DataFrame(rows).to_string())
print(v.grp.value_counts())
