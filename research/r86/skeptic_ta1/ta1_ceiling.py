"""Skeptic check for TA-1: ceiling of adding one extra vote to the 3-run Claude median on 3D non-lab.
Oracle vote (o = truth) and synthetic independent votes o = truth*exp(N(b, s)). Analysis only."""
import sys; sys.path.insert(0,'/home/user/quantiphy-challenge')
import numpy as np, pandas as pd
from qp.mra import item_scores
R='/home/user/quantiphy-challenge/'
m=pd.read_pickle(R+'research/r86/loss_audit/master.pkl')
nl=m.category.isin(['S3','D3'])&(m.srcg=='sim')
C=m[['d1','d2','d3']].where(m[['d1','d2','d3']]>0)
L=np.log(C)
dm=np.exp(L.median(axis=1))
def ev(p,g): p=np.where(np.isfinite(p)&(p>0),p,1e-9); return item_scores(p,g)
rng=np.random.default_rng(0)
for lab,gcol in [('val-overlap',m.val),('facts raw',m.fact)]:
    mask=nl&gcol.notna()&L.notna().all(axis=1)
    g=gcol[mask].values; Lm=L[mask].values
    base=ev(dm[mask].values,g)
    def med4(o): return np.exp(np.median(np.column_stack([Lm,np.log(o)]),axis=1))
    orc=ev(med4(g),g)
    print(f'-- {lab}: n={mask.sum()} clips={m.loc[mask,"video_id"].nunique()} base={base.mean():.4f}  ORACLE med4 gain={orc.mean()-base.mean():+.4f}')
    # how far can med4 move from med3? |log(med4/med3)|
    sh=np.abs(np.log(med4(g)/dm[mask].values)); print(f'   oracle shift |log| median {np.median(sh):.3f}, mean {sh.mean():.3f}, frac rows changing score {np.mean(orc!=base):.2f}')
    for s in [0.05,0.1,0.15,0.2,0.3,0.4]:
        for b in [0.0,-0.1]:
            gains=[]
            for k in range(200):
                o=g*np.exp(rng.normal(b,s,len(g)))
                gains.append(ev(med4(o),g).mean()-base.mean())
            print(f'   indep vote sigma={s:.2f} bias={b:+.1f}: med4 gain {np.mean(gains):+.4f} (sd {np.std(gains):.4f})')

print('\n== actual open members: error vs truth on 3D non-lab (log err)')
from qp.data import load_split
v=load_split('val'); t=load_split('test')
j=v.merge(t[['qid','video_id','question']],on=['video_id','question'],suffixes=('_v','_t'))
vmap=dict(zip(j.qid_v,j.qid_t))
def rd(p):
    d=pd.read_csv(p); return pd.to_numeric(d.set_index('id')['parsed_value'],errors='coerce')
for mm in ['qwen_direct','gemma4_direct','qwen35_direct','qwen_geometry','cvq_geometry']:
    o=rd(R+f'research/r86/intel_tb_pseudolabel/members/test/{mm}.csv').reindex(m.index)
    for lab,gcol in [('val',m.val),('facts',m.fact)]:
        mask=nl&gcol.notna()&(o>0)
        le=np.log(o[mask]/gcol[mask]); lc=np.log(dm[mask]/gcol[mask])
        print(f'{mm:14s} {lab:5s} n={mask.sum():3d} open med|err|={np.median(np.abs(le)):.3f} bias={np.median(le):+.3f} >2x={np.mean(np.abs(le)>np.log(2)):.2f} | claude3 med|err|={np.median(np.abs(lc)):.3f} | corr(err)={np.corrcoef(le,lc)[0,1]:+.2f} sign-agree={np.mean(np.sign(le)==np.sign(lc)):.2f}')
