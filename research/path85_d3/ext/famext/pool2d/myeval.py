import sys
sys.path.insert(0,'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ext/pool2d/rebuild')
from rule import *
TAU,CAP2,SMAX=0.15,0.25,0.35
t=pd.read_pickle(W+'/T.pkl'); ti=t.set_index('qid')
Trows=set()
for line in open(SP+'/big/scene_graph/T_list.txt'):
    if line.startswith('====='): continue
    Trows.add(int(line.split()[0]))
def rule_pv(votes):
    votes=list(votes)
    if len(votes)<2: return None
    if len(votes)<=3 and max(votes)-min(votes)>SMAX: return None
    return pooled_value(votes,TAU,CAP2,'trimmed')
G=build_groups(t,unit='cam',cats=('S2','D2'))
# deployed: which groups pooled, by number of units
dep=[]
for gr in G:
    qs=[q for m in gr['members'].values() for q,_ in m]
    if any(q in Trows for q in qs): continue
    if len(gr['ul'])<2: continue
    pv=rule_pv(gr['ul'].values())
    if pv is None: continue
    n2=sum(1 for q in qs if ti.loc[q,'category']=='D2' and not np.isclose(np.exp(pv),np.exp(dict(sum(gr['members'].values(),[]))[q]),rtol=1e-9))
    dep.append(dict(grp=gr['grp'],nu=len(gr['ul']),kind=gr['kind'],nrows=len(qs),nd2=n2,fam=ti.loc[gr['grp'],'fam']))
D=pd.DataFrame(dep)
print('deployed groups',len(D),'D2 rows changed',D.nd2.sum()); print(D.groupby('nu').agg(groups=('grp','size'),d2rows=('nd2','sum')))
# my pseudo eval: per ROW scoring (own value), reference = each row of held-out unit j (per-row, averaged)
rows=[]
for gr in G:
    qs=[q for m in gr['members'].values() for q,_ in m]
    if any(q in Trows for q in qs): continue
    U=list(gr['ul'])
    if len(U)<3: continue
    for j in U:
        oth=[u for u in U if u!=j]
        pv=rule_pv([gr['ul'][u] for u in oth])
        refs=[lv for q,lv in gr['members'][j]]
        for u in oth:
            for q,lv in gr['members'][u]:
                if ti.loc[q,'category']!='D2': continue
                for rl in refs:
                    rows.append(dict(grp=gr['grp'],fam=ti.loc[gr['grp'],'fam'],kind=gr['kind'],w=1/len(refs),raw=float(S([lv-rl])[0]),pool=float(S([(pv if pv is not None else lv)-rl])[0]),ch=pv is not None and abs(pv-lv)>1e-9))
P=pd.DataFrame(rows); P['d']=P.pool-P.raw
ws=lambda g: np.average(g.d,weights=g.w)
print('pseudo (per-row, row refs): all %+.4f  changed %+.4f  n_changed_wt %.0f'%(ws(P),ws(P[P.ch]),P[P.ch].w.sum()))
print(P[P.ch].groupby('kind').apply(ws).round(4).to_dict())
# cluster bootstrap over families
rng=np.random.default_rng(1); fams=P.fam.unique(); bs=[]
Pc=P[P.ch]
for b in range(2000):
    s=rng.choice(fams,len(fams)); X=pd.concat([Pc[Pc.fam==f] for f in s])
    bs.append(ws(X) if len(X) else 0)
print('family bootstrap of changed-row gain: mean %+.4f  2.5%% %+.4f  97.5%% %+.4f  P(<=0) %.3f'%(np.mean(bs),np.percentile(bs,2.5),np.percentile(bs,97.5),np.mean(np.array(bs)<=0)))
print('by family:'); print(Pc.groupby('fam').apply(lambda g: pd.Series(dict(gain=ws(g),wt=g.w.sum()))).round(4).sort_values('wt',ascending=False).to_string())
