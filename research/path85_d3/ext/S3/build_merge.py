"""Merged S3 variant for probe 5 (on top of v3) + the nosplit alternate + decisions table.

Reproducible from the input CSVs (no API, no replay, repo read-only):
  V3    submissions/trackA_v3_best_per_category.csv                       (base; every non-S3 row is copied from it)
  P4S3  hyp/final/S3_split_full_depthfix.csv                               (probe-4 S3: kind split, segtwin, s/x render,
                                                                            0034b<-0034a, 0040 decimal fix, depthfix)
  DF    hyp/S3/variants_labdirect/S3p3_direct_full.csv                     (the same P4 mechanisms WITHOUT the kind split;
                                                                            differs from P4S3 only on the 91 split rows)
  P4ALL submissions/trackA_probe4_s2twin_d2refineoff_s3split_d3fixes.csv   (D3/D2 lab answers used only as pool INPUTS)
  TL    big/scene_graph/S3_T_LABfix.csv                                    (T stated-fact transfer + LAB prop pooling of v3)
  SIB   big/priors_as_labels/S3_sibling_prior_transfer_noconflict.csv      (sibling-prior transfer, speed-conflict guard)
  + test inputs (qp.data.load_split('test')) and the scene-graph investigator's lab prop groups (imported read-only).

Pipeline per S3 row (mode 'split' = main, 'nosplit' = alternate):
  1. stage A = P4S3 (split) or DF (nosplit) over v3.
  2. LAB pooling re-based on stage A: lab size questions grouped by prop (scene-graph lab_size_groups; bare-noun
     groups skipped as in LABfix); each S3 answer -> geometric median of its own stage-A value and the base-render
     value of every other independent event (events whose values merely duplicate another event's are dropped,
     i.e. 0034b after rule (b)); LABfix guards kept (2 events >2x apart: skip; event >1.6x off the others: skip).
  3. Stated facts (policy 1): T (from TL, non-lab rows) and SIB values; T speeds that disagree with the clip's own
     answer by >2x are dropped (family facts conflict, see decisions); lab stated fact 'ping pong ball diameter'
     applied to the white-ball prop group once the clips' own inputs identify the white ball as the ping pong ball.
  4. Segmented twins re-copy the final answer of their original question (P4 segtwin pairs) unless the twin has its
     own stated value.
"""
import sys, os, re, json, pickle
sys.dont_write_bytecode = True
import numpy as np, pandas as pd

R = '/home/user/quantiphy-challenge'
SP = '/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
OUT = SP + '/merge/S3'
IN = dict(
    V3=R + '/submissions/trackA_v3_best_per_category.csv',
    P4S3=SP + '/hyp/final/S3_split_full_depthfix.csv',
    DF=SP + '/hyp/S3/variants_labdirect/S3p3_direct_full.csv',
    P4ALL=R + '/submissions/trackA_probe4_s2twin_d2refineoff_s3split_d3fixes.csv',
    TL=SP + '/big/scene_graph/S3_T_LABfix.csv',
    SIB=SP + '/big/priors_as_labels/S3_sibling_prior_transfer_noconflict.csv',
)
# ---- scene-graph lab prop groups (investigator modules, imported read-only) ----
W = SP + '/big/scenegraph/work'
_cwd = os.getcwd(); sys.path.insert(0, W); os.chdir(W)
import build as SG                                   # noqa: E402  (loads TS.pkl etc.)
import labpool2                                      # noqa: E402
labpool2.ti = SG.ti; labpool2.v3 = SG.v3
from labpool2 import lab_size_groups, lab_facts, usc  # noqa: E402
from rules import dimnorm                            # noqa: E402
os.chdir(_cwd)
sys.path.insert(0, R)
from qp.geometry import name_score                   # noqa: E402

t = SG.t; ti = SG.ti
CAT = ti.category
rd = lambda k: pd.read_csv(IN[k]).set_index('id').parsed_value
V3df = pd.read_csv(IN['V3'])
v3 = V3df.set_index('id').parsed_value
P4S3, DF, P4ALL, TL, SIB = rd('P4S3'), rd('DF'), rd('P4ALL'), rd('TL'), rd('SIB')
for k, s in dict(P4S3=P4S3, DF=DF, P4ALL=P4ALL, TL=TL, SIB=SIB).items():
    assert list(s.index) == list(v3.index), k
S3 = [q for q in v3.index if CAT[q] == 'S3']
S3set = set(S3)
ne = lambda a, b: not np.isclose(a, b, rtol=1e-9, atol=0)
SPLIT = {q for q in S3 if ne(P4S3[q], DF[q])}            # rows the kind split moved (lab size/distance)
assert all(ti.loc[q, 'video_source'] == 'lab' for q in SPLIT)

