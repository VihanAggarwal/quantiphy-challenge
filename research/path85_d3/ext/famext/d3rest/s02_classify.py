import sys, re, json, numpy as np, pandas as pd
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
W=SP+'/big/scenegraph/work'
D3=pd.read_pickle(SP+'/ext/d3rest/D3.pkl')
t=pd.read_pickle(W+'/TS.pkl').set_index('qid')
for c in ['tkind','tobj','tdim','ttime','pkind','pobj','pdim','pval','direct','method','base','fam','scen','geo_value','direct_value']:
    D3[c]=t.loc[D3.index,c]
fam=json.load(open(SP+'/big/scenegraph/families.json'))
sf=fam['series_families']
inmulti={}
for k,v in sf.items():
    for b in v['bases']: inmulti[b]=k
D3['multifam']=D3.base.map(lambda b: b in inmulti)
D3['famsize']=D3.base.map(lambda b: len(sf[inmulti[b]]['bases']) if b in inmulti else 1)
D3['isdirect']=np.isclose(D3.v3, pd.to_numeric(D3.direct_value,errors='coerce'), rtol=1e-6)
D3.to_pickle(SP+'/ext/d3rest/D3c.pkl')
u=D3[~D3.changed]
pd.set_option('display.width',250)
print(pd.crosstab([u.video_source,u.tkind],[u.multifam,u.isdirect],margins=True))
print(pd.crosstab([D3.video_source,D3.tkind],D3.changed,margins=True))
