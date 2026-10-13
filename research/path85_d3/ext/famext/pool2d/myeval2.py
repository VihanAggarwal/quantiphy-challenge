import sys
sys.path.insert(0,'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ext/pool2d/rebuild')
from rule import *
exec(open('myeval.py').read().split('G=build_groups')[0].split('t=pd.read_pickle')[1].join(['t=pd.read_pickle','']) if False else '')
TAU,CAP2,SMAX=0.15,0.25,0.35
t=pd.read_pickle(W+'/T.pkl'); ti=t.set_index('qid')
Trows=set(int(l.split()[0]) for l in open(SP+'/big/scene_graph/T_list.txt') if not l.startswith('====='))
G=build_groups(t,unit='cam',cats=('S2','D2'))
# (A) 2-vote rule tested inside >=3-unit groups: reference j, pair (i,k) from others
rows=[]
for gr in G:
    qs=[q for m in gr['members'].values() for q,_ in m]
    if any(q in Trows for q in qs): continue
    U=list(gr['ul'])
    if len(U)<3: continue
    for j in U:
        refs=[lv for q,lv in gr['members'][j]]
        oth=[u for u in U if u!=j]
        for a in range(len(oth)):
            for b in range(a+1,len(oth)):
                i,k=oth[a],oth[b]
                vi,vk=gr['ul'][i],gr['ul'][k]
                pv=(vi+vk)/2 if abs(vi-vk)<=CAP2 else None
                for u in (i,k):
                    for q,lv in gr['members'][u]:
                        if ti.loc[q,'category']!='D2': continue
                        for rl in refs:
                            rows.append(dict(fam=ti.loc[gr['grp'],'fam'],w=1/len(refs),raw=float(S([lv-rl])[0]),pool=float(S([(pv if pv is not None else lv)-rl])[0]),ch=pv is not None))
P=pd.DataFrame(rows); P['d']=P.pool-P.raw
ws=lambda g: np.average(g.d,weights=g.w)
print('2-vote rule emulated in >=3-unit groups: changed-row gain %+.4f (wt %.0f), fams %d'%(ws(P[P.ch]),P[P.ch].w.sum(),P.fam.nunique()))
# (B) within-camera vs between-camera variance
wv=[];bv=[];nc=[]
for gr in G:
    for u,m in gr['members'].items():
        if len(m)>=2:
            v=np.array([lv for q,lv in m]); wv.append(np.var(v,ddof=1))
    if len(gr['ul'])>=2:
        cm=np.array(list(gr['ul'].values())); bv.append(np.var(cm,ddof=1))
        nc.append(np.mean([len(m) for m in gr['members'].values()]))
print('within-camera var of log (per clip) median %.5f mean %.5f n=%d'%(np.median(wv),np.mean(wv),len(wv)))
print('between-camera var of camera-mean log median %.5f mean %.5f n=%d; mean clips/cam %.2f'%(np.median(bv),np.mean(bv),len(bv),np.mean(nc)))
