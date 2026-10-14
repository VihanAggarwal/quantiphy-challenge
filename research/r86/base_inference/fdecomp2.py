import sys, numpy as np, pandas as pd
sys.path.insert(0,'/home/user/quantiphy-challenge')
from qp.mra import item_scores
R=pd.read_pickle('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/fdecomp.pkl')
t=pd.read_pickle('research/r86/loss_audit/master.pkl')
R=R.join(t[['fact','val','srcg','category','d1','d2','d3','dmed','prior']])
R=R[R.srcg=='sim']
# per-clip claude f (median over its questions)
R['fcl_clip']=R.groupby('video_id').f_claude.transform('median')
R['fg_clip']=R.groupby('video_id').f_geo.transform('median')
print('clips',R.video_id.nunique(),'with claude f',R.groupby('video_id').fcl_clip.first().notna().sum())
c=R.groupby('video_id')[['fcl_clip','fg_clip']].first().dropna()
print('median |log fcl/fgeo| per clip %.3f; frac >20%%: %.2f'%(np.median(np.abs(np.log(c.fcl_clip/c.fg_clip))), (np.abs(np.log(c.fcl_clip/c.fg_clip))>np.log(1.2)).mean()))
# within-clip spread of Claude's f
sp=R.groupby('video_id').f_claude.agg(lambda s: np.log(s.dropna()).std() if s.notna().sum()>1 else np.nan)
print('within-clip sd log f_claude median %.3f'%sp.median())
# labelled rows: d3 is the v2 run direct? check
lab=R[(R.fact.notna())|(R.val.notna())].copy()
lab['gtv']=lab.fact.fillna(lab.val)
lab=lab[lab.fcl_clip.notna()&lab.fg_clip.notna()]
size=lab.kind.isin(['size','distance'])
# size/dist answer ∝ 1/f ; speed ∝ 1/f too (px/s * r / f); accel too.
for nm,adj in [('direct',lab.direct),('direct*fcl/fg',lab.direct*lab.fcl_clip/lab.fg_clip),('gm',lab.direct*np.sqrt(lab.fcl_clip/lab.fg_clip)),('geo',lab.geo)]:
    s=item_scores(adj,lab.gtv)
    print(nm,'n',len(lab),'MRA %.3f'%np.nanmean(s),'med ale %.3f'%np.nanmedian(np.abs(np.log(adj/lab.gtv))))
# implied true f: f_true = f_claude * direct/gt
lab['f_true']=lab.fcl_clip*lab.direct/lab.gtv
ft=lab.groupby('video_id')[['f_true','fcl_clip','fg_clip']].median()
print('per clip |log fcl/ftrue| %.3f |log fg/ftrue| %.3f n=%d'%(np.median(np.abs(np.log(ft.fcl_clip/ft.f_true))),np.median(np.abs(np.log(ft.fg_clip/ft.f_true))),len(ft)))
print(ft.round(0).assign(W=lab.groupby('video_id').W.first()).to_string())
