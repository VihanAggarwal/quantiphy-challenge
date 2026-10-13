"""Verifier PROPOSAL (not an investigator variant): S3_PK_DS + the scene-family T rule restored for the 0026 person speed.
Rule (model-free, test inputs only): an S3 sim question takes a family clip's stated prior when transfers3 links them by
motion_depth_identical (identical timed depth entries for that object) - here 'speed of the person = 1.3m/s' stated by
simulation_0025, whose human depth entries (114.8319 m -> 114.8356 m) are identical to simulation_0026(_segmented).
Probe 5's S3 merge dropped this T on footage grounds; 0025's own stated GT is 1.3 while the same footage method gives 0.33-0.57,
so the footage estimate is the unreliable one. Validation answers are not used to set anything."""
import pandas as pd, numpy as np, sys
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
R='/home/user/quantiphy-challenge'
A=pd.read_pickle(SP+'/big/scenegraph/work/transfers3.pkl'); A=A[~A.conflict]
base=pd.read_csv(SP+'/ext/s3_perkind/S3_PK_DS.csv')
P5=pd.read_csv(R+'/submissions/trackA_probe5_families_merged.csv')
sel=A[(A.why=='motion_depth_identical')&(A.cat=='S3')]
new=base.set_index('id').parsed_value.copy()
ch={}
for r in sel.itertuples():
    cur=new[r.qid]
    if np.isclose(cur,r.value): continue
    ch[r.qid]=(cur,r.value,r.video_id,r.line)
    new[r.qid]=r.value
print(ch)
out=base.copy(); out['parsed_value']=out.id.map(new)
assert len(out)==3289 and list(out.id)==list(P5.id) and np.isfinite(out.parsed_value).all() and (out.parsed_value>0).all()
out.to_csv('S3_PK_DS_T0026.csv',index=False)
d=out.parsed_value.values!=P5.parsed_value.values
print('changed vs probe5:',int(d.sum()),'vs S3_PK_DS:',int((out.parsed_value.values!=base.parsed_value.values).sum()))
