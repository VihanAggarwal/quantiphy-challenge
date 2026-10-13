"""D3 extension on top of probe 5 (submissions/trackA_probe5_families_merged.csv): only D3 rows change.

Inputs (test inputs only; validation answers are used ONLY to measure, never to set a value):
  work/TS_ext.pkl          extended scene families (extfam.py: scene graph + vocabulary links + segmented frame link
                           + eye-verified identical-prior link, all checked on contact sheets in sheets/ and frames/)
  work/transfers_ext.pkl   stated facts transferred inside extended families (graph.transfers3, unchanged rule)
  work/eq_ext.pkl          equivalence groups (pool2.equiv_groups2, unchanged rule) on extended families
Rules (each D3 row takes the first that applies; rows already changed by probe 5 are only touched by T):
  T     a question asking a quantity a family clip states as its prior takes the stated value (probe-5 T rule, new links).
  LABFACT a lab prop size question takes the size a lab prior states for that prop (probe-5 LABFACT rule, which only ran
        on props asked in >= 2 events; here also single-event props: the 0018 tennis ball takes the stated 6.7 cm).
  P     series pooling (probe-5 P rule): direct-routed sim size/speed answers untouched by probe 5 take the geometric
        median over >= 3 distinct family bases of the K-corrected answers to the equivalent question; speed rows the
        probe-5 K guard dropped (family states the object's speed and pooling/K moves away from it) are skipped.
  P_RE  probe-5 pooled rows (SIM_P) re-pooled on the extended families, so every row of one equivalence group carries
        the same pooled value (12 rows, all moves < 10%).
  KOBJ  same-object scale: a direct sim SIZE answer untouched so far, in a clip whose stated facts include another
        dimension of the SAME object (name score >= 0.6), is multiplied by the median stated/Claude ratio of those facts
        (Claude's model of one object is right in shape but wrong in scale; pairwise LOFO on stated facts .414 -> .614).
  HUMAN a clip whose direct answer puts a person's height outside 1.4-2.2 m while geometry measures it inside that range
        has a wrong direct metric scale: that clip's direct-routed size/speed answers take the geometry value when one
        exists (only simulation_0032_segmented: 15.7 m person, 2.45 m ball, 25 m/s throw -> 1.76 m, 0.28 m, 2.64 m/s).
  TWIN  a pixel-aligned *_segmented twin takes its original's final value when the original changed here (probe-5 twin
        rule; the 0017 pair stays excluded as in probe 5) unless the twin carries its own stated fact.
Variants: A = T; B = T+P; C = T+P+KOBJ+HUMAN.
"""
import sys, os, re, json, pickle, math
SP = '/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
EXT = SP + '/ext/d3rest/verified/rebuild'; W = SP + '/big/scenegraph/work'; R = '/home/user/quantiphy-challenge'
sys.path.insert(0, R); sys.path.insert(0, W)
import numpy as np, pandas as pd
from qp.mra import item_scores
from qp.geometry import name_score
from qp.parse import canonical_unit, _UNITS
from pool2 import per_base_values, gmed

def mra(p, g): return float(item_scores([p], [g])[0])

t = pd.read_pickle(EXT + '/work/TS_ext.pkl'); ti = t.set_index('qid')
A = pd.read_pickle(EXT + '/work/transfers_ext.pkl'); A = A[~A.conflict].copy()
eq = pickle.load(open(EXT + '/work/eq_ext.pkl', 'rb'))
P5 = pd.read_csv(R + '/submissions/trackA_probe5_families_merged.csv')
p5 = dict(zip(P5.id, P5.parsed_value))
V3 = pd.read_csv(R + '/submissions/trackA_v3_best_per_category.csv'); v3 = dict(zip(V3.id, V3.parsed_value))
run = pd.read_csv(R + '/runs/test_v1_high_854/test.csv').set_index('id')
dec = pd.read_csv(SP + '/merge/D3/decisions.csv').set_index('qid')
src5 = dec.chosen_source.reindex(ti.index).fillna('v3').to_dict()
summ5 = json.load(open(SP + '/merge/D3/build_summary.json'))
K_DROP5 = set(summ5['k_dropped'])
D3 = [q for q in P5.id if ti.loc[q, 'category'] == 'D3']
untouched = {q for q in D3 if np.isclose(p5[q], v3[q], rtol=1e-9)}

