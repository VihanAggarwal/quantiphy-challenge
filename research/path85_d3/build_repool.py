"""Candidate: re-derive the D3 non-lab family pools (P), clip scales (K) and same-object scales (KOBJ) on the 3-run
ensemble, instead of probe 7a's 'v1-based value x own ens/v1 ratio' (which re-injects each row's own run noise into a
pooled value: e.g. qid 1224 curb pooled to 0.23 in probe 5, then x1.89 -> 0.434 in 7a while its group stays 0.23).
Same rule per row as the current submission, same groups and facts as the build that set it:
  probe 5 SIM_P / SIM_K rows: eq3 groups, K from transfers3 facts; probe 7b P / P_RE / KOBJ rows: eq_ext, ext facts.
Only the votes change: each base votes its 3-run ensemble median (instead of run 1), K from ensemble fact misses.
Min 3 bases as before. Segmented twins re-copy their original. Test inputs + cached runs only; no API.
Usage: build_repool.py [--write]"""
import sys, re
from lofo import *
SPW = SP + '/big/scenegraph/work'
EQ3 = pickle.load(open(SPW + '/eq3.pkl', 'rb'))
A3 = pd.read_pickle(SPW + '/transfers3.pkl'); A3 = A3[~A3.conflict].copy()
A3['kind'] = ti.loc[A3.qid, 'tkind'].values
AX = A.copy()
R = pd.read_pickle(OUT / 'rules_D3.pkl')
cur = read_sub()
S = {k: read_sub(ROOT / f'submissions/trackA_{k}.csv') for k in ['v3_best_per_category', 'probe5_families_merged',
     'probe7a_p5_ensemble3dnl', 'probe7b_p5_ens_famext']}
SP5 = pd.read_csv(SP + '/merge/D3/decisions.csv').set_index('qid').chosen_source
SPX = pd.read_csv(SP + '/ext/d3rest/decisions_ext.csv').set_index('qid').rule

def changed(a, b, q):
    return not np.isclose(S[a][q], S[b][q], rtol=1e-9)

def Kclip(v, facts, col=ENS, kinds=('size', 'speed')):
    g = facts[(facts.video_id == v) & facts.kind.isin(kinds)]
    if not len(g): return 0.0
    lk = np.log(g.value.values / col.reindex(g.qid).values)
    lk = lk[np.isfinite(lk)]
    return float(np.median(np.r_[lk, 0.0])) if len(lk) else 0.0

KO = {v: Kclip(v, A3) for v in ti.video_id.unique()}
KX = {v: Kclip(v, AX) for v in ti.video_id.unique()}

def per_base_g(q, eq):
    me = ti.loc[q]; per = {}
    for p in eq[q]:
        b = ti.loc[p, 'base']
        if b == me.base and p != q: continue
        v = ti.loc[p, 'video_id']; rank = 0 if v == b else 1
        if b not in per or rank < per[b][0]: per[b] = (rank, p)
    return {b: x[1] for b, x in per.items()}

def vote(p, K):
    val = ENS[p]
    if is_direct(p) and ti.loc[p, 'tkind'] in ('size', 'speed'):
        val = val * math.exp(K[ti.loc[p, 'video_id']])
    return val * USC[p]

def actual_rule(q):
    if changed('probe7b_p5_ens_famext', 'probe7a_p5_ensemble3dnl', q):
        return '7b:' + str(SPX.get(q, '?'))
    if changed('probe5_families_merged', 'v3_best_per_category', q):
        return '5:' + str(SP5.get(q, '?'))
    return 'none'

new, why, rules = {}, {}, {}
for q, r in R.iterrows():
    rule = actual_rule(q); rules[q] = rule
    if not np.isclose(cur[q], S['probe7b_p5_ens_famext'][q], rtol=1e-9):
        continue                                       # changed after 7b (sim3d motion facts etc.): keep
    if rule == '5:SIM_P':
        per = per_base_g(q, EQ3)
        if len(per) >= 3:
            new[q] = gmed([vote(p, KO) for p in per.values()]) / USC[q]; why[q] = 'P_ens'
    elif rule in ('7b:P', '7b:P_RE'):
        per = per_base_g(q, EQ)
        if len(per) >= 3:
            new[q] = gmed([vote(p, KX) for p in per.values()]) / USC[q]; why[q] = 'P_ens'
    elif rule == '5:SIM_K':
        new[q] = ENS[q] * math.exp(KO[r.video]); why[q] = 'K_ens'
    elif rule == '7b:KOBJ' and '--kobj' in sys.argv:          # off by default: 1 validation row says ens-KOBJ is worse
        from qp.geometry import name_score
        obj = ti.loc[q, 'tobj']
        g = AX[(AX.video_id == r.video) & (AX.kind == 'size')]
        g = g[[max(name_score(a, b) for a in str(obj).split('|') for b in str(ti.loc[x, 'tobj']).split('|')) >= 0.6 for x in g.qid]]
        if len(g):
            new[q] = ENS[q] * float(np.exp(np.median(np.log(g.value.values / ENS.reindex(g.qid).values)))); why[q] = 'KOBJ_ens'
