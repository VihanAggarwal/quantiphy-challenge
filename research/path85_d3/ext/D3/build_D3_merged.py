"""Build the merged D3 variant for probe 5 (on top of v3) and its lab-motion alternate.

Inputs (read-only):
  v3            submissions/trackA_v3_best_per_category.csv
  P4            hyp/final/D3_main_transfer_fixed.csv (probe-4 D3 variant) + hyp/D3/review_code/steplog.pkl (its step labels)
  TKP/TP/T      big/scene_graph/D3_{TKP,TP,T}_LABfix.csv (values re-derived here with the verifier's fix_build.py, which also
                gives per-row rule labels; asserted equal to the CSVs)
  sib           big/priors_as_labels/D3_sibling_prior_transfer_ext.csv (+ transfer_rebuilt.pkl for the source lines)
  cam           big/sim3d_camera/D3_camera_consistency.csv
  lm            big/labmotion/D3_labmotion_direct.csv (alternate only)
  cached run    runs/test_v1_high_854/test.csv (flags, direct values), hyp/D3/work/lab_test_anns.pkl (lab specs+tracks)

Priority per D3 row (first that applies):
  1 FACT      a value stated by a family clip's prior (scene-graph T or sibling transfer; they agree wherever both fire)
  2 LABFACT   lab prop with a stated lab prior size (basketball 23.2 cm)
  3 LABPOOL   lab prop pooling (verifier's fixed rule), re-run on the P4-corrected lab base
  4 DEPTHFIX  geometry rows whose target depth was borrowed from target2 (re-solved with the right entry, else direct)
  5 P4LAB     P4 lab steps (relink / no-time speed / per-video static scale / s-x renders take base render's motion answer)
  6 SIM_P/K   scene-graph series pooling (P) and per-clip scale (K) on direct-routed sim answers; K dropped on a speed when
              the family states that object's speed and K moves away from it (or below its own depth_info radial speed)
  7 SEGTWIN   a pixel-aligned *_segmented twin takes its original clip's final value (P4 pairs; 0017 pair left out as in P4)
  8 v3
"""
import sys, os, re, json, pickle, math
import numpy as np, pandas as pd

SP = '/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
MD = SP + '/merge/D3'
R = '/home/user/quantiphy-challenge'
sys.path.insert(0, MD)

# ---------------------------------------------------------------- inputs
V3 = pd.read_csv(R + '/submissions/trackA_v3_best_per_category.csv')
V3['cat'] = [i[0] + v[1] for i, v in zip(V3.inference_type, V3.video_type)]
v3 = dict(zip(V3.id, V3.parsed_value))
V = V3.set_index('id')
D3 = [q for q in V3.id if V.loc[q, 'cat'] == 'D3']
def csv(p):
    d = pd.read_csv(p); return dict(zip(d.id, d.parsed_value))
P4 = csv(SP + '/hyp/final/D3_main_transfer_fixed.csv')
TKPc = csv(SP + '/big/scene_graph/D3_TKP_LABfix.csv')
SIB = csv(SP + '/big/priors_as_labels/D3_sibling_prior_transfer_ext.csv')
CAM = csv(SP + '/big/sim3d_camera/D3_camera_consistency.csv')
LM = csv(SP + '/big/labmotion/D3_labmotion_direct.csv')
run = pd.read_csv(R + '/runs/test_v1_high_854/test.csv').set_index('id')
def changed(d, q): return not np.isclose(d[q], v3[q], rtol=1e-9)

# scene-graph rules (verifier's fixed build), with labels
sys.path.insert(0, SP + '/big/scene_graph')
_cwd = os.getcwd()
import fix_build as FB
os.chdir(_cwd)
ti = FB.ti
TKP_new, TKP_why = FB.variant_fixed(('D3',), rule_K=True, rule_P=True, rule_LAB=True)
for q in D3:
    assert np.isclose(TKP_new[q], TKPc[q], rtol=1e-9), ('TKP repro', q)
