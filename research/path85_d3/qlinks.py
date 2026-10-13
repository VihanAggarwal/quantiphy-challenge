"""Candidate new scene links: simulation base clips in DIFFERENT Track A families that ask >= 2 identical (normalized)
questions with specific object phrases. Test inputs only."""
from lofo import *
import itertools, collections
t = ti.reset_index()
s = t[t.video_id.str.startswith('simulation')].copy()
s['nq'] = s.question.map(pp.norm_question)
# idf of questions across bases
qb = s.groupby('nq').base.nunique()
bq = s.groupby('base').nq.agg(set)
fam = s.groupby('base').fam.first()
cat = s.groupby('base').category.agg(lambda x: ''.join(sorted(set(x))))
pairs = []
for a, b in itertools.combinations(sorted(bq.index), 2):
    if fam[a] == fam[b]: continue
    sh = bq[a] & bq[b]
    sh = {q for q in sh if qb[q] <= 6}
    if len(sh) >= 2:
        pairs.append((a, b, cat[a], cat[b], len(sh), sorted(sh)[:4]))
print(len(pairs))
for p in pairs: print(p)