def gmed(vals):
    vals = [v for v in vals if v and v > 0 and np.isfinite(v)]
    return float(np.exp(np.median(np.log(vals)))) if vals else np.nan

def base_of(v):
    return re.sub(r'(_segmented|[sxX])$', '', v)

def normq(q):
    return re.sub(r'[^a-z0-9.]', '', str(q).lower())

# ---------------------------------------------------------------- LAB pooling (re-based)
LAB = t[(t.video_source == 'lab') & (t.tkind == 'size')]
NAMES = sorted({x.lower().strip() for o in LAB.tobj for x in str(o).split('|')})
def ambiguous(name):                                   # LABfix fix 1 (bare noun with a modified sibling name)
    n = name.lower().strip()
    if ' ' in n: return False
    return any(m != n and m.split()[-1] == n for m in NAMES)
GROUPS = lab_size_groups(t)

def lab_pool(stageA, log):
    """returns {S3 qid: (pooled value, group label, info)}"""
    val = lambda q: (stageA[q] if q in S3set else P4ALL[q]) * usc(q)      # SI
    out = {}
    for k, qs in GROUPS.items():
        g = ti.loc[qs]
        objs = sorted({x.lower().strip() for o in g.tobj for x in str(o).split('|')})
        label = '/'.join(objs) + ':' + str(g.tdim.iloc[0])
        if not any(q in S3set for q in qs): continue
        if any(ambiguous(o) for o in objs):
            log.append(('skip_ambiguous', label)); continue
        bases = sorted(set(g.base))
        rows_of = {b: [q for q in qs if ti.loc[q, 'base'] == b] for b in bases}
        bv = {}
        for b in bases:
            r = [q for q in rows_of[b] if ti.loc[q, 'video_id'] == b]
            bv[b] = val(r[0]) if r else gmed([val(q) for q in rows_of[b]])
        # independence: an event whose every S3 answer was REPLACED in stage A by a value of another event is a copy
        # (0034b after P4 rule b: its static answers are 0034a's), so it is not separate evidence for the pool
        copies = set()
        for b in bases:
            other_vals = [val(q) for x in bases if x != b for q in rows_of[x]]
            if other_vals and all(q in S3set and ne(stageA[q], v3[q]) and
                                  any(np.isclose(val(q), o, rtol=1e-9) for o in other_vals) for q in rows_of[b]):
                copies.add(b)
        indep = [b for b in bases if b not in copies]
        if copies: log.append(('copy_event_not_independent', label, sorted(copies)))
        if len(indep) == 2 and max(bv[b] for b in indep) / min(bv[b] for b in indep) > 2.0:
            log.append(('skip_spread2', label)); continue
        bad = set()
        for b in indep:
            others = [bv[x] for x in indep if x != b]
            if len(others) < 2: continue
            own = float(np.median([val(q) for q in rows_of[b]]))
            m = gmed(others)
            if max(own / m, m / own) > 1.6: bad.add(b)
        if bad: log.append(('skip_event_different_object', label, sorted(bad)))
        for q in qs:
            if q not in S3set: continue
            b = ti.loc[q, 'base']
            if b in bad: continue
            others = [bv[x] for x in indep if x != b]
            pooled = gmed(others + [val(q)]) / usc(q)
            out[q] = (pooled, label, dict(n_events=len(others) + 1,
                                          others={x: round(bv[x] / usc(q), 4) for x in indep if x != b}))
    return out

# ---------------------------------------------------------------- stated facts
LABFACTS = lab_facts(t)          # (prior object, dimension, SI value, clip) from lab priors

def depth_names(di):
    return {m.group(1).replace('_', ' ').lower() for m in re.finditer(r'distance_(.+?)_camera', str(di))}

def clip_names(v):
    g = t[t.video_id == v]
    qn = set()
    for o in g.tobj: qn |= {x.lower().strip() for x in str(o).split('|')}
    for qq in g.question:                         # objects named in question text
        qn |= {f.lower() for f in re.findall(r'(ping ?pong ball|tennis ball|white ball|soccer ball|basketball)', qq, re.I)}
    return qn, depth_names(g.depth_info.iloc[0])

