"""Evaluation of the deployed pooling rule (no labels): (1) stated facts as truth (leave the fact out: the T row's own
pre-T answer is pooled with its group), (2) pseudo-truth: each 2D camera in turn is held out as the reference and the
other cameras' rows are scored raw vs pooled under the same rule, (3) cross-clip spread."""
from rule import *
from qp.parse import canonical_unit,_UNITS
TAU,CAP2,SMAX=0.15,0.25,0.35
t=pd.read_pickle(W+'/T.pkl')
t['pre']=np.where(t.category=='S2',t.p4,t.p5)       # S2 p5 carries T on 4 rows; p4 = same rows before T
ti=t.set_index('qid')
def rule_pv(votes):
    if len(votes)<2: return None
    if len(votes)<=3 and max(votes)-min(votes)>SMAX: return None
    return pooled_value(votes,TAU,CAP2,'trimmed')
Trows={}
cur=None
for line in open(SP+'/big/scene_graph/T_list.txt'):
    if line.startswith('====='): cur=line.split()[1]; continue
    q=int(line.split()[0]); Trows[q]=float(re.search(r'-> ([\d.eE+-]+)',line).group(1))
out={}
for label,cats in (('2D votes',('S2','D2')),('2D+3D votes',('S2','D2','S3','D3'))):
    G=build_groups(t,col='pre',unit='cam',cats=cats)
    # (1) stated facts
    fr=[]
    for gr in G:
        qs=[q for mem in gr['members'].values() for q,_ in mem]
        tq=[q for q in qs if q in Trows and ti.loc[q,'category'] in ('S2','D2')]
        if not tq: continue
        cat_of={u:('2D' if set(ti.loc[[q for q,_ in m],'category'])<={'S2','D2'} else '3D') for u,m in gr['members'].items()}
        votes=list(gr['ul'].values())
        if label=='2D votes' and sum(1 for u in cat_of if cat_of[u]=='2D')<2: pv=None
        else: pv=rule_pv(votes)
        for q in tq:
            tu=ti.loc[q,'target_unit']; u=canonical_unit(str(tu)) if tu else None; f=_UNITS[u][0] if u in _UNITS else 1.0
            V=Trows[q]; raw=ti.loc[q,'pre']; new=raw if pv is None else np.exp(pv)/f
            fr.append(dict(qid=q,V=V,rawv=raw,newv=new,cat=ti.loc[q,'category'],raw=mra1(raw,V),pool=mra1(new,V),changed=pv is not None))
    F=pd.DataFrame(fr); print(label); print(F[F.raw!=F.pool].to_string()) if (F.raw!=F.pool).any() else None
    # (2) pseudo-truth over held-out 2D cameras
    rows=[]
    for gr in G:
        cat_of={u:('2D' if set(ti.loc[[q for q,_ in m],'category'])<={'S2','D2'} else '3D') for u,m in gr['members'].items()}
        u2=[u for u in gr['ul'] if cat_of[u]=='2D']
        if len(u2)<2: continue
        cat=ti.loc[gr['grp'],'category'] if ti.loc[gr['grp'],'category'] in ('S2','D2') else ti.loc[[q for q,_ in gr['members'][u2[0]]][0],'category']
        for j in u2:
            oth=[u for u in gr['ul'] if u!=j]
            o2=[u for u in oth if cat_of[u]=='2D']
            if label=='2D votes' and len(o2)<2: pv=None
            else: pv=rule_pv([gr['ul'][u] for u in oth])
            for i in o2:
                ai=gr['ul'][i]
                rows.append(dict(cat=cat,kind=gr['kind'],wt=len(gr['members'][i]),e_raw=ai-gr['ul'][j],e_pool=(pv if pv is not None else ai)-gr['ul'][j],ch=pv is not None))
    P=pd.DataFrame(rows); P['d']=S(P.e_pool)-S(P.e_raw)
    ws=lambda g: float(np.average(g.d,weights=g.wt)) if len(g) else float('nan')
    out[label]=dict(
        facts=dict(n=len(F),n_changed=int(F.changed.sum()),raw=round(F.raw.mean(),4),pooled=round(F.pool.mean(),4),
                   by_cat={c:dict(n=len(g),raw=round(g.raw.mean(),4),pooled=round(g.pool.mean(),4)) for c,g in F.groupby('cat')}),
        pseudo=dict(pairs_weight=int(P.wt.sum()),gain_per_row_all=round(ws(P),4),gain_per_changed_row=round(ws(P[P.ch]),4),
                    by_cat={c:round(ws(g[g.ch]),4) for c,g in P.groupby('cat')},by_kind={k:round(ws(g[g.ch]),4) for k,g in P.groupby('kind')},
                    raw_pseudo_mra=round(float(np.average(S(P.e_raw),weights=P.wt)),4),pooled_pseudo_mra=round(float(np.average(S(P.e_pool),weights=P.wt)),4)))
print(json.dumps(out,indent=1))
json.dump(out,open(W+'/final_eval.json','w'),indent=1)
