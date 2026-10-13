from pool2 import *
t=pd.read_pickle(W+'/T.pkl')
# within-camera groups: split each group by camera, units = prior text
G=build_groups(t,unit='camprior')
WG=[]
for gr in G:
    bycam={}
    for u,v in gr['ul'].items(): bycam.setdefault(u[0],{})[u]=v
    for cam,ul in bycam.items():
        if len(ul)>=2:
            WG.append(dict(grp=gr['grp'],kind=gr['kind'],ul=ul,members={u:gr['members'][u] for u in ul},spread=max(ul.values())-min(ul.values())))
print('within-camera groups',len(WG),'rows',sum(sum(len(m) for m in g['members'].values()) for g in WG))
for stat in ('mean','median'):
    for minu in (2,3):
        R=pseudo(WG,stat,10,minu=minu)
        ws=lambda g: np.average(g.d,weights=g.wt)
        print(stat,'minu',minu,f'all {ws(R):+.4f} n={int(R.wt.sum())}',{k:(round(ws(g),4),int(g.wt.sum())) for k,g in R.groupby('kind')})
# pairs (n=2) within camera: how often do the two disagree > 5%?
d=[abs(list(g['ul'].values())[0]-list(g['ul'].values())[1]) for g in WG if len(g['ul'])==2]
print('2-prior within-camera pairs',len(d),'median |dlog|',np.median(d).round(4),'frac>0.05',np.mean(np.array(d)>0.05).round(3))
