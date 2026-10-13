import sys, os, pickle, re, json
import numpy as np, pandas as pd
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
W=SP+'/big/scenegraph/work'
R='/home/user/quantiphy-challenge'
OUT=SP+'/ext/s3kp/rebuild'
sys.path.insert(0,R)
_cwd=os.getcwd()
sys.path.insert(0,W); os.chdir(W)
sys.dont_write_bytecode=True
from evalknown import *   # pool2, graph, series, fam2, ... (reads only)
os.chdir(_cwd)
from qp.mra import item_scores
t=pd.read_pickle(W+'/work/TS.pkl'); ti=t.set_index('qid')
eq=pickle.load(open(W+'/work/eq3.pkl','rb'))
V3=pd.read_csv(R+'/submissions/trackA_v3_best_per_category.csv'); v3=dict(zip(V3.id,V3.parsed_value))
P5=pd.read_csv(R+'/submissions/trackA_probe5_families_merged.csv'); p5=dict(zip(P5.id,P5.parsed_value))
A=pd.read_pickle(W+'/work/transfers3.pkl'); A=A[~A.conflict].copy()
A['kind']=ti.loc[A.qid,'tkind'].values
def m1(p,g):
    return float(item_scores(np.array([p],float),np.array([g],float))[0])
from qp.parse import canonical_unit, _UNITS
def usc(q):
    cu=canonical_unit(ti.loc[q,'target_unit'] or 'm') or 'm'
    return _UNITS[cu][0] if cu in _UNITS else 1.0
