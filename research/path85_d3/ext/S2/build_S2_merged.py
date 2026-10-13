"""Probe-5 S2 merge on v3 (reproducible from the input CSVs).

Inputs (all built on v3 or v2; only their S2 rows are used):
  P4  = hyp/final/S2_maxext_segtwin.csv            (probe 4's S2: twin copy; its non-S2 rows are v2 and ignored)
  T   = big/scene_graph/S2_T.csv                   (scene-graph T: value stated by a family clip's prior)
  SIB = big/priors_as_labels/S2_sibling_prior_transfer.csv  (sibling-prior transfer, same idea as T)

Policy
  (1) a stated family value (T / SIB) wins, unless the family's stated facts conflict with each other;
      T and SIB must agree where both fire (asserted).
  (2) conflicting / contested rows: per-row decision by mechanism (table CONTESTED below, with reasons).
  (3) everything else is stacked.  The twin copy (P4) is re-applied AFTER the transfers, so a segmented
      clip copies its original's FINAL value; a segmented row with its own stated value keeps it.

Outputs (in this directory): S2_merged.csv (id,parsed_value; all 3289 template ids; only S2 rows differ
from v3), decisions.csv, build_summary.json.  Validation answers are only used to MEASURE at the end.
"""
import sys, re, json, importlib.util
import numpy as np, pandas as pd

R = '/home/user/quantiphy-challenge'
SP = '/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
OUT = SP + '/merge/S2'
sys.path.insert(0, R)
from qp.data import load_split
from qp.mra import item_scores

V3 = R + '/submissions/trackA_v3_best_per_category.csv'
P4SUB = R + '/submissions/trackA_probe4_s2twin_d2refineoff_s3split_d3fixes.csv'
CANDS = {'P4': SP + '/hyp/final/S2_maxext_segtwin.csv',
         'T': SP + '/big/scene_graph/S2_T.csv',
         'SIB': SP + '/big/priors_as_labels/S2_sibling_prior_transfer.csv'}
T_LIST = SP + '/big/scene_graph/T_list.txt'
SIB_CHANGED = SP + '/big/priors_as_labels/changed.pkl'
SEGTWIN = SP + '/hyp/S2/t2/segtwin.py'

# twin key of the probe-4 rule (normalised question text + prior value), imported, not re-typed
spec = importlib.util.spec_from_file_location('segtwin_rule', SEGTWIN)
seg = importlib.util.module_from_spec(spec); spec.loader.exec_module(seg)

t = load_split('test').set_index('qid')
v3 = pd.read_csv(V3)
ids = v3.id.values
cat = t.loc[ids, 'category'].values
S2 = cat == 'S2'
base = pd.Series(v3.parsed_value.values, index=ids)


def changed(path):
    d = pd.read_csv(path)
    assert (d.id.values == ids).all(), path
    x = d.parsed_value.values.astype(float)
    m = ~np.isclose(x, base.values, rtol=1e-12, atol=0)
    other = sorted(set(cat[m & ~S2]))
    return pd.Series(x[m & S2], index=ids[m & S2]), other


ch, other_cats = {}, {}
for k, f in CANDS.items():
    ch[k], other_cats[k] = changed(f)
assert other_cats['T'] == [] and other_cats['SIB'] == [], other_cats
# P4 S2 file was built on v2, so its S3 rows differ from v3; only its S2 rows are probe 4's S2 change
p4sub, _ = changed(P4SUB)
assert p4sub.index.equals(ch['P4'].index) and np.allclose(p4sub.values, ch['P4'].values)

# provenance text of the stated values
t_src = {}
for line in open(T_LIST):
    mm = re.match(r'^(\d+) (\S+) \| .*? \| v3=\S+ -> \S+ (\S+) \| src (.*?) \| (.*)$', line.strip())
    if mm:
        t_src[int(mm.group(1))] = f"{mm.group(5)} [{mm.group(3)}; src {mm.group(4)}]"
sib_src = pd.read_pickle(SIB_CHANGED).set_index('qid').src.to_dict()

