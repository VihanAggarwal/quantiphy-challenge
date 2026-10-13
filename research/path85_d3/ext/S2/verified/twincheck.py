import sys, importlib.util, numpy as np, pandas as pd
sys.path.insert(0,'/home/user/quantiphy-challenge')
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
spec=importlib.util.spec_from_file_location('segtwin_rule', SP+'/hyp/S2/t2/segtwin.py')
seg=importlib.util.module_from_spec(spec); spec.loader.exec_module(seg)
tt=seg.t.set_index('qid')
v3=pd.read_csv('/home/user/quantiphy-challenge/submissions/trackA_v3_best_per_category.csv').set_index('id').parsed_value
m=pd.read_csv(sys.argv[1]).set_index('id').parsed_value
o=tt[~tt.video_id.str.endswith('_segmented')]
key={(r.twin,r.nq,r.pv):q for q,r in o.iterrows()}
segs=tt[(tt.category=='S2')&tt.video_id.str.endswith('_segmented')]
n=0; bad=[]
for q,r in segs.iterrows():
    oq=key.get((r.twin,r.nq,r.pv))
    if oq is None or tt.category[oq]!='S2': continue
    n+=1
    if not np.isclose(m[q],m[oq],rtol=1e-12): bad.append((q,r.video_id,oq,m[q],m[oq],v3[q],v3[oq]))
print('S2 seg rows with S2 twin',n,'mismatch final',bad)
# segmented S2 rows w/o twin
print('seg S2 rows total',len(segs))
# originals changed by merge that have any segmented S2 sibling (any question)
d=pd.read_csv(SP+'/merge/S2/decisions.csv')
for q in d.qid:
    vid=tt.video_id[q]
    if not vid.endswith('_segmented'):
        sib=tt[tt.video_id==vid+'_segmented']
        print(q, vid, 'seg clip exists' if len(sib) else 'no seg clip', list(zip(sib.index, sib.category, sib.question.str[:50])))