Atab = FB.A  # accepted (non-conflicting) T transfers
T_val = {r.qid: r.value for r in Atab.itertuples() if r.cat == 'D3'}
T_src = {r.qid: f'{r.line.strip()} @{r.src} ({r.why})' for r in Atab.itertuples() if r.cat == 'D3'}
sibt = pd.read_pickle(SP + '/big/priors_as_labels/transfer_rebuilt.pkl'); sibt = sibt[sibt.category == 'D3']
SIB_val = dict(zip(sibt.qid, sibt.value)); SIB_src = dict(zip(sibt.qid, sibt.src))
for q in D3:
    if changed(SIB, q): assert q in SIB_val and np.isclose(SIB[q], SIB_val[q])
st = pickle.load(open(SP + '/hyp/D3/review_code/steplog.pkl', 'rb'))
L = st['L']
P4_step = L[L.changed].groupby('qid').step.agg(lambda s: '+'.join(s)).to_dict()

# ---------------------------------------------------------------- 1 FACT
FACT, FACT_src = {}, {}
for q in D3:
    vals = {}
    if q in T_val: vals['T'] = T_val[q]
    if q in SIB_val: vals['sib'] = SIB_val[q]
    if P4_step.get(q) == 'sibling_transfer' and changed(P4, q): vals['P4sib'] = P4[q]
    if not vals: continue
    u = np.unique(np.round(list(vals.values()), 9))
    assert len(u) == 1, ('stated facts disagree', q, vals)
    FACT[q] = float(u[0])
    FACT_src[q] = '+'.join(vals) + ': ' + (T_src.get(q) or ('%s @%s' % ('sibling prior', SIB_src.get(q))))

# ---------------------------------------------------------------- 4 DEPTHFIX (computed before pooling; distance rows, not pooled)
import depthfix
DF = depthfix.run_fix()
# guard: a re-solve is accepted only when the target time lies inside the timed depth_info span of the renamed entry
lab_anns = pickle.load(open(SP + '/hyp/D3/work/lab_test_anns.pkl', 'rb'))
from qp.geometry import _depth_groups
DEPTHFIX, DEPTHFIX_why = {}, {}
for r in DF.itertuples():
    a = lab_anns['anns'][r.qid]
    tt = a.spec.target.time
    if r.how.startswith('resolved'):
        g = [p for nm, p in _depth_groups(a.spec.depth) if nm == r.unclaimed[0] or nm.replace('_', ' ') == r.unclaimed[0]]
        ts = sorted({t for t, _ in (g[0] if g else []) if t is not None})
        inside = (tt is None) or (len(ts) >= 1 and ts[0] - 1e-6 <= float(tt) <= ts[-1] + 1e-6)
        if inside:
            DEPTHFIX[r.qid] = float(r.value)
            DEPTHFIX_why[r.qid] = f"re-solved with depth entry '{r.unclaimed[0]}' as {r.tobj[0]} (geo {r.run_geo:.4g} -> {r.value:.4g})"
        else:
            DEPTHFIX[r.qid] = float(r.direct)
            DEPTHFIX_why[r.qid] = (f"direct: re-solve extrapolates the '{r.unclaimed[0]}' depth to t={tt} outside its entries "
                                   f"{ts} (gives {r.new_geo:.4g}); borrowed-depth geo was {r.run_geo:.4g}")
    else:
        DEPTHFIX[r.qid] = float(r.direct)
        DEPTHFIX_why[r.qid] = f"direct: target has no depth entry of its own (borrowed-depth geo was {r.run_geo:.4g})"

# ---------------------------------------------------------------- 5 P4LAB and base for lab pooling
P4LAB = {q: P4[q] for q in D3 if V.loc[q, 'video_source'] == 'lab' and changed(P4, q)}
labbase = dict(v3)
labbase.update(P4LAB)
labbase.update(DEPTHFIX)

# ---------------------------------------------------------------- 2/3 LABFACT / LABPOOL re-run on the corrected lab base
import labpool2
def lab_pool_on(base):
    FB.v3 = base; labpool2.v3 = base
    try:
        LP, lw = FB.lab_pool_fixed(FB.t, cats=('S3', 'D3', 'D2'))
    finally:
        FB.v3 = v3; labpool2.v3 = v3
    return LP, lw