# ---- (1) stated family values -------------------------------------------------------------------
fact, fact_src = {}, {}
for q in sorted(set(ch['T'].index) | set(ch['SIB'].index)):
    vals = {k: ch[k][q] for k in ('T', 'SIB') if q in ch[k].index}
    vv = list(vals.values())
    assert all(np.isclose(v, vv[0], rtol=1e-9) for v in vv), (q, vals)   # T and SIB never disagree on S2
    fact[q] = vv[0]
    fact_src[q] = '+'.join(vals)

# ---- (2) contested rows: per-row decisions (policy 1 exception / policy 2) ----------------------
# Person speed 1.3 m/s is stated in 0025/0031/0037/0038 (footage B and others) and conflicts with the
# family's other stated facts in footage B (boat 4, eagle 11.84, person height 1.75 all imply f~3000-3100 px,
# person speed 1.3 implies ~950 px; verifier priors_as_labels).  The policy-1 exception therefore applies to
# person-speed transfers of this family, and each row is decided on its own evidence:
#   qid 14   (0041 speed of the person at 1.0s): SIB 1.3 vs v3 1.426.  v3 is inflated by the foreshortened
#            person-height prior of the overhead view (its boat length 13.03 vs stated 10, boat speed 5.28 vs
#            stated 4: x1.30); boat-scaled render speed ~1.08, 0039 3D direct 1.19.  1.3 is closer than v3 to every
#            candidate truth <= 1.36 -> take 1.3 (+0.1 item under every convention).
#   qid 1748 (0041_seg average speed of the person): SIB 1.3 vs v3 1.263.  v3 is already within 2.9% of the
#            stated value (scores 1.0 if the truth is 1.3) and is closer to every render-based truth below 1.28
#            (boat-scaled render ~1.00, 0039_seg 3D direct 1.10) -> keep v3 (weakly dominant).
CONTESTED = {
    1748: ('v3', 'policy-1 exception (person speed 1.3 conflicts with the family\'s other stated facts in footage B): '
                 'v3 1.263 is within 2.9% of 1.3 (same score if truth=1.3) and closer to the footage-C render '
                 'evidence (boat-scaled 0041_seg ~1.00, 0039_seg D3 1.10) -> keep v3, weakly dominant'),
    14:   ('SIB', 'policy-1 exception checked (person speed 1.3 contested in footage B): v3 1.426 carries the 0041 '
                  'overhead foreshortening (x1.30 from boat 13.03/10, 5.28/4); boat-scaled render ~1.08, 0039 D3 1.19; '
                  '1.3 beats v3 under both the stated and the render convention -> take 1.3'),
}

NOTES = {1746: 'cross-check: boat width 2.59 agrees with the depth-identical 3D views (0039 2.70, 0042 2.65) and the '
               'D3 family pool 2.667; v3 3.83 is 44% above (no stated width, so no conflict)'}

# ---- (3) twin copy re-applied on top of the transfers -------------------------------------------
orig_key = {}
tt = seg.t  # test split with twin/nq/pv columns, built by the probe-4 rule
o = tt[~tt.video_id.str.endswith('_segmented')]
key = {(r.twin, r.nq, r.pv): r.qid for r in o.itertuples()}
for r in tt[(tt.category == 'S2') & tt.video_id.str.endswith('_segmented')].itertuples():
    q = key.get((r.twin, r.nq, r.pv))
    if q is not None and t.category[q] == 'S2':
        orig_key[r.qid] = q
for q, v in ch['P4'].items():           # every probe-4 S2 change is a pure twin copy of the original's v3 value
    assert q in orig_key and np.isclose(v, base[orig_key[q]], rtol=1e-12), q

final = base.copy()
src, reason, comp = {}, {}, {}


def fmt(x):
    return f'{x:.6g}'


for q, v in fact.items():
    choice = CONTESTED.get(q, (None, None))[0]
    if choice == 'v3':
        src[q] = 'v3'; reason[q] = CONTESTED[q][1]
        continue
    final[q] = v
    src[q] = fact_src[q]
    s = t_src.get(q) or sib_src.get(q)
    reason[q] = CONTESTED[q][1] if q in CONTESTED else f'policy 1 (stated family value): {s}'

