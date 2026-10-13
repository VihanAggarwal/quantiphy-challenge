"""LOFO: does weighting size-prior (S2/S3) votes over motion-prior (D2/D3) votes in the family pool help D3?"""
from lofo import *
CAT = ti.category

def pool_variant(q, ex, minb, mode):
    per = per_base(q)
    if len(per) < minb:
        return kcorr(q, ex, ENS, True)
    votes = [(kcorr(p, ex, ENS, True) * USC[p], CAT[p]) for p in per.values()]
    if mode == 'all':
        v = [x for x, _ in votes]
    elif mode == 'Sonly':
        v = [x for x, c in votes if c[0] == 'S'] or [x for x, _ in votes]
    elif mode == 'Sdouble':
        v = [x for x, c in votes] + [x for x, c in votes if c[0] == 'S']
    elif mode == 'no2D':
        v = [x for x, c in votes if c[1] == '3'] or [x for x, _ in votes]
    elif mode == '3Donly':
        v = [x for (x, c), p in zip(votes, per.values()) if c[1] == '3' or p == q]
        if len([1 for (x, c) in votes if c[1] == '3']) < minb: return kcorr(q, ex, ENS, True)
    return gmed(v) / USC[q]

rows = []
for fact, g in A.groupby('fact'):
    ex = {fact}
    for r in g.itertuples():
        if r.cat != 'D3' or r.method != 'direct' or r.src_type == 'lab': continue
        q = r.qid
        per = per_base(q)
        cats = [CAT[p] for p in per.values()]
        row = dict(qid=q, fam=ti.loc[q, 'fam'], kind=r.kind, nS=sum(c[0] == 'S' for c in cats), n2=sum(c[1] == '2' for c in cats), nb=len(per))
        for mode in ('all', 'Sonly', 'Sdouble', 'no2D', '3Donly'):
            row[mode] = mra1(pool_variant(q, ex, 3, mode), r.value)
        rows.append(row)
R = pd.DataFrame(rows)
print('n', len(R), 'rows with S votes', (R.nS > 0).sum(), 'rows with 2D votes', (R.n2 > 0).sum())
M = ['all', 'Sonly', 'Sdouble', 'no2D', '3Donly']
print(R[M].mean().round(3).to_dict())
print(R[R.nS > 0][M].mean().round(3).to_dict(), 'n', (R.nS > 0).sum())
for m in M[1:]:
    print(m, '-all', np.round(boot_delta(R[m], R['all'], R.fam), 4))
