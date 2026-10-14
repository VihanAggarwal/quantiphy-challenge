import json, glob, os, sys, numpy as np, pandas as pd
sys.path.insert(0,'/home/user/quantiphy-challenge')
from qp.mra import item_scores
def track_px(tr):
    """median object size in sent pixels: extent length, else box max side"""
    L=[]
    for o in tr['obs']:
        if o.get('extent'):
            (x1,y1),(x2,y2)=o['extent'][0],o['extent'][1]; L.append(np.hypot(x2-x1,y2-y1))
        elif o.get('box'):
            b=o['box']; L.append(max(abs(b[2]-b[0]),abs(b[3]-b[1])))
    return float(np.median(L)) if L else np.nan
def motion_px(tr):
    P=[(o['frame'],o['point']) for o in tr['obs'] if o.get('point')]
    if len(P)<2: return np.nan
    P.sort(); f=np.array([p[0] for p in P]); xy=np.array([p[1] for p in P])
    return float(np.hypot(*(xy[-1]-xy[0])))
rows=[]
for run in ['runs/test_v1_high_854/test/records']:
    for p in glob.glob(run+'/*.json'):
        d=json.load(open(p))
        if not d.get('parsed'): continue
        W,H=d['meta']['image_size']; sc=d['meta']['scale']
        # object name -> best track size
        objsz={}
        for q in d['parsed']['questions']:
            for tr in q['tracks']:
                s=track_px(tr)
                if not np.isnan(s): objsz[tr['object']]=max(objsz.get(tr['object'],0),s)
        for q in d['parsed']['questions']:
            r={'qid':q['qid'],'video_id':d['video_id'],'W_sent':round(W*sc),'conf':q['confidence']}
            for tr in q['tracks']:
                s=track_px(tr)
                if np.isnan(s): s=objsz.get(tr['object'],np.nan)
                r[tr['role']+'_px']=s
                if tr['role'] in ('prior','target'): r[tr['role']+'_mov']=motion_px(tr)
            rows.append(r)
df=pd.DataFrame(rows).set_index('qid')
df.to_pickle('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/objsize.pkl')
print(df.describe())
