"""Reproduce the scene_graph verifier's D3 variants (TKP_LABfix, TP_LABfix, T_LABfix) with per-row rule labels."""
import sys, os, pickle
MD='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/merge/D3'
sys.path.insert(0,'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/big/scene_graph')
import fix_build as FB
import numpy as np, pandas as pd
out={}
for name,cfg in {'TKP':dict(rule_K=True,rule_P=True,rule_LAB=True),'TP':dict(rule_P=True,rule_LAB=True),'T':dict(rule_LAB=True)}.items():
    new,why=FB.variant_fixed(('D3',),**cfg)
    out[name]=(new,why)
# also the T table (transfers) and the clip K values, for inspection
A=FB.A.copy()
out['A']=A
out['KC']=FB.KC
out['ti']=FB.ti
out['eq']=FB.eq
pickle.dump(out,open(MD+'/sg_why.pkl','wb'))
for name in ('TKP','TP','T'):
    d=pd.read_csv(f'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/big/scene_graph/D3_{name}_LABfix.csv')
    new,why=out[name]
    d3=[q for q in d.id if FB.ti.loc[q,'category']=='D3']
    dv=dict(zip(d.id,d.parsed_value))
    bad=[q for q in d3 if not np.isclose(dv[q],new[q],rtol=1e-9)]
    print(name,'repro mismatches',len(bad))
