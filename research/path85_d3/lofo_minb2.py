"""LOFO for 2-base pools (rows with exactly 2 family bases for the asked quantity): new = geometric mean of the two
K-corrected ensemble votes when they agree within cap (log), else unchanged (K-corrected ens). Baseline = K-corrected ens."""
from build_repool import *
import itertools

def run(eq, facts, cap):
    F = facts.copy()
    F['method'] = ti.loc[F.qid, 'method'].values; F['src_type'] = ti.loc[F.qid, 'video_source'].values
    F['fact'] = F.line.str.strip().str.lower() + '|' + F.value.round(6).astype(str)
    def K(v, ex):
        g = F[(F.video_id == v) & ~F.fact.isin(ex) & F.kind.isin(('size', 'speed'))]
        if not len(g): return 0.0
        lk = np.log(g.value.values / ENS.reindex(g.qid).values); lk = lk[np.isfinite(lk)]
        return float(np.median(np.r_[lk, 0.0])) if len(lk) else 0.0
    def vote(p, ex):
        val = ENS[p]
        if is_direct(p) and ti.loc[p, 'tkind'] in ('size', 'speed'): val *= math.exp(K(ti.loc[p, 'video_id'], ex))
        return val * USC[p]
    rows = []
    for fact, g in F.groupby('fact'):
        ex = {fact}
        for r in g.itertuples():
            if r.cat not in ('D3', 'S3') or r.method != 'direct' or r.src_type == 'lab': continue
            q = r.qid; per = per_base_g(q, eq)
            if len(per) != 2: continue
            v = [math.log(vote(p, ex)) for p in per.values()]
            own = vote(q, ex) / USC[q]
            new = math.exp(np.mean(v)) / USC[q] if abs(v[0] - v[1]) <= cap else own
            rows.append(dict(cat=r.cat, qid=q, fam=ti.loc[q, 'fam'], base=own, new=new, m_base=mra1(own, r.value), m_new=mra1(new, r.value)))
    return pd.DataFrame(rows)

for cap in (0.3, 0.7, 9):
    for name, eq, facts in [('eq3', EQ3, A3), ('eq_ext', EQ, AX)]:
        L = run(eq, facts, cap)
        if not len(L): print(cap, name, 'no rows'); continue
        ch = ~np.isclose(L.base, L.new, rtol=0.01)
        print('cap', cap, name, 'rows', len(L), L.groupby('cat').size().to_dict(), 'fams', L.fam.nunique(), 'base %.3f new %.3f' % (L.m_base.mean(), L.m_new.mean()),
              'changed', ch.sum(), 'delta', np.round(boot_delta(L.m_new, L.m_base, L.fam), 3))
