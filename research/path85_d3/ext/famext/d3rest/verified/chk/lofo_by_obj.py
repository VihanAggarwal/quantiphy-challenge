import sys, pickle
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
E=SP+'/ext/d3rest'; W=SP+'/big/scenegraph/work'
sys.path.insert(0,E); sys.path.insert(0,W); sys.path.insert(0,'/home/user/quantiphy-challenge')
import pandas as pd, numpy as np, io, contextlib
import s04_lofo as L
t=pd.read_pickle(E+'/work/TS_ext.pkl'); A=pd.read_pickle(E+'/work/transfers_ext.pkl'); eq=pickle.load(open(E+'/work/eq_ext.pkl','rb'))
ti=t.set_index('qid')
with contextlib.redirect_stdout(io.StringIO()):
    R=L.run(t,A,eq,3)
R['obj']=ti.loc[R.qid,'tobj'].values; R['vid']=ti.loc[R.qid,'video_id'].values
R['person']=R.obj.str.contains('person|man|woman|human|pedestrian',case=False)
per={q:len(__import__('pool2').per_base_values(ti,eq,q)) for q in R.qid}
R['nb']=R.qid.map(per)
pd.set_option('display.width',250); pd.set_option('display.max_rows',200)
print(R.groupby('person')[['m_raw','m_K','m_P','m_KP']].agg(['mean','size']).round(3))
X=R[R.nb>=3]
print('pooled only'); print(X.groupby('person')[['m_raw','m_K','m_P','m_KP']].agg(['mean','size']).round(3))
print(R.groupby('obj')[['m_raw','m_KP','nb']].agg(['mean','size']).round(3).to_string())
