import sys, numpy as np, pandas as pd
sys.path.insert(0,'/home/user/quantiphy-challenge')
from qp.mra import item_scores
t=pd.read_pickle('research/r86/loss_audit/master.pkl')
t['qn']=t.question.str.strip().str.lower()
s3=t[(t.category.isin(['S3','D3']))&(t.srcg=='sim')].copy()
seg=s3[s3.video_id.str.endswith('_segmented')].copy()
seg['orig']=seg.video_id.str.replace('_segmented','')
orig=s3[~s3.video_id.str.endswith('_segmented')].reset_index().set_index(['video_id','qn'])
pairs=[]
for q,r in seg.iterrows():
    k=(r.orig,r.qn)
    if k in orig.index:
        o=orig.loc[k]
        if isinstance(o,pd.DataFrame): o=o.iloc[0]
        if r.prior.strip()!=o.prior.strip(): continue
        pairs.append(dict(qid_s=q,qid_o=o['qid'],vid=r.orig,cat=r.category,kind=r.kind,
            s1=r.d1,s2=r.d2,s3=r.d3,o1=o.d1,o2=o.d2,o3=o.d3,fact=r.fact if pd.notna(r.fact) else o.fact,
            val=r.val if pd.notna(r.val) else o.val, scored_s=r.scored, scored_o=o.scored))
P=pd.DataFrame(pairs)
print('pairs',len(P),'clips',P.vid.nunique())
L=lambda c: np.log(P[c].astype(float))
P['om']=np.exp(pd.concat([L('o1'),L('o2'),L('o3')],axis=1).median(axis=1))
P['sm']=np.exp(pd.concat([L('s1'),L('s2'),L('s3')],axis=1).median(axis=1))
P['pool6']=np.exp(pd.concat([L(c) for c in ['o1','o2','o3','s1','s2','s3']],axis=1).median(axis=1))
P['gm2']=np.sqrt(P.om*P.sm)
# within-run spread vs between twin
P['sd_o']=pd.concat([L('o1'),L('o2'),L('o3')],axis=1).std(axis=1)
P['sd_s']=pd.concat([L('s1'),L('s2'),L('s3')],axis=1).std(axis=1)
P['tw']=np.abs(np.log(P.om/P.sm))
print('median within sd orig %.3f twin %.3f ; median |log om/sm| %.3f'%(P.sd_o.median(),P.sd_s.median(),P.tw.median()))
for lbl in ['fact','val']:
    Q=P[P[lbl].notna()]
    if len(Q)==0: continue
    g=Q[lbl].astype(float)
    print(lbl,len(Q),'clips',Q.vid.nunique(),{c:round(np.mean(item_scores(Q[c],g)),3) for c in ['om','sm','gm2','pool6']},
          'ale',{c:round(np.median(np.abs(np.log(Q[c]/g))),3) for c in ['om','sm','gm2','pool6']})
    # orig error vs twin error correlation
    eo=np.log(Q.om/g); es=np.log(Q.sm/g)
    print('   corr(err_o, err_s)=%.2f'%np.corrcoef(eo,es)[0,1], 'sd eo %.3f es %.3f'%(eo.std(),es.std()))
# runs correlation: corr of err between run1 and run2 within orig on facts
Q=P[P.fact.notna()]; g=Q.fact.astype(float)
e1=np.log(Q.o1/g); e2=np.log(Q.o2/g); e3=np.log(Q.o3/g)
print('corr err run1-run2 %.2f run1-run3 %.2f run2-run3 %.2f'%(np.corrcoef(e1,e2)[0,1],np.corrcoef(e1,e3)[0,1],np.corrcoef(e2,e3)[0,1]))
print('corr err o1-s1 %.2f'%np.corrcoef(e1,np.log(Q.s1/g))[0,1])
P.to_pickle('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/twinpairs.pkl')
print('scored rows in pairs: seg',P.scored_s.sum(),'orig',P.scored_o.sum())
print(P.groupby('cat').size())
