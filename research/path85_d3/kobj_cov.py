"""How many D3 non-lab rows with < 3 pool bases have another dimension of the same object (same clip) that is a stated
fact or a >=3-base pool?  (potential reach of a consensus same-object scale)."""
from lofo import *
from qp.geometry import name_score
R = pd.read_pickle(OUT / 'repool_D3.pkl')
facts_q = set(A.qid)
def same(a, b): return max(name_score(x, y) for x in str(a).split('|') for y in str(b).split('|')) >= 0.6
rows = []
for q, r in R.iterrows():
    if r.fact or r.method != 'direct' or r.kind != 'size' or r.nb >= 3: continue
    v = r.video; obj = ti.loc[q, 'tobj']
    sib = ti[(ti.video_id == v) & (ti.tkind == 'size') & (ti.index != q)]
    sib = sib[[same(o, obj) for o in sib.tobj]]
    anch = [p for p in sib.index if p in facts_q or (p in R.index and R.loc[p, 'nb'] >= 3)]
    rows.append(dict(qid=q, video=v, obj=obj, nb=r.nb, n_same=len(sib), n_anchor=len(anch), val=r.val))
X = pd.DataFrame(rows)
print('size rows nb<3:', len(X), ' with same-object sibling:', (X.n_same > 0).sum(), ' with anchored sibling:', (X.n_anchor > 0).sum(),
      ' scored:', ((X.n_anchor > 0) & X.val.isna()).sum())
print(X[X.n_anchor > 0].to_string())