A['v3'] = A.qid.map(v3)
A['lk'] = np.log(A.value / A.v3); A['kind'] = ti.loc[A.qid, 'tkind'].values; A['obj'] = ti.loc[A.qid, 'tobj'].values
Tval = {r.qid: r.value for r in A.itertuples()}
Tsrc = {r.qid: f'{r.line.strip()} @{r.src} ({r.why})' for r in A.itertuples()}

def is_direct(q):
    d = pd.to_numeric(ti.loc[q, 'direct'], errors='coerce')
    return bool(d > 0 and abs(v3[q] / d - 1) < 1e-6)
def usc(q):
    cu = canonical_unit(ti.loc[q, 'target_unit'] or 'm') or 'm'
    return _UNITS[cu][0] if cu in _UNITS else 1.0
# probe-5 K (median of the clip's fact log-ratios with a 0), on the extended facts
KC = {}
for v, g in A[A.kind.isin(('size', 'speed'))].groupby('video_id'):
    KC[v] = float(np.median(np.r_[g.lk.values, 0.0]))
def corrected(q):
    val = v3[q]
    if is_direct(q) and ti.loc[q, 'tkind'] in ('size', 'speed'): val *= math.exp(KC.get(ti.loc[q, 'video_id'], 0.0))
    return val
def pooled(q, minb=3):
    per = per_base_values(ti, eq, q, col='v3', include_self=True)
    if len(per) < minb: return None, per
    return gmed([corrected(x[2]) * usc(x[2]) for x in per.values()]) / usc(q), per

def same_obj(a, b): return max(name_score(x, y) for x in str(a).split('|') for y in str(b).split('|')) >= 0.6

HUMAN = re.compile(r'height of the (?:\w+ )?(?:person|man|woman|human|pedestrian|boy|girl|player)\b', re.I)
def human_clips():
    out = {}
    for q in D3:
        r = ti.loc[q]
        if not r.video_id.startswith('simulation') or not HUMAN.search(r.question) or not is_direct(q): continue
        d = v3[q] * usc(q); g = pd.to_numeric(run.loc[q, 'geo_value'], errors='coerce') * usc(q)
        if not (1.4 <= d <= 2.2) and np.isfinite(g) and 1.4 <= g <= 2.2:
            out[r.video_id] = (q, d, g)
    return out

def twin_pairs():
    tt = t[t.category == 'D3'].copy()
    tt['nq'] = tt.question.map(lambda s: re.sub(r'\s+', ' ', str(s).strip().lower()).rstrip('?. '))
    pairs = {}
    for _, g in tt.groupby(['base', 'nq', 'prior', 'depth_info', 'target_unit']):
        o = g[~g.video_id.str.endswith('_segmented')]; s = g[g.video_id.str.endswith('_segmented')]
        if len(o) == 1 and len(s) >= 1:
            for q in s.qid: pairs[int(q)] = int(o.qid.iloc[0])
    return pairs
TWIN_EXCLUDED = set(summ5['twin_pairs_excluded'])  # probe 5 left the 0017 pair out (rotated view)

