import sys, pandas as pd, numpy as np
sys.path.insert(0,'/home/user/quantiphy-challenge')
from qp.mra import item_scores
v=pd.read_pickle('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/valruns.pkl')
v['grp']=np.where(v.category.str[1]=='2','2D',np.where(v.video_source=='lab','lab','3Dsim'))
def sc(x,sub): return np.nanmean(item_scores(x,sub.answer))
for g in ['2D','lab','3Dsim']:
    sub=v[v.grp==g]
    print('==',g,len(sub))
    for nm in ['o854','om','om2','v2v','hr1','hr2','hr2m']:
        gm=np.exp((np.log(sub[nm+'_g'].where(sub[nm+'_g']>0))+np.log(sub[nm+'_d']))/2).fillna(sub[nm+'_d'])
        print(nm, 'parsed %.3f geo %.3f dir %.3f gm %.3f'%(sc(sub[nm+'_p'],sub),sc(sub[nm+'_g'],sub),sc(sub[nm+'_d'],sub),sc(gm,sub)))
    # cross-run median of directs at hires
    D=np.log(sub[[n+'_d' for n in ['hr1','hr2','hr2m']]])
    print('hr med3 direct %.3f'%sc(np.exp(D.median(axis=1)),sub))
    D=np.log(sub[[n+'_d' for n in ['o854','om','om2']]])
    print('480 med3 direct %.3f'%sc(np.exp(D.median(axis=1)),sub))
    D=np.log(sub[[n+'_g' for n in ['hr1','hr2','hr2m']]])
    print('hr med3 geo %.3f'%sc(np.exp(D.median(axis=1)),sub))
