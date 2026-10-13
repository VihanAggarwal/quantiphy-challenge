import sys, pickle
sys.path.insert(0,'/home/user/quantiphy-challenge')
import pandas as pd, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_rows',500); pd.set_option('display.max_colwidth',60)
R='/home/user/quantiphy-challenge'; SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
S=pickle.load(open(SP+'/merge/S3/sg_state.pkl','rb'))
t=S['t']; ti=t.set_index('qid'); why=S['why']
v3=pd.read_csv(R+'/submissions/trackA_v3_best_per_category.csv').set_index('id').parsed_value
F={'P4':SP+'/hyp/final/S3_split_full_depthfix.csv','TL':SP+'/big/scene_graph/S3_T_LABfix.csv','SIB':SP+'/big/priors_as_labels/S3_sibling_prior_transfer_noconflict.csv'}
D={k:pd.read_csv(f).set_index('id').parsed_value for k,f in F.items()}
run=pd.read_csv(R+'/runs/test_v1_high_854/test.csv').set_index('id')
v2=pd.read_csv(R+'/submissions/trackA_opus55_high_v2.csv').set_index('id').parsed_value
s3=ti[ti.category=='S3'].index
rows=[]
for q in s3:
    vals={k:D[k][q] for k in D}
    chg={k:not np.isclose(vals[k],v3[q],rtol=1e-9) for k in D}
    if not any(chg.values()): continue
    r=ti.loc[q]
    rows.append(dict(qid=q,vid=r.video_id,src=r.video_source,tkind=r.tkind,tobj=r.tobj,tdim=r.tdim,q=r.question[:70],prior=str(r.prior)[:50],v3=v3[q],P4=vals['P4'] if chg['P4'] else np.nan,TL=vals['TL'] if chg['TL'] else np.nan,SIB=vals['SIB'] if chg['SIB'] else np.nan,
       tlwhy=why.get(q,''),geo=run.loc[q,'geo_value'],dirv=run.loc[q,'direct_value'],meth=run.loc[q,'method'],flags=str(run.loc[q,'flags'])[:60],v2=v2[q]))
X=pd.DataFrame(rows)
X.to_pickle(SP+'/merge/S3/changed.pkl')
print(len(X))
print(X.groupby(['src',X.P4.notna(),X.TL.notna(),X.SIB.notna()]).size())
