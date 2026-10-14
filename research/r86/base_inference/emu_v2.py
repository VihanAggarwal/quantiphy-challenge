import sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/labnoise'); sys.path.insert(0,'/home/user/quantiphy-challenge')
import numpy as np, pandas as pd
from common import tracks, mra_item, ROOT
from qp.data import load_split
import emulate as EM
d = tracks("val_hires")
v = load_split("val_hires").set_index("qid")
runs={'hr1':'runs/val_hr_v1_high/val_hires.csv','hr2':'runs/val_hr_v2_high/val_hires.csv','hr2m':'runs/val_hr_v2_med/val_hires.csv',
      'o854':'runs/val_opus_high/val.csv','v2v':'runs/val_v2_high/val.csv','om2':'runs/val_opus_med2/val.csv','om':'runs/val_opus_med/val.csv'}
R={k:pd.read_csv(ROOT/p).set_index('id') for k,p in runs.items()}
rows=[]
for q,x in sorted(d.items()):
    kind=EM.motion_kind(x["question"])
    if kind is None: continue
    r=dict(qid=q,video=x['video'],kind=kind,answer=float(v.loc[q,'answer']))
    for k,res in R.items():
        a=float(res.loc[q,'direct_value']) if q in res.index else np.nan
        m=EM.row_model(x,a,v.loc[q,'target_unit']) if np.isfinite(a) else None
        f=m['factor'] if m else 1.0
        r[k]=mra_item(a,r['answer']) if np.isfinite(a) else 0; r[k+'_emu']=mra_item(a*f,r['answer']) if np.isfinite(a) else 0; r[k+'_f']=f
    rows.append(r)
df=pd.DataFrame(rows)
df=df[df.kind!='acceleration']
pd.set_option('display.width',250)
print(df[['video','kind','answer']+[k+'_emu' for k in runs]+[k+'_f' for k in ['o854','hr1','hr2']]].round(2).to_string())
print('n',len(df),'clips',df.video.nunique())
print(df[[c for k in runs for c in (k,k+'_emu')]].mean().round(3).to_string())
g=df.groupby('video')[[k+'_emu' for k in runs]].mean().round(3); print(g)
