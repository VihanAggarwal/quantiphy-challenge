import sys; sys.path.insert(0,'/home/user/quantiphy-challenge')
import numpy as np, pandas as pd
from qp.data import load_split
from qp.mra import item_scores
R='/home/user/quantiphy-challenge/'
m=pd.read_pickle(R+'research/r86/loss_audit/master.pkl')
v=load_split('val'); t=load_split('test')
j=v.merge(t[['qid','video_id','question']],on=['video_id','question'],suffixes=('_v','_t'))
vmap=dict(zip(j.qid_v,j.qid_t))
MEM=['cvq_geometry','cv_geometry','qwen_geometry','caw_caw','qwen_direct','gemma4_direct','qwen35_direct']
def rd(p):
    d=pd.read_csv(p); return pd.to_numeric(d.set_index('id')['parsed_value'],errors='coerce')
for mm in MEM:
    vv=rd(R+f'research/r86/intel_tb_pseudolabel/members/val/{mm}.csv')
    s=pd.Series({vmap[k]:x for k,x in vv.items() if k in vmap})
    tt=rd(R+f'research/r86/intel_tb_pseudolabel/members/test/{mm}.csv')
    # for val-overlap rows use the val-run output (that is what was evaluated); else test output
    m[mm]=tt.reindex(m.index)
    m.loc[s.index.intersection(m.index), mm+'_v']=s
m['raw']=m.r_parsed_value.where(~((m.category.isin(['S3','D3']))&(m.srcg=='sim')),m.dmed)
def ev(pred,gt,mask):
    p=pred[mask].values; g=gt[mask].values
    p=np.where(np.isfinite(p)&(p>0),p,1e-9); return item_scores(p,g).mean(), mask.sum()
for mm in ['cvq_geometry','cv_geometry','qwen_geometry']:
    print('==',mm)
    for lab,A,B,gt in [('val',m.combo3,m[mm+'_v'],m.val),('fact',m.raw,m[mm],m.fact)]:
        has=gt.notna()&B.notna()&(B>0)
        for grp,gm in [('2D',m.category.isin(['S2','D2'])),('3D',m.category.isin(['S3','D3']))]:
            mask=has&gm
            if mask.sum()==0: continue
            base,n=ev(A,gt,mask)
            lr=np.log(B/A)
            out=[]
            for tau in [0.05,0.1,0.15,0.25]:
                for w in [0.5]:
                    P=A.copy(); g=mask&(lr.abs()<tau)
                    P[g]=np.exp((1-w)*np.log(A[g])+w*np.log(B[g]))
                    s,_=ev(P,gt,mask); out.append(f't{tau}:{s-base:+.4f}(n{g.sum()})')
            print(lab,grp,'n',n,'base %.4f'%base,' '.join(out))
