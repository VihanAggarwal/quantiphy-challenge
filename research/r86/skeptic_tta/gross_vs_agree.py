"""Which cvq gross misses (vs Track A combo2 pseudo-labels) sit on tracks that drift from Qwen's own boxes (agree<0.8,
the population re-seeding could fix) vs tracks that follow Qwen's instance (re-seeding from Qwen's other frames
reproduces them). Test rows of non-validation videos, S2 sim and D2 sim static."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path('/home/user/quantiphy-challenge'); sys.path.insert(0, str(ROOT))
from qp.data import load_split
from qp.mra import item_scores
TB = Path('/tmp/claude-0/tb3/x/trackb_v1/test')
def rd(p):
    d = pd.read_csv(p); return pd.to_numeric(d.set_index('id')['parsed_value'], errors='coerce')
test, val = load_split('test'), load_split('val')
pl = rd(ROOT / 'submissions/trackA_cand_combo2.csv')
t = test[~test.video_id.isin(set(val.video_id))].copy()
q = t.question.str.lower(); mot = q.str.contains('acceler|veloc|speed|travel')
sim = t.video_source.isin(['simulation', 'segmentation'])
t['sub'] = np.where((t.category == 'S2') & sim, 'S2sim', np.where((t.category == 'D2') & sim & ~mot, 'D2simstatic', ''))
t = t[t['sub'] != '']
geo = rd(TB / 'cvq/cv_geometry.csv'); fb = rd(TB / 'cvq/geometry.csv')
recs = {}
def minagree(vid, qid):
    if vid not in recs:
        recs[vid] = json.load(open(TB / 'cvq/annotate' / f'{vid}.json'))
    r = recs[vid]; ph = {o.get('phrase'): o.get('agree') for o in r['objects'].values()}
    tr = r['tracks'].get(str(qid), [])
    a = [ph.get(x['object']) for x in tr]; a = [x for x in a if x is not None]
    fl = r['flags'].get(str(qid), [])
    return (min(a) if a else np.nan), len(tr), ','.join(fl)
out = [minagree(v, qq) for v, qq in zip(t.video_id, t.qid)]
t['agree'] = [o[0] for o in out]; t['ntr'] = [o[1] for o in out]; t['flags'] = [o[2] for o in out]
t['pl'] = t.qid.map(pl); t['geo'] = t.qid.map(geo); t['fb'] = t.qid.map(fb)
ok = np.isfinite(t.fb) & (t.fb > 0)
t['it'] = item_scores(np.where(ok, t.fb, 1e-9), t.pl.values)
t['gross'] = np.abs(np.log(np.where(ok, t.fb, 1e-9) / t.pl)) > np.log(2)
t['nogeo'] = ~(np.isfinite(t.geo) & (t.geo > 0))
t['agree_cls'] = np.where(t.nogeo, 'no_geo(fallback)', np.where(t.agree < 0.8, 'drift<0.8', 'follows_qwen>=0.8'))
for s, g in t.groupby('sub'):
    print(s, 'rows', len(g), 'item', round(g.it.mean(), 3), 'gross', int(g.gross.sum()))
    print(g.groupby('agree_cls').agg(n=('qid', 'size'), item=('it', 'mean'), gross=('gross', 'sum'),
                                     loss=('it', lambda x: (1 - x).sum())).round(3).to_string())
t.to_csv(ROOT / 'research/r86/skeptic_tta/rows_gross_agree.csv', index=False)