def labfacts():
    sys.path.insert(0, W)
    from rules import dimnorm, stated_si
    lab = t[t.video_source == 'lab']
    F = []
    for (v, p), g in lab.groupby(['video_id', 'prior']):
        r = g.iloc[0]
        if r.pkind != 'size': continue
        si = stated_si(p, r.pobj)
        if si: F.append((r.pobj, r.pdim, si, p.strip()))
    out = {}
    for q in D3:
        r = ti.loc[q]
        if r.video_source != 'lab' or r.tkind != 'size': continue
        m = [(si, line) for po, pd_, si, line in F if dimnorm(pd_) == dimnorm(r.tdim)
             and max(name_score(a, po) for a in str(r.tobj).split('|')) >= 0.8]
        if m and len({round(x[0], 6) for x in m}) == 1:
            out[q] = (m[0][0] / usc(q), m[0][1])
    return out

def build(useP=False, useKOBJ=False, useHUMAN=False, usePRE=None):
    if usePRE is None: usePRE = useP
    new, why, note = dict(p5), {}, {}
    # T
    for q in D3:
        if q in Tval and not np.isclose(Tval[q], p5[q], rtol=1e-9):
            if src5.get(q, 'v3').endswith('FACT'):
                note[q] = 'conflict with probe-5 fact, kept probe 5'; continue
            new[q] = Tval[q]; why[q] = 'T'; note[q] = Tsrc[q]
    # LABFACT (single-event props)
    for q, (val, line) in labfacts().items():
        if q in why or np.isclose(val, p5[q], rtol=1e-9) or src5.get(q, 'v3') not in ('v3',): continue
        new[q] = val; why[q] = 'LABFACT'; note[q] = 'stated lab prior: ' + line
    # P
    if useP:
        for q in sorted(untouched):
            if q in why or q in Tval or q in K_DROP5: continue
            r = ti.loc[q]
            if not r.video_id.startswith('simulation') or r.tkind not in ('size', 'speed') or not is_direct(q): continue
            pv, per = pooled(q)
            if pv is None or not np.isfinite(pv) or np.isclose(pv, p5[q], rtol=1e-9): continue
            new[q] = pv; why[q] = 'P'
            note[q] = 'pool over %d bases: ' % len(per) + ', '.join('%s=%.4g' % (ti.loc[x[2], 'video_id'], corrected(x[2])) for x in per.values())
    # P_RE
    if usePRE:
        for q in D3:
            if q in why or q in Tval or src5.get(q) != 'SIM_P': continue
            pv, per = pooled(q)
            if pv is None or not np.isfinite(pv) or np.isclose(pv, p5[q], rtol=1e-9): continue
            new[q] = pv; why[q] = 'P_RE'
            note[q] = 're-pool over %d bases (probe 5 %.4g): ' % (len(per), p5[q]) + ', '.join('%s=%.4g' % (ti.loc[x[2], 'video_id'], corrected(x[2])) for x in per.values())
    # KOBJ
    if useKOBJ:
        for q in sorted(untouched):
            if q in why or q in Tval: continue
            r = ti.loc[q]
            if not r.video_id.startswith('simulation') or r.tkind != 'size' or not is_direct(q): continue
            f = A[(A.video_id == r.video_id) & (A.kind == 'size') & (A.qid != q)]
            f = f[[same_obj(o, r.tobj) for o in f.obj]]
            if not len(f): continue
            k = float(np.median(f.lk.values))
            new[q] = v3[q] * math.exp(k); why[q] = 'KOBJ'
            note[q] = 'x%.3f from same-object facts: ' % math.exp(k) + '; '.join(f.line.str.strip())
    # HUMAN
    if useHUMAN:
        for v, (hq, d, g) in human_clips().items():
            for q in D3:
                if ti.loc[q, 'video_id'] != v or q in why or q in Tval or q not in untouched: continue
                if ti.loc[q, 'tkind'] not in ('size', 'speed') or not is_direct(q): continue
                gv = pd.to_numeric(run.loc[q, 'geo_value'], errors='coerce')
                if not (np.isfinite(gv) and gv > 0): continue
                new[q] = float(gv); why[q] = 'HUMAN'
                note[q] = 'direct person height %.3g m implausible, geometry %.3g m: clip takes geometry (%.4g -> %.4g)' % (d, g, v3[q], gv)
    # TWIN sync
    for tq, oq in twin_pairs().items():
        if ti.loc[tq, 'video_id'] in TWIN_EXCLUDED: continue
        if oq not in why: continue
        if tq in Tval and why.get(tq) == 'T' and why.get(oq) != 'T': continue
        if not np.isclose(new[tq], new[oq], rtol=1e-12):
            note[tq] = 'twin of %d (%s); own rule %s %.4g' % (oq, why[oq], why.get(tq, 'none'), new[tq])
            new[tq] = new[oq]; why[tq] = 'TWIN<' + why[oq]
    return new, why, note

