import sys, pickle
sys.path.insert(0,'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ext/pool2d/rebuild')
from rule import *
TAU,CAP2,SMAX=0.15,0.25,0.35
t=pd.read_pickle(W+'/T.pkl'); ti=t.set_index('qid')
eq3=pickle.load(open(SP+'/big/scenegraph/work/eq3.pkl','rb'))
dec=pd.read_csv(SP+'/merge/D3/decisions.csv').set_index('qid')
Trows=set(int(l.split()[0]) for l in open(SP+'/big/scene_graph/T_list.txt') if not l.startswith('====='))
def rule_pv(v):
    v=list(v)
    if len(v)<2: return None
    if len(v)<=3 and max(v)-min(v)>SMAX: return None
    return pooled_value(v,TAU,CAP2,'trimmed')
G=build_groups(t,unit='cam',cats=('S2','D2','S3','D3'))
ws=lambda g: np.average(g.d,weights=g.w) if len(g) else float('nan')
for mode in ('all3d','drop_leaky','dedup'):
    rows=[]
    for gr in G:
        qs=[q for m in gr['members'].values() for q,_ in m]
        if any(q in Trows for q in qs): continue
        q2d=set(q for q in qs if ti.loc[q,'category'] in ('S2','D2'))
        cat_of={u:('2D' if set(ti.loc[[q for q,_ in m],'category'])<={'S2','D2'} else '3D') for u,m in gr['members'].items()}
        ul=dict(gr['ul'])
        if mode=='drop_leaky':
            for u,m in gr['members'].items():
                if cat_of[u]=='3D' and any(q in dec.index and 'SIM_P' in str(dec.chosen_source[q]) and set(eq3.get(q,()))&q2d for q,_ in m): ul.pop(u,None)
        if mode=='dedup':
            seen=set()
            for u in list(ul):
                if cat_of[u]=='3D':
                    k=round(ul[u],6)
                    if k in seen: ul.pop(u)
                    seen.add(k)
        u2=[u for u in ul if cat_of[u]=='2D']
        if len(u2)<2: continue
        for j in u2:
            oth=[u for u in ul if u!=j]
            pv=rule_pv([ul[u] for u in oth])
            for i in oth:
                if cat_of[i]!='2D': continue
                for q,lv in gr['members'][i]:
                    if ti.loc[q,'category']!='D2': continue
                    for _,rl in gr['members'][j]:
                        w=1/len(gr['members'][j])
                        rows.append(dict(w=w,d=float(S([(pv if pv is not None else lv)-rl])[0]-S([lv-rl])[0]),ch=pv is not None))
    P=pd.DataFrame(rows)
    print(f'{mode:11}: pseudo gain per changed D2 row {ws(P[P.ch]):+.4f}  (changed wt {P[P.ch].w.sum():.0f}); all rows {ws(P):+.4f}')
