"""LOFO mirroring the candidate exactly: probe-5 groups (eq3) and facts (transfers3) for SIM_P-style pools,
probe-7b groups (eq_ext) and facts (ext) for 7b pools. Held-out fact excluded from every member's K.
cur  = pool over bases of K-corrected run-1 votes (min 3 bases; else K-corrected run 1), times the row's ens/run1
new  = pool over bases of K-corrected 3-run-ensemble votes (min 3 bases; else K-corrected ens)."""
from build_repool import *

def lofo(eq, facts):
    F = facts.copy()
    F['method'] = ti.loc[F.qid, 'method'].values
    F['src_type'] = ti.loc[F.qid, 'video_source'].values
    F['fact'] = F.line.str.strip().str.lower() + '|' + F.value.round(6).astype(str)
    def K(v, ex, col):
        g = F[(F.video_id == v) & ~F.fact.isin(ex) & F.kind.isin(('size', 'speed'))]
        if not len(g): return 0.0
        lk = np.log(g.value.values / col.reindex(g.qid).values); lk = lk[np.isfinite(lk)]
        return float(np.median(np.r_[lk, 0.0])) if len(lk) else 0.0
    def vote(p, ex, col):
        val = col[p]
        if is_direct(p) and ti.loc[p, 'tkind'] in ('size', 'speed'):
            val *= math.exp(K(ti.loc[p, 'video_id'], ex, col))
        return val * USC[p]
    rows = []
    for fact, g in F.groupby('fact'):
        ex = {fact}
        for r in g.itertuples():
            if r.cat != 'D3' or r.method != 'direct' or r.src_type == 'lab': continue
            q = r.qid
            per = per_base_g(q, eq)
            if len(per) >= 3:
                c = gmed([vote(p, ex, V3) for p in per.values()]) / USC[q] * ENS[q] / V3[q]
                n = gmed([vote(p, ex, ENS) for p in per.values()]) / USC[q]
            else:
                c = vote(q, ex, V3) / USC[q] * ENS[q] / V3[q]
                n = vote(q, ex, ENS) / USC[q]
            rows.append(dict(qid=q, fam=ti.loc[q, 'fam'], kind=r.kind, nb=len(per), V=r.value, ens=ENS[q], cur=c, new=n,
                             m_ens=mra1(ENS[q], r.value), m_cur=mra1(c, r.value), m_new=mra1(n, r.value)))
    return pd.DataFrame(rows)

for name, eq, facts in [('probe5 groups (eq3, transfers3)', EQ3, A3), ('7b groups (eq_ext, ext facts)', EQ, AX)]:
    L = lofo(eq, facts)
    ch = ~np.isclose(L.cur, L.new, rtol=0.01)
    print(name, 'rows', len(L), 'fams', L.fam.nunique(), 'ens %.3f cur %.3f new %.3f' % (L.m_ens.mean(), L.m_cur.mean(), L.m_new.mean()))
    print('   new-cur', np.round(boot_delta(L.m_new, L.m_cur, L.fam), 4), ' changed>1%:', ch.sum(), ' per changed row %+.3f' % (L.m_new - L.m_cur)[ch].mean(),
          ' wins/losses', int(((L.m_new - L.m_cur)[ch] > 0).sum()), int(((L.m_new - L.m_cur)[ch] < 0).sum()))
    print('   by fam', (L.m_new - L.m_cur).groupby(L.fam).sum().round(2).to_dict())
    L.to_pickle(OUT / ('lofo_build_%s.pkl' % name.split()[0]))
