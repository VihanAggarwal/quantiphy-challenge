"""Adversarial verification of the s3_perkind S3 variants (measurement only; validation labels never set answers)."""
import sys, json, glob
import numpy as np, pandas as pd
R='/home/user/quantiphy-challenge'
sys.path.insert(0, R)
from qp.mra import item_scores
from qp.data import load_split
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
INV=SP+'/ext/s3_perkind'
t=load_split('test').set_index('qid')
T=pd.read_csv(R+'/data/submission_template/quantiphy_submission_template.csv')
P5=pd.read_csv(R+'/submissions/trackA_probe5_families_merged.csv')
p5=dict(zip(P5.id,P5.parsed_value))
def m1(p,g): return float(item_scores(np.array([p],float),np.array([g],float))[0])
# validation answers on test clips (measurement only)
m=pd.read_csv(SP+'/hyp/S2/val_test_map.csv').sort_values('sim').drop_duplicates('tqid',keep='last')
m=m[m.sim>=0.9]; known=dict(zip(m.tqid,m.answer)); kvid={q:t.loc[q,'video_id'] for q in known}
# proxy groups: same object/quantity across the family (label clip -> rows); defined from the eq3 groups
import pickle
eq=pickle.load(open(SP+'/big/scenegraph/work/eq3.pkl','rb'))
def proxy(q):
    if q in known: return known[q], kvid[q]
    kp=[p for p in eq.get(q,()) if p!=q and p in known and p!=139]
    kv=[known[p] for p in kp]
    if kv and max(kv)/min(kv)<=1.05: return float(np.median(kv)), '+'.join(sorted(set(kvid[p] for p in kp)))
    return None, None
out={}
cols=list(P5.columns)
for f in sorted(glob.glob(INV+'/S3_*.csv')):
    name=f.split('/')[-1][:-4]
    d=pd.read_csv(f)
    fmt=dict(n=len(d), cols_ok=list(d.columns)==cols, ids_match_template=list(d.id)==list(T.id),
             other_cols_identical=bool((d.drop(columns='parsed_value').fillna('')==P5.drop(columns='parsed_value').fillna('')).all().all()),
             finite_pos=bool(np.isfinite(d.parsed_value).all() and (d.parsed_value>0).all()))
    ch=d[d.parsed_value.values!=P5.parsed_value.values]
    fmt['changed']=len(ch); fmt['cats']=t.loc[ch.id,'category'].value_counts().to_dict()
    fmt['lab_rows_changed']=int((t.loc[ch.id,'video_source']=='lab').sum())
    rows=[]
    for q,v in zip(ch.id,ch.parsed_value):
        V,lab=proxy(q)
        rows.append(dict(qid=q,vid=t.loc[q,'video_id'].replace('simulation_',''),q=t.loc[q,'question'][:48],p5=p5[q],new=v,ratio=v/p5[q],
                         V=V,lab=lab,d=(m1(v,V)-m1(p5[q],V)) if V is not None else np.nan))
    E=pd.DataFrame(rows)
    byl=E.dropna(subset=['d']).groupby('lab').d.agg(['count','sum','mean'])
    out[name]=dict(format=fmt, n_proxy=int(E.d.notna().sum()), proxy_sum=round(float(E.d.sum()),2),
                   per_label=byl.round(3).reset_index().to_dict('records'),
                   label_dedup_mean=round(float(byl['mean'].mean()),3) if len(byl) else None)
    if name=='S3_PK_DS':
        pd.set_option('display.width',250); pd.set_option('display.max_rows',100)
        print(E.round(3).to_string())
        E.to_csv(SP+'/ext/s3kp/S3_PK_DS_rows.csv',index=False)
    print(name, json.dumps(out[name]['format']), 'proxy rows',out[name]['n_proxy'],'sum',out[name]['proxy_sum'])
    print(byl.round(3).to_string())
json.dump(out,open(SP+'/ext/s3kp/verify.json','w'),indent=1,default=str)
