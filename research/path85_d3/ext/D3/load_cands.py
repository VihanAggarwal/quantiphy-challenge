import pandas as pd, numpy as np
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
R='/home/user/quantiphy-challenge'
V3=pd.read_csv(R+'/submissions/trackA_v3_best_per_category.csv')
def cat_of(vt):
    return ('S' if vt[0]=='S' else 'D')+vt[1]
V3['cat']=[i[0]+v[1] for i,v in zip(V3.inference_type,V3.video_type)]
CANDS={
 'P4':SP+'/hyp/final/D3_main_transfer_fixed.csv',
 'TKP':SP+'/big/scene_graph/D3_TKP_LABfix.csv',
 'TP':SP+'/big/scene_graph/D3_TP_LABfix.csv',
 'T':SP+'/big/scene_graph/D3_T_LABfix.csv',
 'sib':SP+'/big/priors_as_labels/D3_sibling_prior_transfer_ext.csv',
 'cam':SP+'/big/sim3d_camera/D3_camera_consistency.csv',
 'lm':SP+'/big/labmotion/D3_labmotion_direct.csv',
}
v3=dict(zip(V3.id,V3.parsed_value))
def load(name):
    d=pd.read_csv(CANDS[name])
    return dict(zip(d.id,d.parsed_value))