LP, LPwhy = lab_pool_on(labbase)
LABFACT = {q: v for q, v in LP.items() if LPwhy[q] == 'labfact' and q in V.index and V.loc[q, 'cat'] == 'D3'}
LABPOOL = {q: v for q, v in LP.items() if LPwhy[q] == 'labpool' and q in V.index and V.loc[q, 'cat'] == 'D3'}

# ---------------------------------------------------------------- 6 SIM P / K with the K guard
import kguard
KG = kguard.compute(ti, FB.KC, TKP_why, TKP_new, v3)
KG['drop_radial2'] = (KG.K < KG.radial * 0.999) & (KG.v3 >= KG.radial * 0.999)   # K introduces a contradiction
K_DROP = set(KG[KG.drop_fact | KG.drop_radial2].qid)
SIMP, SIMK, SIMK_dropped = {}, {}, {}
for q in D3:
    w = TKP_why.get(q)
    if w not in ('pool', 'K') or not changed(TKP_new, q): continue
    if w == 'pool': SIMP[q] = TKP_new[q]
    elif q in K_DROP: SIMK_dropped[q] = TKP_new[q]
    else: SIMK[q] = TKP_new[q]

# ---------------------------------------------------------------- 7 SEGTWIN pairs (P4's key; the pair P4-fixed reverted is left out)
from qp.data import load_split
t = load_split('test'); t = t[t.category == 'D3'].copy()
t['base'] = t.video_id.str.replace(r'_segmented$', '', regex=True)
t['nq'] = t.question.map(lambda s: re.sub(r'\s+', ' ', str(s).strip().lower()).rstrip('?. '))
P4main = csv(SP + '/hyp/D3/D3_main_transfer.csv')
reverted_twins = {q for q in D3 if P4_step.get(q) == 'segtwin' and not np.isclose(P4main[q], P4[q]) and np.isclose(P4[q], v3[q])}
TWIN = {}
for _, g in t.groupby(['base', 'nq', 'prior', 'depth_info', 'target_unit']):
    o = g[~g.video_id.str.endswith('_segmented')]; s = g[g.video_id.str.endswith('_segmented')]
    if len(o) == 1 and len(s) >= 1:
        for q in s.qid:
            if q in reverted_twins: continue
            TWIN[int(q)] = int(o.qid.iloc[0])
excluded_bases = sorted({V.loc[q, 'video_id'] for q in reverted_twins})

# ---------------------------------------------------------------- assemble
final, src, reason = {}, {}, {}
def put(q, v, s, why):
    final[q] = float(v); src[q] = s; reason[q] = why
for q in D3:
    if q in FACT: put(q, FACT[q], 'FACT', FACT_src[q])
    elif q in LABFACT: put(q, LABFACT[q], 'LABFACT', 'stated lab basketball diameter (23.2 cm, a lab prior)')
    elif q in LABPOOL: put(q, LABPOOL[q], 'LABPOOL', 'lab prop pooling (fixed rule) over events, on the P4-corrected lab base')
    elif q in DEPTHFIX: put(q, DEPTHFIX[q], 'DEPTHFIX', DEPTHFIX_why[q])
    elif q in P4LAB: put(q, P4LAB[q], 'P4LAB:' + P4_step.get(q, '?'), 'P4 lab step')
    elif q in SIMP: put(q, SIMP[q], 'SIM_P', 'series pooling of K-corrected direct answers (>=3 bases)')
    elif q in SIMK: put(q, SIMK[q], 'SIM_K', 'per-clip scale K=%.3f from the family stated facts' % math.exp(FB.KC[V.loc[q, 'video_id']]))
    else: put(q, v3[q], 'v3', '')
# twins follow their original (unless the twin carries a stated fact the original lacks)
for tq, oq in TWIN.items():
    if src[tq] == 'FACT' and src[oq] != 'FACT':
        reason[tq] += ' | twin keeps its stated fact (original has none)'; continue
    if np.isclose(final[tq], final[oq], rtol=1e-12):
        if src[tq] == 'v3' and src[oq] == 'v3': continue
        if src[tq] == src[oq]: continue
    prev = (src[tq], final[tq])
    put(tq, final[oq], 'SEGTWIN<' + src[oq], f'segmented twin takes original qid {oq} final value ({src[oq]}); own rule would give {prev[0]} {prev[1]:.4g}')