for q in ch['P4'].index:
    oq = orig_key[q]
    twin_val = final[oq]
    if q in fact and src.get(q) != 'v3':
        reason[q] = (f'policy 1: stated family value wins over the twin copy (P4 copied original qid {oq} v3 '
                     f'{fmt(base[oq])}; original qid {oq} itself now takes the same stated value {fmt(final[oq])})')
        src[q] = fact_src[q] + '>P4'
        continue
    final[q] = twin_val
    src[q] = 'P4' if np.isclose(twin_val, ch['P4'][q]) else 'P4(twin of final)'
    reason[q] = f'policy 3 (stack): segmented twin takes original qid {oq} ({t.video_id[oq]}) answer {fmt(twin_val)}'
    if q in NOTES:
        reason[q] += '; ' + NOTES[q]

# competing values for the table
rows = []
for q in sorted(set(src)):
    c = {k: ch[k][q] for k in ('P4', 'T', 'SIB') if q in ch[k].index}
    comp = '; '.join(f'{k}={fmt(v)}' for k, v in c.items())
    rows.append(dict(qid=q, video_id=t.video_id[q], question=t.question[q], prior=t.prior[q],
                     v3_value=base[q], final_value=final[q], chosen_source=src[q], competing_values=comp,
                     reason=reason[q]))
dec = pd.DataFrame(rows)

# ---- outputs + checks ---------------------------------------------------------------------------
out = pd.DataFrame({'id': ids, 'parsed_value': final.values})
assert len(out) == 3289 and np.isfinite(out.parsed_value).all() and (out.parsed_value > 0).all()
diff = ~np.isclose(out.parsed_value.values, base.values, rtol=1e-12, atol=0)
assert set(cat[diff]) <= {'S2'}
out.to_csv(OUT + '/S2_merged.csv', index=False)
dec.to_csv(OUT + '/decisions.csv', index=False)

# probe-4 S2 for comparison
p4 = base.copy(); p4[ch['P4'].index] = ch['P4'].values
vs_p4 = ~np.isclose(final.values, p4.values, rtol=1e-12, atol=0)

summary = {
    'changed_vs_v3': int(diff.sum()),
    'changed_vs_probe4_S2': int(vs_p4.sum()),
    'rows_considered': int(len(dec)),
    'per_source': dec.chosen_source.value_counts().to_dict(),
    'candidate_changes': {k: int(len(v)) for k, v in ch.items()},
    'median_ratio_changed_vs_v3': float(np.median(final.values[diff] / base.values[diff])),
    'ids_vs_probe4': [int(i) for i in ids[vs_p4]],
}


# measurement only: validation answers matched to test S2 rows (and their segmented twins) by question text
def val_known():
    v = load_split('val')
    v['twin'] = v.video_id.str.replace('_segmented', '', regex=False)
    v['nq'] = v.question.map(seg.normq)
    gt = v.set_index(['twin', 'nq']).answer
    gt = gt[~gt.index.duplicated()]
    e = tt[tt.category == 'S2'].copy()
    e['ans'] = [gt.get((a, b), np.nan) for a, b in zip(e.twin, e.nq)]
    return e[e.ans.notna()].set_index('qid').ans


kn = val_known()
kn_ch = kn[kn.index.isin(dec.qid)]
meas = {}
for name, s in [('v3', base), ('probe4', p4), ('merged', final)]:
    sc = item_scores(s[kn.index].values, kn.values)
    meas[name] = {'known_S2_rows': int(len(kn)), 'mra_known': round(float(np.nanmean(sc)), 4),
                  'mra_known_changed_rows': round(float(np.nanmean(item_scores(s[kn_ch.index].values, kn_ch.values))), 4)
                  if len(kn_ch) else None, 'n_known_changed': int(len(kn_ch))}
summary['val_on_test_measure_only'] = meas
json.dump(summary, open(OUT + '/build_summary.json', 'w'), indent=1)
print(json.dumps(summary, indent=1))
