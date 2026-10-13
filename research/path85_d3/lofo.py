"""Leave-one-fact-out (LOFO) on exact stated facts, 3-run ensemble era.
Families / equivalence / transfers: Track A extended scene graph (probe 7b; eq_ext.pkl, transfers_ext.pkl).
For each stated fact (line+value) and each direct-routed D3/S3 non-lab row it answers, the fact is held out of K
(and its rows are never used as pool votes with their fact value: votes are raw model answers), and the row is
predicted by several methods. Scored with qp.mra.item_scores against the stated value. Label-free (test inputs)."""
from common import *
import pickle, itertools
SP = '/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
E = SP + '/ext/d3rest/work'
TS = pd.read_pickle(E + '/TS_ext.pkl'); ti = TS.set_index('qid')
EQ = pickle.load(open(E + '/eq_ext.pkl', 'rb'))
A = pd.read_pickle(E + '/transfers_ext.pkl'); A = A[~A.conflict].copy()
A['kind'] = ti.loc[A.qid, 'tkind'].values; A['method'] = ti.loc[A.qid, 'method'].values
A['src_type'] = ti.loc[A.qid, 'video_source'].values
A['fact'] = A.line.str.strip().str.lower() + '|' + A.value.round(6).astype(str)
D = runs_direct().reindex(ti.index)
V3 = ti.v3
nl3 = (ti.video_type.str[1] == '3') & (ti.video_source != 'lab')
# per-run values: 3D non-lab rows use each run's direct answer; other rows (2D geometry siblings) use v3 for all runs
RV = pd.DataFrame({r: D[r].where(nl3 & (ti.method == 'direct'), np.nan) for r in RUNS})
for r in RUNS:
    RV[r] = RV[r].fillna(V3)
ENS = lmed(RV)
from qp.parse import canonical_unit, _UNITS
def usc(q):
    cu = canonical_unit(ti.loc[q, 'target_unit'] or 'm') or 'm'
    return _UNITS[cu][0] if cu in _UNITS else 1.0
USC = {q: usc(q) for q in ti.index}
byv = {v: g for v, g in A.groupby('video_id')}

def clipK(v, ex, col, kinds=('size', 'speed')):
    g = byv.get(v)
    if g is None: return 0.0
    g = g[~g.fact.isin(ex) & g.kind.isin(kinds)]
    if not len(g): return 0.0
    base = col.reindex(g.qid).values
    lk = np.log(g.value.values / base)
    lk = lk[np.isfinite(lk)]
    return float(np.median(np.r_[lk, 0.0])) if len(lk) else 0.0

def per_base(q, excl_same_base=True):
    me = ti.loc[q]; per = {}
    for p in EQ[q]:
        b = ti.loc[p, 'base']
        if excl_same_base and b == me.base and p != q: continue
        v = ti.loc[p, 'video_id']; rank = 0 if v == b else 1
        if b not in per or rank < per[b][0]: per[b] = (rank, p)
    return {b: x[1] for b, x in per.items()}

def is_direct(p):
    return ti.loc[p, 'method'] == 'direct'

def kcorr(p, ex, col, useK):
    val = col[p]
    if useK and is_direct(p) and ti.loc[p, 'tkind'] in ('size', 'speed'):
        val = val * math.exp(clipK(ti.loc[p, 'video_id'], ex, col))
    return val

def gmed(v):
    v = np.array([x for x in v if x and x > 0 and np.isfinite(x)])
    return float(np.exp(np.median(np.log(v)))) if len(v) else np.nan

def trim_mean(v, tau=0.15):
    v = np.log(np.array([x for x in v if x and x > 0 and np.isfinite(x)]))
    if not len(v): return np.nan
    m = np.median(v); k = v[np.abs(v - m) <= tau]
    return float(np.exp(k.mean() if len(k) else m))

def predict(q, ex, method, minb=3):
    """methods: raw1, ens, cur (KP on v1 x ens/v1), KPens, KPruns (votes = base x run, K per run), variants."""
    per = per_base(q)
    s = USC[q]
    if method == 'raw1': return V3[q]
    if method == 'ens': return ENS[q]
    if method == 'Kens': return kcorr(q, ex, ENS, True)
    if method in ('cur', 'curP'):
        useK = method == 'cur'
        if len(per) >= minb:
            v = gmed([kcorr(p, ex, V3, useK) * USC[p] for p in per.values()]) / s
        else:
            v = kcorr(q, ex, V3, useK)
        return v * ENS[q] / V3[q] if is_direct(q) else v
    if method in ('KPens', 'Pens', 'KPens_tm', 'KPens_mean'):
        useK = method != 'Pens'
        if len(per) >= minb:
            votes = [kcorr(p, ex, ENS, useK) * USC[p] for p in per.values()]
            if method == 'KPens_tm': return trim_mean(votes) / s
            if method == 'KPens_mean': return float(np.exp(np.mean(np.log(votes)))) / s
            return gmed(votes) / s
        return kcorr(q, ex, ENS, useK)
    if method in ('KPruns', 'KPruns_tm'):
        if len(per) >= minb:
            votes = []
            for p in per.values():
                for r in RUNS:
                    votes.append(kcorr(p, ex, RV[r], True) * USC[p])
            return (trim_mean(votes) if method.endswith('tm') else gmed(votes)) / s
        return kcorr(q, ex, ENS, True)
    raise ValueError(method)

METHODS = ['raw1', 'ens', 'Kens', 'cur', 'curP', 'Pens', 'KPens', 'KPens_tm', 'KPens_mean', 'KPruns', 'KPruns_tm']

def run(cats=('D3',), minb=3, methods=METHODS):
    rows = []
    for fact, g in A.groupby('fact'):
        ex = {fact}
        for r in g.itertuples():
            if r.cat not in cats or r.method != 'direct' or r.src_type == 'lab': continue
            row = dict(cat=r.cat, qid=r.qid, video=r.video_id, fam=ti.loc[r.qid, 'fam'], kind=r.kind, V=r.value, fact=fact,
                       nb=len(per_base(r.qid)))
            for m in methods:
                p = predict(r.qid, ex, m, minb)
                row[m] = mra1(p, r.value)
                row['p_' + m] = p
            rows.append(row)
    return pd.DataFrame(rows)

if __name__ == '__main__':
    pd.set_option('display.width', 250)
    for cats in (('D3',), ('S3',)):
        for mb in (3, 2):
            R = run(cats, mb)
            print(cats, 'minb', mb, 'n', len(R), 'facts', R.fact.nunique(), 'fams', R.fam.nunique())
            print('  row mean ', R[METHODS].mean().round(3).to_dict())
            # equal weight per fact
            print('  fact mean', R.groupby('fact')[METHODS].mean().mean().round(3).to_dict())
            print('  fam mean ', R.groupby('fam')[METHODS].mean().mean().round(3).to_dict())
            for a, b in [('KPens', 'cur'), ('KPruns', 'cur'), ('KPens_tm', 'cur'), ('Kens', 'ens'), ('KPens', 'KPruns')]:
                print('   ', a, '-', b, np.round(boot_delta(R[a], R[b], R.fam), 4))
            R.to_pickle(OUT / f"lofo_{cats[0]}_mb{mb}.pkl")