# ---------------------------------------------------------------- write main CSV
def write(vals, path):
    out = V3[['id']].copy()
    out['parsed_value'] = [vals.get(q, v3[q]) if V.loc[q, 'cat'] == 'D3' else v3[q] for q in V3.id]
    assert len(out) == 3289 and out.id.is_unique
    tmpl = pd.read_csv(R + '/data/submission_template/quantiphy_submission_template.csv')
    assert list(out.id) == list(tmpl.id)
    pv = out.parsed_value.astype(float)
    assert np.isfinite(pv).all() and (pv > 0).all()
    ch = ~np.isclose(pv.values, V3.parsed_value.values, rtol=1e-12)
    assert set(V3.cat[ch]) <= {'D3'}
    out.to_csv(path, index=False)
    r = pv[ch].values / V3.parsed_value[ch].values
    return int(ch.sum()), float(np.median(r)) if ch.any() else 1.0
n_main, med_main = write(final, MD + '/D3_merged.csv')

# ---------------------------------------------------------------- alternate: lab motion to direct (s/x renders take the base render's direct)
MOT = ('speed', 'acceleration', 'displacement', 'path_length')
alt = dict(final); alt_src = dict(src); alt_reason = dict(reason)
lab_mot = [q for q in D3 if V.loc[q, 'video_source'] == 'lab' and ti.loc[q, 'tkind'] in MOT]
for q in lab_mot:
    if src[q] == 'FACT': continue
    d = run.loc[q, 'direct_value']
    assert np.isclose(LM[q], d) if np.isfinite(d) else True
    if np.isfinite(d) and d > 0:
        alt[q] = float(d); alt_src[q] = 'LABMOTION_DIRECT'; alt_reason[q] = 'lab motion to Claude direct (labmotion lever, probe-3 2x2)'
tl = load_split('test'); tl = tl[(tl.category == 'D3') & (tl.video_source == 'lab')].copy()
tl['base'] = tl.video_id.str.replace(r'^(captured_\d+[ab]?)[sxX]$', r'\1', regex=True)
tl['nq'] = tl.question.map(lambda s: re.sub(r'\s+', ' ', str(s).strip().lower()).rstrip('?. '))
n_rdm_alt = 0
for _, g in tl.groupby(['base', 'nq', 'prior', 'depth_info', 'target_unit']):
    b = g[g.video_id == g.base]
    if len(b) != 1: continue
    bq = int(b.qid.iloc[0])
    if bq not in lab_mot or alt_src.get(bq) == 'FACT': continue
    for q in g.qid[g.video_id != g.base]:
        q = int(q)
        if q not in lab_mot or alt_src.get(q) == 'FACT': continue
        if not np.isclose(alt[q], alt[bq]):
            alt[q] = alt[bq]; alt_src[q] = 'LABMOTION_DIRECT_BASE'; n_rdm_alt += 1
            alt_reason[q] = f's/x render takes the base render qid {bq} direct answer (P4 rdm rule under all-direct lab motion)'
n_alt, med_alt = write(alt, MD + '/D3_merged_labmotion.csv')

# ---------------------------------------------------------------- decisions table
cand = dict(P4=P4, TKP=TKPc, TP=csv(SP + '/big/scene_graph/D3_TP_LABfix.csv'), T=csv(SP + '/big/scene_graph/D3_T_LABfix.csv'),
            sib=SIB, cam=CAM, lm=LM)
rows = []
for q in D3:
    comp = {k: d[q] for k, d in cand.items() if changed(d, q)}
    if q in DEPTHFIX: comp['depthfix'] = DEPTHFIX[q]
    if q in LABPOOL and changed(LABPOOL, q): comp["labpool_rerun"] = LABPOOL[q]
    if not comp and src[q] == 'v3' and alt_src[q] == src[q]: continue
    if not comp and not changed(final, q) and not changed(alt, q): continue
    rows.append(dict(qid=q, video_id=V.loc[q, 'video_id'], kind=ti.loc[q, 'tkind'], question=V.loc[q, 'question'].strip(),
                     v3=v3[q], final=final[q], source=src[q], alt_labmotion=alt[q], alt_source=alt_src[q],
                     competing='; '.join(f'{k}={v:.5g}' for k, v in comp.items()),
                     tkp_rule=TKP_why.get(q, '') if changed(TKPc, q) else '', p4_step=P4_step.get(q, '') if changed(P4, q) else '',
                     reason=reason[q]))
