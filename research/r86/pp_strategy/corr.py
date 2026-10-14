import sys; sys.path.insert(0,'/home/user/quantiphy-challenge')
import numpy as np, pandas as pd, glob
from qp.data import load_split
from qp.mra import item_scores
R='/home/user/quantiphy-challenge/runs/'
v=load_split('val').set_index('qid')
runs={}
for d in ['val_hr_v1_high','val_hr_v2_high','val_opus_high','val_opus_xhigh','val_fable_high','val_astra_high','val_gem31pro_video','val_v2_high','val_opus_med','val_opus_med2','val_hr_v2_med']:
    f=glob.glob(R+d+'/*.csv'); f=[x for x in f if 'dense' not in x][0]
    s=pd.read_csv(f); s=s.rename(columns={s.columns[0]:'id'}).set_index('id')['parsed_value']
    runs[d]=pd.to_numeric(s,errors='coerce').reindex(v.index)
E=pd.DataFrame({k:np.log(x/v.answer) for k,x in runs.items()})
E=E.replace([np.inf,-np.inf],np.nan)
grp=np.where(v.category.isin(['S2','D2']),'2D',np.where(v.video_source.isin(['lab','captured']),'lab','3dnl'))
v['grp']=grp
print(v.grp.value_counts())
def rsd(x): x=x.dropna(); return 1.4826*np.median(np.abs(x-np.median(x)))
for g in ['2D','lab','3dnl']:
    sub=E[v.grp==g]
    print('==',g)
    print('MRA', {k: round(np.nanmean(item_scores(runs[k][v.grp==g].values, v.answer[v.grp==g].values)),3) for k in runs})
    print('robust sd', sub.apply(rsd).round(3).to_dict())
    # winsorized correlation
    W=sub.clip(-0.7,0.7)
    print(W.corr(method='spearman').round(2).loc[['val_hr_v1_high','val_opus_high','val_astra_high','val_gem31pro_video']].to_string())
import itertools
print('\n=== triples (median) on 3dnl and lab and 2D')
cands=['val_hr_v1_high','val_hr_v2_high','val_opus_high','val_v2_high','val_opus_med2','val_fable_high','val_astra_high']
for g in ['3dnl','2D','lab']:
    msk=(v.grp==g).values
    res=[]
    for tri in itertools.combinations(cands,3):
        L=np.log(np.column_stack([runs[k].values for k in tri]))
        med=np.exp(np.nanmedian(L,axis=1))
        s=np.nanmean(item_scores(med[msk],v.answer.values[msk]))
        hr=sum('hr' in k for k in tri)
        res.append((round(s,3),hr,tri))
    res.sort(reverse=True)
    print(g); [print(r) for r in res[:6]]
    import collections
    byhr=collections.defaultdict(list)
    for s,hr,tri in res:
        if 'val_astra_high' in tri or 'val_fable_high' in tri: continue
        byhr[hr].append(s)
    print({k:(round(np.mean(x),3),len(x)) for k,x in byhr.items()})
print('\n=== empirical pair calibration: gm(A,B) - A vs (MRA_B - MRA_A, rho)')
rows=[]
allr=[k for k in runs if k!='val_gem31pro_video']
for g in ['2D','lab','3dnl']:
    msk=(v.grp==g).values; gt=v.answer.values[msk]
    for a in allr:
        for b in allr:
            if a==b: continue
            pa=runs[a].values[msk]; pb=runs[b].values[msk]
            ok=np.isfinite(pa)&np.isfinite(pb)&(pa>0)&(pb>0)
            if ok.sum()<20: continue
            ma=item_scores(pa[ok],gt[ok]).mean(); mb=item_scores(pb[ok],gt[ok]).mean()
            gm=np.sqrt(pa[ok]*pb[ok]); mg=item_scores(gm,gt[ok]).mean()
            ea=np.clip(np.log(pa[ok]/gt[ok]),-.7,.7); eb=np.clip(np.log(pb[ok]/gt[ok]),-.7,.7)
            rho=pd.Series(ea).rank().corr(pd.Series(eb).rank())
            rows.append(dict(g=g,a=a,b=b,dm=mb-ma,rho=rho,gain=mg-ma,n=ok.sum()))
P=pd.DataFrame(rows)
import numpy.linalg as la
for g in ['2D','lab','3dnl','all']:
    d=P if g=='all' else P[P.g==g]
    X=np.column_stack([np.ones(len(d)),d.dm,d.rho]); beta=la.lstsq(X,d.gain,rcond=None)[0]
    print(g,'n pairs',len(d),'gain ~ %.3f + %.2f*dm + %.3f*rho'%tuple(beta))
d=P
for lo,hi in [(-1,-.03),(-.03,-.01),(-.01,.01),(.01,.03),(.03,1)]:
    s=d[(d.dm>lo)&(d.dm<=hi)]
    print('dm in (%.2f,%.2f]: n %d mean gain %+.3f | rho<.6: %+.3f (n%d) rho>=.8: %+.3f (n%d)'%(lo,hi,len(s),s.gain.mean(),s[s.rho<.6].gain.mean(),(s.rho<.6).sum(),s[s.rho>=.8].gain.mean(),(s.rho>=.8).sum()))
