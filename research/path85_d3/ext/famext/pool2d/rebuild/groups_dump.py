from eq import *
t=pd.read_pickle(W+'/T.pkl'); ti=t.set_index('qid')
eq=groups(t)
# connected components among 2D+3D, print those containing 2D
seen=set(); comps=[]
for q in eq:
    if q in seen: continue
    st=[q]; comp=set()
    while st:
        x=st.pop()
        if x in comp: continue
        comp.add(x); st.extend(eq.get(x,()))
    seen|=comp; comps.append(sorted(comp))
out=[]
for c in comps:
    g=ti.loc[c]
    if not g.category.isin(['S2','D2']).any(): continue
    g2=g[g.category.isin(['S2','D2'])]
    lv=np.log(g2.p5.astype(float))
    out.append((float(lv.max()-lv.min()), c))
out.sort(key=lambda x:-x[0])
import sys
kind=sys.argv[1] if len(sys.argv)>1 else 'size'
for sp,c in out:
    g=ti.loc[c]
    if g.tkind.iloc[0]!=kind: continue
    print(f'=== spread {sp:.3f} n={len(c)} {g.tkind.iloc[0]} {g.tobj.iloc[0]} {g.tdim.iloc[0]} t={g.ttime.iloc[0]}')
    for q,r in g.sort_values('video_id').iterrows():
        print(f'   {q:5d} {r.video_id:28s} {r.category} {r.prior[:45]:45s} p5={r.p5:.4g} dir={r.direct_value:.4g} {r.question[:60]}')