DEC = pd.DataFrame(rows)

# rule-pair conflict notes (filled per row; see report for group rationale)
def note(r):
    c = r.competing
    n = []
    if 'cam=' in c and r.source in ('FACT', 'SIM_P', 'SEGTWIN<SIM_P', 'SEGTWIN<FACT'):
        n.append('cam vs fact/pool: stated sibling facts kept (verifier rule); wingspans take the 10-base series pool over the single-clip camera rescale')
    if r.qid in K_DROP:
        n.append('K dropped: family states this object speed and K moves away from it' + (' (and below its depth_info radial speed)' if r.qid in set(KG[KG.drop_radial2].qid) else ''))
    if r.source == 'FACT' and r.tkp_rule == 'K':
        n.append('K vs stated fact: stated fact wins')
    if r.source == 'LABFACT' and r.p4_step == 'lab_relink':
        n.append('relink vs labfact: stated lab basketball 23.2 wins (relink geometry 22.8-25 agrees)')
    if r.source == 'LABPOOL' and r.p4_step == 'lab_kcal_static':
        n.append('kstatic vs labpool: pooled over events on the kstatic-corrected base')
    if r.source.startswith('SEGTWIN') and r.p4_step == 'segtwin' and r.tkp_rule:
        n.append('segtwin vs scene-graph twin value: twin takes the original final value')
    if r.source == 'FACT' and r.p4_step == 'segtwin':
        n.append('segtwin copy of v3 vs stated fact: fact wins (original gets the same fact)')
    if r.source == 'FACT' and 'T=' not in c and 'sib=' in c:
        n.append('sibling transfer only (scene-graph T needs proven motion identity for speeds); the family statements agree with each other and '
                 'the move is < 2x, so the stated value is used')
    if r.qid in dropped_by_p4_fixed:
        n.append('P4-fixed dropped this transfer (strict own-depth-entry check); T and sib both link it to the identical-footage clip '
                 'simulation_0021 (same camera and street, hydrant depth 12.565 m in both; frames checked), so the stated 1.87 m is kept')
    if r.source == 'LABPOOL' and 'labpool_rerun' in c and r.p4_step == '':
        n.append('pool value differs from TKP because the pool was re-run on the P4-corrected lab base (0020 yellow toy kstatic)')
    return ' | '.join(n)
dropped_by_p4_fixed = {q for q in D3 if P4_step.get(q) == 'sibling_transfer' and not np.isclose(P4main[q], P4[q])}
DEC['conflict_note'] = DEC.apply(note, axis=1)
DEC = DEC.rename(columns={'v3': 'v3_value', 'final': 'final_value', 'source': 'chosen_source', 'competing': 'competing_values'})
DEC.to_csv(MD + '/decisions.csv', index=False)

summary = dict(
    main=dict(csv=MD + '/D3_merged.csv', changed_vs_v3=n_main, median_ratio=med_main,
              by_source=DEC[~np.isclose(DEC.final_value, DEC.v3_value, rtol=1e-12)].chosen_source.value_counts().to_dict()),
    alternate=dict(csv=MD + '/D3_merged_labmotion.csv', changed_vs_v3=n_alt, median_ratio=med_alt, s_x_take_base=n_rdm_alt,
                   by_source=DEC[~np.isclose(DEC.alt_labmotion, DEC.v3_value, rtol=1e-12)].alt_source.value_counts().to_dict()),
    k_dropped=sorted(int(x) for x in K_DROP - set(FACT)), twins=len(TWIN), twin_pairs_excluded=excluded_bases,
)
json.dump(summary, open(MD + '/build_summary.json', 'w'), indent=1, default=str)
print(json.dumps(summary, indent=1, default=str))