# measurement: known rows (validation GT on the same test clip/question), suspects excluded
m = pd.read_csv(SP + '/hyp/S2/val_test_map.csv').sort_values('sim').drop_duplicates('tqid', keep='last'); m = m[m.sim >= 0.9]
SUS = {403, 2349, 2607, 3049, 3051, 1123, 1130, 1354, 1355, 3054, 139, 2276}; m = m[~m.vqid.isin(SUS)]
known = {q: a for q, a in zip(m.tqid, m.answer) if q in set(D3)}

def write(new, path):
    out = P5[['id']].copy()
    out['parsed_value'] = [new[q] if ti.loc[q, 'category'] == 'D3' else p5[q] for q in P5.id]
    tmpl = pd.read_csv(R + '/data/submission_template/quantiphy_submission_template.csv')
    assert list(out.id) == list(tmpl.id) and len(out) == 3289
    pv = out.parsed_value.astype(float)
    assert np.isfinite(pv).all() and (pv > 0).all()
    ch = ~np.isclose(pv.values, P5.parsed_value.values, rtol=1e-12)
    assert set(ti.loc[out.id[ch], 'category']) <= {'D3'}
    out.to_csv(path, index=False)
    r = pv[ch].values / P5.parsed_value[ch].values
    return int(ch.sum()), float(np.median(r)) if ch.any() else 1.0

if __name__ == '__main__':
    VARS = {'A_T': dict(), 'B_TP': dict(useP=True), 'C_TP_KOBJ_HUMAN': dict(useP=True, useKOBJ=True, useHUMAN=True)}
    res = {}; rows = []
    for name, cfg in VARS.items():
        new, why, note = build(**cfg)
        path = EXT + f'/D3ext_{name}.csv'
        n, med = write(new, path)
        ch = [q for q in D3 if not np.isclose(new[q], p5[q], rtol=1e-12)]
        kq = list(known); k0 = np.mean([mra(p5[q], known[q]) for q in kq]); k1 = np.mean([mra(new[q], known[q]) for q in kq])
        kch = [(q, round(p5[q], 4), round(new[q], 4), known[q], why.get(q)) for q in kq if q in ch]
        res[name] = dict(csv=path, rows_changed=n, median_ratio=med, by_rule=pd.Series([why[q] for q in ch]).value_counts().to_dict(),
                         known_n=len(kq), known_p5=round(k0, 4), known_new=round(k1, 4), known_changed=kch,
                         T_if_right_gain=round(sum(1 - mra(p5[q], new[q]) for q in ch if why[q] in ('T', 'TWIN<T')) / 969, 4))
        print(name, json.dumps(res[name], default=str))
        if name == 'C_TP_KOBJ_HUMAN':
            for q in ch:
                rows.append(dict(qid=q, video_id=ti.loc[q, 'video_id'], kind=ti.loc[q, 'tkind'], question=ti.loc[q, 'question'].strip(),
                                 p5=p5[q], new=new[q], ratio=new[q] / p5[q], rule=why[q], note=note.get(q, '')))
    pd.DataFrame(rows).sort_values(['rule', 'video_id']).to_csv(EXT + '/decisions_ext.csv', index=False)
    json.dump(res, open(EXT + '/build_summary.json', 'w'), indent=1, default=str)
