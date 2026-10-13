import sys, numpy as np, pandas as pd
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
E=SP+'/ext/d3rest'
t=pd.read_pickle(E+'/work/TS_ext.pkl')
R='/home/user/quantiphy-challenge'
p5=pd.read_csv(R+'/submissions/trackA_probe5_families_merged.csv').set_index('id').parsed_value
C=pd.read_csv(E+'/D3ext_C_TP_KOBJ_HUMAN.csv').set_index('id').parsed_value
t['p5']=t.qid.map(p5); t['C']=t.qid.map(C)
vids=sys.argv[1].split(',')
for v in vids:
    g=t[t.video_id==v]
    if not len(g): print('== missing',v); continue
    print(f'=== {v} {g.category.iloc[0]} fam_old={g.fam_old.iloc[0]} fam={g.fam.iloc[0]} prior="{g.prior.iloc[0]}"')
    if '-d' in sys.argv: print('   depth:', str(g.depth_info.iloc[0])[:400].replace('\n',' | '))
    for r in g.itertuples():
        mark='*' if not np.isclose(r.p5,r.C) else ' '
        print(f'  {mark}{r.qid} {r.category} {r.tkind:8s} {r.question[:95]:95s} v3={r.v3:.4g} p5={r.p5:.4g} C={r.C:.4g} {str(r.method)[:12]}')
