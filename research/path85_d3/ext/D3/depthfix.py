"""Re-solve D3 lab rows whose geometry borrowed target2's depth (flag geo:target_depth_from_target2).
Generic repair (same as the S3 reviewer's fix_depthlink.py): the one depth_info object not claimed by target2 or the prior
is the target's; rename that entry to the target's name and re-solve with the rig camera (84 deg). If no single unclaimed
entry exists (the target has no depth entry at all), route the row to Claude's direct answer."""
import sys, pickle, copy, math
sys.path.insert(0,'/home/user/quantiphy-challenge')
import numpy as np, pandas as pd
from qp.geometry import solve, name_score, DEPTH_MATCH_MIN
from qp.spec import DepthEntry
import qp.combine as C
from qp.spec import KIND_DIM
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
R='/home/user/quantiphy-challenge'
def run_fix(verbose=True):
    d=pickle.load(open(SP+'/hyp/D3/work/lab_test_anns.pkl','rb')); anns=d['anns']; meta=d['meta']; df=d['df'].set_index('qid')
    run=pd.read_csv(R+'/runs/test_v1_high_854/test.csv').set_index('id')
    cand=[q for q in df.index if df.loc[q,'category']=='D3' and str(run.loc[q,'method']).startswith('geometry')
          and 'geo:target_depth_from_target2' in str(run.loc[q,'flags'])]
    out={}
    for q in cand:
        a=anns[q]; vid=df.loc[q,'video_id']; m=meta[vid]
        A0=solve(a.spec,a.tracks,tuple(m['image_size']),float(m['fps']),camera_fov_deg=84.0,seen_scale=float(m.get('scale') or 1.0))
        sp=copy.deepcopy(a.spec)
        claimers=list(sp.target.objects[1:2])+list(sp.prior.objects or [])
        objs=list(dict.fromkeys(e.object for e in sp.depth))
        unclaimed=[o for o in objs if max((name_score(c,o) for c in claimers),default=0)<DEPTH_MATCH_MIN]
        rec=dict(qid=q,vid=vid,kind=sp.target.kind,tobj=list(sp.target.objects),depth_objs=objs,unclaimed=unclaimed,
                 run_geo=run.loc[q,'geo_value'],resolve0=A0.value,direct=run.loc[q,'direct_value'])
        if len(unclaimed)==1:
            sp.depth=[DepthEntry(object=(sp.target.objects[0] if e.object==unclaimed[0] else e.object),distance_m=e.distance_m,time=e.time) for e in sp.depth]
            A=solve(sp,a.tracks,tuple(m['image_size']),float(m['fps']),camera_fov_deg=84.0,seen_scale=float(m.get('scale') or 1.0))
            bad={'target_depth_from_target2','target_depth_from_prior','target_depth_scene_median'}&set(A.flags)
            rec.update(new_geo=A.value,new_flags=';'.join(sorted(A.flags)),dt=A.debug.get('depth_target'),dt2=A.debug.get('depth_target2'))
            if not bad and A.value is not None and np.isfinite(A.value) and A.value>0:
                rec.update(value=float(A.value),how='resolved_with_target_depth')
            else:
                rec.update(value=float(rec['direct']),how='direct (re-solve still assumed a depth)')
        else:
            rec.update(new_geo=np.nan,value=float(rec['direct']),how='direct (target has no depth entry of its own)')
        out[q]=rec
    return pd.DataFrame(out.values())
if __name__=='__main__':
    pd.set_option('display.width',320); pd.set_option('display.max_colwidth',60)
    X=run_fix()
    print(X.drop(columns=['new_flags']).round(3).to_string())
    print(X[['qid','new_flags','dt','dt2']].to_string())
