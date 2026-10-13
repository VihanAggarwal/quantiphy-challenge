import sys, os, pickle
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
W=SP+'/big/scenegraph/work'; EXT=SP+'/ext/d3rest'
sys.path.insert(0,W); sys.path.insert(0,EXT)
import numpy as np, pandas as pd
import graph as G
import equiv; equiv.MIN_NS=0.8   # eq3 (the scene graph pool) used 0.8
from pool2 import equiv_groups2
t=pd.read_pickle(EXT+'/work/TS_ext.pkl')
F=G.facts(t)
A_ext,R_ext=G.transfers3(t,F)
A_old=pd.read_pickle(W+'/transfers3.pkl')
A_ext.to_pickle(EXT+'/work/transfers_ext.pkl'); R_ext.to_pickle(EXT+'/work/transfers_ext_raw.pkl')
F.to_pickle(EXT+'/work/facts_ext.pkl')
print('old',len(A_old),(~A_old.conflict).sum(),' ext',len(A_ext),(~A_ext.conflict).sum())
new=A_ext[~A_ext.qid.isin(A_old.qid)]
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',70); pd.set_option('display.max_rows',300)
print(new[['qid','video_id','cat','question','v3','value','conflict','why','src','line']].to_string())
ch=A_ext.merge(A_old[['qid','value','conflict']],on='qid',suffixes=('','_old'))
ch=ch[(~np.isclose(ch.value.fillna(-1),ch.value_old.fillna(-1)))|(ch.conflict!=ch.conflict_old)]
print('changed old transfers'); print(ch[['qid','video_id','cat','question','value','value_old','conflict','conflict_old','src']].to_string())
eq=equiv_groups2(t)
pickle.dump(eq,open(EXT+'/work/eq_ext.pkl','wb'))
