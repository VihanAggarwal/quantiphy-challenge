"""Verifier correction of S3_merged.csv (no API, repo read-only, test inputs only).
Fix: the sibling-prior (SIB) rule's question regex takes 'boat from the beginning to the end' as the object name, so the
5 ORIGINAL clips whose questions carry that phrase (0034/0035/0036) never received the stated value that their
segmented twins (identical prior, depth_info and footage) received. Re-run the same SIB rule with the trailing time span
stripped from the question, keep the verified noconflict guard (transferred speed >2x off the clip's own answer -> drop),
and apply the new S3 rows on top of S3_merged.csv. Result: twins and originals answer the same stated value."""
import sys, re, os
sys.dont_write_bytecode = True
os.chdir('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/merge/S3/verified')
sys.path.insert(0, '/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/big/priors_as_labels')
from valcheck import *            # rule(), SP (test.pkl location); reads test inputs only
import pandas as pd, numpy as np
R = '/home/user/quantiphy-challenge'
OUTD = '/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/merge/S3/verified/'
MERGED = '/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/merge/S3/S3_merged.csv'
t_all = pd.read_pickle(SP + 'test.pkl')
cat = t_all.set_index('qid').category
V3 = pd.read_csv(R + '/submissions/trackA_v3_best_per_category.csv'); v3 = V3.set_index('id').parsed_value
Mdf = pd.read_csv(MERGED); M = Mdf.set_index('id').parsed_value
qs = t_all.copy()
STRIP = r'\s+from\s+(?:the\s+)?beginning\s+to\s+(?:the\s+)?end\b|\s+from\s+[\d.]+\s*s\s+to\s+[\d.]+\s*s\b'
qs['question'] = qs.question.str.replace(STRIP, '', regex=True, flags=re.I)
R0 = rule(t_all, t_all); R1 = rule(qs, t_all)
new = R1[~R1.qid.isin(R0.qid) & (R1.qid.map(cat) == 'S3')].copy()
new['v3'] = new.qid.map(v3); new['ratio'] = new.value / new.v3
orig_q = t_all.set_index('qid').question
new['is_speed'] = new.qid.map(orig_q).str.contains(r'\b(speed|velocity)\b', case=False) & ~new.qid.map(orig_q).str.contains('acceleration', case=False)
drop = new[new.is_speed & ((new.ratio > 2) | (new.ratio < 0.5))]
keep = new.drop(drop.index)
print('new SIB rows (time span stripped):', new[['qid', 'video_id', 'value', 'v3', 'ratio']].to_dict('records'))
print('dropped by noconflict guard:', drop.qid.tolist())
out = Mdf.copy()
m = out.id.isin(keep.qid)
out.loc[m, 'parsed_value'] = out.loc[m, 'id'].map(keep.set_index('qid').value)
v = out.parsed_value.values.astype(float)
assert len(out) == 3289 and list(out.id) == list(V3.id) and list(out.columns) == list(V3.columns)
assert np.isfinite(v).all() and (v > 0).all()
ch = ~np.isclose(v, V3.parsed_value.values, rtol=1e-9, atol=0)
assert set(cat.loc[out.id[ch]]) <= {'S3'}
dM = ~np.isclose(v, Mdf.parsed_value.values, rtol=1e-9, atol=0)
out.to_csv(OUTD + 'S3_merged_verified.csv', index=False)
print('changed vs v3:', int(ch.sum()), 'median ratio', float(np.median(v[ch] / V3.parsed_value.values[ch])))
print('differs from S3_merged:', int(dM.sum()), out.loc[dM, ['id', 'parsed_value']].assign(merged=Mdf.parsed_value[dM]).to_dict('records'))