def aliases(group_obj, fact_obj, clips):
    """the clip's own inputs identify group_obj with fact_obj (same logic as P4's reviewed depth relink): the clip asks
    about group_obj, which has no depth_info entry; fact_obj has a depth_info entry but no question names it; and
    group_obj is the only question object without a depth entry that shares a name token with fact_obj."""
    ev = []
    sim = lambda a, b: name_score(a, b) >= 0.8
    for v in clips:
        qn, dn = clip_names(v)
        if not any(sim(group_obj, x) for x in qn): continue
        if any(sim(group_obj, x) for x in dn): continue                       # group_obj has its own depth entry
        if not any(sim(fact_obj, x) for x in dn): continue                    # fact_obj not in depth_info
        if any(sim(fact_obj, x) for x in qn): continue                        # fact_obj also asked about: distinct object
        no_depth = [o for o in qn if not any(sim(o, d) for d in dn)]
        tok = [o for o in no_depth if name_score(o, fact_obj) > 0]
        if len(tok) == 1 and sim(tok[0], group_obj):
            ev.append(v)
    return ev

def labfact_alias(log):
    """S3 lab size rows of a prop group whose object is identified (aliases) with an object of a stated lab prior."""
    out = {}
    for k, qs in GROUPS.items():
        g = ti.loc[qs]
        objs = sorted({x.lower().strip() for o in g.tobj for x in str(o).split('|')})
        if any(ambiguous(o) for o in objs) or not any(q in S3set for q in qs): continue
        dim = dimnorm(g.tdim.iloc[0])
        for (po, pd_, si, vsrc) in LABFACTS:
            if dimnorm(pd_) != dim or max(name_score(po, o) for o in objs) >= 0.8: continue   # direct name match = LABfix labfact
            clips = sorted(set(g.video_id))
            ev = aliases(objs[0], po, clips)
            if not ev: continue
            vals = sorted({round(s, 6) for (p2, d2, s, v2) in LABFACTS if dimnorm(d2) == dim and name_score(p2, po) >= 0.8})
            if len(vals) != 1: log.append(('alias_fact_conflict', objs, po, vals)); continue
            log.append(('alias', objs[0], '=', po, 'evidence clips', ev, 'fact', vals[0], 'm'))
            out[k] = (vals[0], objs[0], po, ev)
            break
    return out

# ---------------------------------------------------------------- segmented-twin pairs (P4 segtwin)
def segtwin_pairs():
    S = t[t.category == 'S3'].copy()
    S['twin'] = S.video_id.str.replace('_segmented', '', regex=False)
    S['nq'] = S.question.map(normq)
    orig = S[~S.video_id.str.endswith('_segmented') & (S.video_source != 'lab')]
    pairs = {}
    for r in S[S.video_id.str.endswith('_segmented')].itertuples():
        o = orig[(orig.twin == r.twin) & (orig.nq == r.nq)]
        if len(o) and o.prior.iloc[0] == r.prior and o.depth_info.iloc[0] == r.depth_info:
            pairs[r.qid] = int(o.qid.iloc[0])
    return pairs

def is_speed(q):
    s = ti.loc[q, 'question']
    return bool(re.search(r'\b(speed|velocity)\b', s, re.I)) and not re.search('acceleration', s, re.I)

# ---------------------------------------------------------------- merge
def merge(mode, use_alias=True):
    log = []
    stageA = (P4S3 if mode == 'split' else DF).copy()
    final = {q: float(stageA[q]) for q in S3}
    src = {q: ('v3' if not ne(stageA[q], v3[q]) else 'P4') for q in S3}
    info = {q: '' for q in S3}
    # 2. LAB pooling on stage A
    P = lab_pool(stageA, log)
    for q, (pv, label, inf) in P.items():
        if ne(pv, final[q]):
            final[q] = pv; src[q] = 'LABpool_on_P4' if mode == 'split' else 'LABpool_on_direct'
        info[q] = f"group {label}; {inf['n_events']} events"
    # 3a. stated facts: T (TL non-lab changes) and SIB
    T = {q: float(TL[q]) for q in S3 if ne(TL[q], v3[q]) and ti.loc[q, 'video_source'] != 'lab'}
    Sb = {q: float(SIB[q]) for q in S3 if ne(SIB[q], v3[q])}
    for q in set(T) & set(Sb): assert np.isclose(T[q], Sb[q], rtol=1e-9), q
    dropped = {}
    for q, x in T.items():
        if is_speed(q) and (x / v3[q] > 2 or x / v3[q] < 0.5) and q not in Sb:
            dropped[q] = x; continue          # family facts conflict (policy 1 exception), keep footage value
        final[q] = x; src[q] = 'T' if q not in Sb else 'T=SIB'
    for q, x in Sb.items():
        if q not in T: final[q] = x; src[q] = 'SIB'
    stated = set(T) - set(dropped) | set(Sb)
    # 3b. lab stated fact through an alias identified by the clips' own inputs (white ball = ping pong ball)
    if use_alias:
        AF = labfact_alias(log)
        bad_events = {e for (tag, *rest) in log if tag == 'skip_event_different_object' for e in rest[1]}
        for k, (si, gobj, fobj, ev) in AF.items():
            for q in GROUPS[k]:
                if q in S3set and ti.loc[q, 'base'] not in bad_events:
                    final[q] = si / usc(q); src[q] = 'labfact_alias'; stated.add(q)
                    info[q] = f"'{gobj}' = '{fobj}' (clips {','.join(ev)}); lab prior states {fobj} = {si*100:g} cm"
    # 4. segmented twins follow their original's final answer (P4 segtwin pairs)
    for tw, orq in segtwin_pairs().items():
        if tw in stated: continue
        if ne(final[tw], final[orq]):
            final[tw] = final[orq]; src[tw] = 'segtwin_resync'
    return final, src, info, dropped, log, P, T, Sb

