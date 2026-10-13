import sys, json, glob, re, math, os, pickle
sys.path.insert(0,'/home/user/quantiphy-challenge')
import pandas as pd, numpy as np
from qp.data import load_split
from qp.mra import item_scores
R='/home/user/quantiphy-challenge'
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
W=SP+'/ext/pool2d/rebuild'
def base_id(v):
    return re.sub(r'(_segmented|(?<=\d)[sxX])$','',v)
def mra1(p,g):
    return float(item_scores([p],[g])[0])
def records(d=R+'/runs/test_v1_high_854/test/records'):
    out={}
    for f in glob.glob(d+'/*.json'):
        r=json.load(open(f)); out[r['video_id']]=r
    return out
def build():
    t=load_split('test')
    recs=records()
    rows={}
    for v,r in recs.items():
        p=r.get('parsed') or {}
        for q in p.get('questions',[]):
            s=q['spec']; T=s['target']; P=s['prior']
            rows[int(q['qid'])]=dict(tkind=T['kind'],tobj='|'.join(T['objects'] or []),tdim=T.get('dimension'),ttime=T.get('time'),twin=T.get('window'),tunit=T.get('unit'),
               pkind=P['kind'],pobj='|'.join(P['objects'] or []),pdim=P.get('dimension'),ptime=P.get('time'),pwin=P.get('window'),pval=P.get('value_si'),
               direct=q.get('direct_answer'),conf=q.get('confidence'))
    Q=pd.DataFrame.from_dict(rows,orient='index'); Q.index.name='qid'
    t=t.merge(Q,left_on='qid',right_index=True,how='left')
    run=pd.read_csv(R+'/runs/test_v1_high_854/test.csv').rename(columns={'id':'qid'})
    t=t.merge(run[['qid','geo_value','direct_value','method','flags']],on='qid',how='left')
    ro=pd.read_csv(SP+'/probe3/refineoff/runs/test_v1_high_854/test.csv').rename(columns={'id':'qid','parsed_value':'refoff','geo_value':'geo_refoff'})
    t=t.merge(ro[['qid','refoff','geo_refoff']],on='qid',how='left')
    for name,f in [('v2','trackA_opus55_high_v2.csv'),('v3','trackA_v3_best_per_category.csv'),('p4','trackA_probe4_s2twin_d2refineoff_s3split_d3fixes.csv'),('p5','trackA_probe5_families_merged.csv')]:
        s=pd.read_csv(R+'/submissions/'+f)[['id','parsed_value']].rename(columns={'id':'qid','parsed_value':name})
        t=t.merge(s,on='qid',how='left')
    t['base']=t.video_id.map(base_id)
    return t, recs
if __name__=='__main__':
    t,recs=build()
    t.to_pickle(W+'/T.pkl')
    print(t.shape); print(t.category.value_counts())
    print(t[t.category.isin(['S2','D2'])].groupby(['category','video_source']).size())