key = TS.assign(nq=TS.question.map(lambda s: re.sub(r'\s+', ' ', str(s).strip().lower()).rstrip('?. ')))
orig_of = {}
for _, g in key[key.category == 'D3'].groupby(['base', 'nq', 'prior', 'depth_info', 'target_unit']):
    o = g[~g.video_id.str.endswith('_segmented')]; s = g[g.video_id.str.endswith('_segmented')]
    if len(o) == 1:
        for x in s.qid: orig_of[int(x)] = int(o.qid.iloc[0])
for q in R.index:
    if ('TWIN' in rules[q]) and q in orig_of and orig_of[q] in new and np.isclose(cur[q], cur[orig_of[q]], rtol=1e-9):
        new[q] = new[orig_of[q]]; why[q] = 'TWIN<' + why[orig_of[q]]
N = pd.Series(new, dtype=float); W = pd.Series(why)
print('rule counts', pd.Series(rules).value_counts().to_dict())
chg = N[~np.isclose(N, cur.reindex(N.index), rtol=1e-6)]
lr = np.log(chg / cur.reindex(chg.index))
print('rows recomputed', len(N), 'changed', len(chg), 'by rule', W[chg.index].value_counts().to_dict())
print('|log change| quantiles', np.round(lr.abs().quantile([.5, .75, .9, 1]).values, 3), ' >5%:', (lr.abs() > .05).sum(), ' >10%:', (lr.abs() > .1).sum())
vl = val_labels()
D = pd.DataFrame(dict(video=ti.loc[chg.index, 'video_id'], kind=ti.loc[chg.index, 'tkind'], rule=pd.Series(rules)[chg.index],
                      how=W[chg.index], v1=V3[chg.index], ens=ENS[chg.index], cur=cur[chg.index], new=chg, lr=lr, val=vl.reindex(chg.index)))
D['q'] = ti.loc[chg.index, 'question'].str[:60]
D.to_csv(OUT / 'repool_changes.csv')
v = D[D.val.notna()]
if len(v):
    v = v.assign(m_cur=[mra1(a, b) for a, b in zip(v.cur, v.val)], m_new=[mra1(a, b) for a, b in zip(v.new, v.val)])
    print('validation overlap rows changed', len(v)); print(v[['video', 'rule', 'cur', 'new', 'val', 'm_cur', 'm_new']].round(3).to_string())
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 300)
print(D[D.lr.abs() > 0.05].sort_values('lr').round(3).to_string())
if '--write' in sys.argv:
    sub = pd.read_csv(BASE, float_precision='round_trip')
    sub['parsed_value'] = [float(chg[q]) if q in chg.index else v for q, v in zip(sub.id, sub.parsed_value)]
    tmpl = pd.read_csv(ROOT / 'data/submission_template/quantiphy_submission_template.csv')
    assert list(sub.id) == list(tmpl.id) and len(sub) == 3289
    assert np.isfinite(sub.parsed_value).all() and (sub.parsed_value > 0).all()
    assert set(ti.loc[chg.index, 'category']) <= {'D3'}
    _, flog = pp.apply_rules(read_sub().reindex(ti.index), load_split('test'), rules=('facts', 'motionfam', 'freefall'))
    fact_rows = set(flog[flog.applied].qid.astype(int))
    assert not (set(chg.index) & fact_rows), 'a stated-fact row changed'
    out = ROOT / 'submissions/trackA_cand_d3repool_on_physb2.csv'
    sub.to_csv(out, index=False)
    print('wrote', out, 'changed D3 rows', len(chg), 'scored (non-val-overlap)', int(D.val.isna().sum()))