def write(final, path):
    df = V3df.copy()
    m = df.id.isin(S3set)
    df.loc[m, 'parsed_value'] = df.loc[m, 'id'].map(final)
    v = df.parsed_value.values.astype(float)
    assert len(df) == 3289 and list(df.id) == list(V3df.id)
    assert np.isfinite(v).all() and (v > 0).all()
    ch = ~np.isclose(v, V3df.parsed_value.values, rtol=1e-9, atol=0)
    assert set(CAT[df.id[ch]]) <= {'S3'}
    df.to_csv(path, index=False)
    return int(ch.sum()), float(np.median(v[ch] / V3df.parsed_value.values[ch]))

if __name__ == '__main__':
    res = {}
    fin, src, info, dropped, log, P, T, Sb = merge('split')
    res['main'] = write(fin, OUT + '/S3_merged.csv')
    finN, srcN, infoN, *_ = merge('nosplit')
    res['nosplit'] = write(finN, OUT + '/S3_merged_nosplit.csv')
    finNA, srcNA, *_ = merge('split', use_alias=False)
    res['noalias'] = write(finNA, OUT + '/S3_merged_noalias.csv')
    print(json.dumps(res))
    for l in log: print('LOG', l)
    print('dropped T (speed conflicts):', dropped)
    # ---- decisions table
    RUN = pd.read_csv(R + '/runs/test_v1_high_854/test.csv').set_index('id')
    SFULL = pd.read_csv(SP + '/hyp/S3/variants_labdirect/S3p3_split_full.csv').set_index('id').parsed_value
    SB = pd.read_pickle(SP + '/big/priors_as_labels/transfer_rebuilt.pkl').set_index('qid')
    TA = SG.A.set_index('qid')
    def p4_reason(q):
        v = ti.loc[q, 'video_id']; srcv = ti.loc[q, 'video_source']
        if srcv == 'segmentation':
            return 'P4 segtwin: segmented clip copies its original clip\'s answer (same question, prior, depth_info); no competing candidate'
        if q in SPLIT:
            if base_of(v).endswith('0034b'):
                return "P4 rule (b): 0034b is a second camera carrying 0034a's depth_info -> static answer = median of 0034a renders (split: 0034a geometry)"
            if ne(P4S3[q], SFULL[q]):
                return 'P4 depthfix: geometry re-solved with the depth entry the question object was named differently in (white ball <-> ping_pong_ball)'
            g = RUN.loc[q, 'geo_value']
            if np.isfinite(g) and g / P4S3[q] > 100:
                return "P4 decimal fix: depth_info '8420m' read as 0.842 m and geometry re-solved"
            return 'P4 kind split: lab static kind (size/distance) -> v2 geometry selection (probe-3 2x2: direct -0.087/answer on static, +0.082 on motion)'
        if srcv == 'lab':
            return "P4 render: s/x render takes the original render's direct answer (original render's direct beats s/x own in 6/6 cells on known rows)"
        return 'P4'
    rows = []
    cand = {q for q in S3 if ne(P4S3[q], v3[q]) or ne(TL[q], v3[q]) or ne(SIB[q], v3[q]) or ne(fin[q], v3[q])}
    for q in sorted(cand):
        comp = []
        for k, s in (('P4', P4S3), ('TL', TL), ('SIB', SIB)):
            if ne(s[q], v3[q]): comp.append(f'{k}={s[q]:.4g}')
        if q in P: comp.append(f'pooled_on_P4={P[q][0]:.4g}')
        if q in SPLIT or ne(finN[q], fin[q]): comp.append(f'nosplit={finN[q]:.4g}')
        s_ = src[q]; qq = ti.loc[q, 'question'].lower()
        tl_lab = ne(TL[q], v3[q]) and ti.loc[q, 'video_source'] == 'lab'
        if s_ == 'P4':
            reason = p4_reason(q)
            if tl_lab:
                reason = 'P4 vs TL-LABpool: ' + reason + '; LAB pool re-based on P4 leaves the P4 value (' + info[q] + \
                         ('' if 'pencil bag' not in qq else ': 0034b is a copy of 0034a, one independent event') + \
                         '); TL pooled probe-3 direct values (0034b direct runs ~35% high on the wrong depth_info)'
        elif s_.startswith('LABpool'):
            if 'table' in qq:
                why = ('table is direct-routed in every candidate (geometry implausible); the same lab table is seen in 0021-0040 frames, '
                       'so its base-render direct answers are pooled across events; s/x rows use the base render\'s direct as own value (P4 render rule)')
            elif 'soccer' in qq:
                why = ('geometry (P4 split) pooled across 9 independent soccer-ball events (0034b copy dropped); 0035 geometry has a duplicated '
                       'soccer-ball depth entry (one is the basketball), pooling removes that error; TL pooled probe-3 direct values')
            else:
                why = ('lab prop measured by geometry (P4 split) in every event; pooled across events (geometry agrees within ~2%); '
                       'TL pooled probe-3 direct values that run 8-12% below geometry for this prop set (poker tower 9.2 vs 10.4, pink bottle 18.8 vs 21.0, '
                       'cup height 13.5 vs 14.8); fixed-rig geometry is calibrated to 1.5% on val static objects and the same white tumbler in 0013 has val GT 14.5 (geometry 14.6, direct 10.6)')
            reason = ('P4 vs TL: ' if tl_lab and ne(P4S3[q], v3[q]) else ('TL-only: ' if tl_lab else 'P4-only: ')) + 'LAB pool re-based on P4 (' + info[q] + '); ' + why
        elif s_ == 'labfact_alias':
            reason = ('policy 1 (stated lab fact): ' + info[q] + '; the 0031 base render asks the same distance question with "ping pong ball" '
                      'where its s/x renders say "white ball"; frames show the same 4 cm white ball (0031, 0037-0040). Beats geometry pool and TL direct pool')
        elif s_ in ('T', 'T=SIB'):
            r_ = TA.loc[q] if q in TA.index else None
            reason = 'policy 1 (stated fact, T' + ('=SIB' if s_ == 'T=SIB' else '') + '): ' + (f"{r_.why} from {str(r_.src)[:80]}: '{str(r_.line).strip()[:60]}'" if r_ is not None else '')
            if ne(P4S3[q], v3[q]): reason += '; overrides P4 segtwin copy of the original (which also gets the stated value)'
        elif s_ == 'SIB':
            reason = 'policy 1 (stated fact, sibling transfer): ' + str(SB.loc[q, 'src'])[:120]
        elif s_ == 'v3':
            reason = ('T stated value dropped (policy 1 exception): the family\'s stated facts conflict through the shared camera - boat speed 4, eagle speed 11.84 and '
                      'person height 1.75 imply f~3000-3100 px, person speed 1.3 (0025) implies ~950 px; footage gives 0.33-0.57 m/s in 0025/0026/0027. '
                      'MRA asymmetry: keeping the footage value scores 0.3 if GT=1.3, the stated value scores 0 if GT~0.4 -> break-even P(GT=1.3)~0.58')
        else:
            reason = s_
        rows.append(dict(qid=q, video_id=ti.loc[q, 'video_id'], question=ti.loc[q, 'question'], v3_value=v3[q], final_value=fin[q],
                         chosen_source=s_, competing_values='; '.join(comp), reason=reason))
    D = pd.DataFrame(rows)
    D.to_csv(OUT + '/decisions.csv', index=False)
    D.to_pickle(OUT + '/decisions_raw.pkl')
    print(D.chosen_source.value_counts().to_dict())
    # counts per source among rows that differ from v3
    chg = D[[ne(a, b) for a, b in zip(D.final_value, D.v3_value)]]
    print('changed vs v3 by source:', chg.chosen_source.value_counts().to_dict(), 'total', len(chg))
    chP4 = [q for q in S3 if ne(fin[q], P4S3[q])]
    print('differs from P4 S3:', len(chP4), pd.Series([src[q] for q in chP4]).value_counts().to_dict())
    chN = [q for q in S3 if ne(fin[q], finN[q])]
    print('main vs nosplit differ:', len(chN))
