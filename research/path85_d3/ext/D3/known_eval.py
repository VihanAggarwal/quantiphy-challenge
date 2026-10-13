"""Measurement only: val-on-test known D3 rows (validation GT on test clips with the same question+prior), suspects excluded."""
import sys, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0,'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/hyp/D3/work')
from harness import *
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
F={'v3':R+'/submissions/trackA_v3_best_per_category.csv','P4':SP+'/hyp/final/D3_main_transfer_fixed.csv',
   'TKP':SP+'/big/scene_graph/D3_TKP_LABfix.csv','T':SP+'/big/scene_graph/D3_T_LABfix.csv','sib':SP+'/big/priors_as_labels/D3_sibling_prior_transfer_ext.csv',
   'cam':SP+'/big/sim3d_camera/D3_camera_consistency.csv','lm':SP+'/big/labmotion/D3_labmotion_direct.csv',
   'merged':SP+'/merge/D3/D3_merged.csv','merged_lm':SP+'/merge/D3/D3_merged_labmotion.csv'}
k=known()
out={}
base=None
for n,p in F.items():
    x=score_csv(p,k)
    if base is None: base=x.set_index('qid').sc
    s=x.set_index('qid')
    lab=s.video_source=='lab'
    d=(s.sc-base.loc[s.index])
    out[n]=dict(n=len(s),all=round(s.sc.mean(),4),lab=round(s.sc[lab].mean(),4),nonlab=round(s.sc[~lab].mean(),4),changed=int((~np.isclose(s.parsed_value,pd.read_csv(F['v3']).set_index('id').parsed_value.loc[s.index])).sum()),sum_delta=round(d.sum(),3))
print(pd.DataFrame(out).T.to_string())
# per-row detail for merged
x=score_csv(F['merged'],k).set_index('qid'); x0=score_csv(F['v3'],k).set_index('qid')
xl=score_csv(F['merged_lm'],k).set_index('qid')
d=pd.DataFrame(dict(vid=x.video_id,gt=x.answer,v3=x0.parsed_value,new=x.parsed_value,s0=x0.sc,s1=x.sc,alt=xl.parsed_value,s2=xl.sc))
pd.set_option('display.width',250)
print(d[~np.isclose(d.v3,d.new)|~np.isclose(d.v3,d.alt)].round(3).to_string())
