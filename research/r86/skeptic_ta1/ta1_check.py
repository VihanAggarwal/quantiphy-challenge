import sys; sys.path.insert(0,'/home/user/quantiphy-challenge')
import numpy as np, pandas as pd
from qp.data import load_split
from qp.mra import item_scores
R='/home/user/quantiphy-challenge/'
m=pd.read_pickle(R+'research/r86/loss_audit/master.pkl')
v=load_split('val'); t=load_split('test')
j=v.merge(t[['qid','video_id','question']],on=['video_id','question'],suffixes=('_v','_t'))
vmap=dict(zip(j.qid_v,j.qid_t))
def rd(p):
    d=pd.read_csv(p); return pd.to_numeric(d.set_index('id')['parsed_value'],errors='coerce')
rr=lambda p: pd.to_numeric(pd.read_csv(p).set_index('id')['direct_value'],errors='coerce').reindex(m.index)
C=[rr(R+'runs/test_v1_high_854/test.csv'),rr(R+'runs/test_3dnl_v1_high_b/test.csv'),rr(R+'runs/test_3dnl_v2_high/test.csv')]
for i,c in enumerate(C): m[f'c{i}']=c
OPEN=['qwen_direct','gemma4_direct','qwen35_direct','qwen_geometry','cvq_geometry']
for mm in OPEN:
    tt=rd(R+f'research/r86/intel_tb_pseudolabel/members/test/{mm}.csv'); m[mm]=tt.reindex(m.index)
    vv=rd(R+f'research/r86/intel_tb_pseudolabel/members/val/{mm}.csv')
    s=pd.Series({vmap[k]:x for k,x in vv.items() if k in vmap})
    m[mm+'_v']=np.nan; m.loc[s.index.intersection(m.index), mm+'_v']=s
nl=m.category.isin(['S3','D3'])&(m.srcg=='sim')
print('3D non-lab rows', nl.sum(), 'scored', (nl&m.scored.astype(bool)).sum())
dm=np.exp(np.log(m[['c0','c1','c2']]).median(axis=1))
print('dmed vs recomputed median: max |log|', np.nanmax(np.abs(np.log(dm[nl]/m.dmed[nl]))))
print('\n== PRE-CHECK: median |log(open/claude3med)| on 3D non-lab test rows')
for mm in OPEN:
    x=m.loc[nl,mm]; ok=(x>0)&np.isfinite(x)
    lr=np.log(x[ok]/dm[nl][ok])
    print(f'{mm:15s} n={ok.sum():4d} med|lr|={np.median(np.abs(lr)):.3f}  median lr={np.median(lr):+.3f}  frac>2x={np.mean(np.abs(lr)>np.log(2)):.2f}')
# Claude run vs run for reference
lr=np.log(m.loc[nl,'c1']/m.loc[nl,'c0']); print('claude c1 vs c0 med|lr|', round(np.nanmedian(np.abs(lr)),3))
def ev(p,g): p=np.where(np.isfinite(p)&(p>0),p,1e-9); return item_scores(p,g).mean()
print('\n== GATE: median(3 Claude + open) vs 3-run median')
for lab,gcol,suff in [('val-overlap',m.val,'_v'),('val-overlap(testrun)',m.val,''),('facts raw',m.fact,'')]:
    mask=nl&gcol.notna()
    g=gcol[mask].values
    base=ev(dm[mask].values,g)
    print(f'-- {lab}: n={mask.sum()} clips={m.loc[mask,"video_id"].nunique()} base(3med)={base:.4f}')
    for mm in OPEN:
        o=m.loc[mask,mm+suff]
        have=(o>0)&np.isfinite(o)
        L=np.log(m.loc[mask,['c0','c1','c2']]).copy(); L['o']=np.log(o.where(have))
        med4=np.exp(L.median(axis=1,skipna=True)).values
        gm=np.exp(0.75*np.log(dm[mask])+0.25*np.log(o.where(have,dm[mask]))).values
        so=ev(o.where(have,np.nan).fillna(1e-9).values,g)
        print(f'   {mm:15s} have={have.sum():3d} alone={so:.3f} med4={ev(med4,g)-base:+.4f} w.25={ev(gm,g)-base:+.4f}')
    # all three open directs together + 3 Claude => median of 6
    L=np.log(m.loc[mask,['c0','c1','c2']+[x+suff for x in OPEN[:3]]].where(lambda d:d>0))
    print(f'   median6(3C+3open) {ev(np.exp(L.median(axis=1)).values,g)-base:+.4f}')
