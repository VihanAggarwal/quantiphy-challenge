"""EVALUATION ONLY: validation lab questions; compare original-render direct vs median of the three renders' direct
answers (each render is a separate Claude call on the same event = same label)."""
import pandas as pd, numpy as np
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE.parents[1]))
from qp.mra import item_scores
v = pd.read_pickle(HERE / 'out/val_lab.pkl')
t = pd.read_pickle(HERE / 'out/labtable.pkl')
t['qn'] = t.question.str.strip().str.lower()
rows = []
for _, r in v.iterrows():
    fam = t.loc[r.tq, 'family']; qn = r.question.strip().lower()
    g = t[(t.family == fam) & (t.qn == qn)]
    o = g[g.render == '']
    dd = g.direct.dropna(); gg = g.geo.dropna(); gg = gg[gg > 0]
    rows.append(dict(video=r.video_id, kind=r.kind, cat=r.category, label=r.answer, n=len(g),
                     d_o=float(o.direct.iloc[0]) if len(o) else np.nan, d_med=float(np.median(dd)),
                     d_lmean=float(np.exp(np.log(dd).mean())),
                     g_o=float(o.geo.iloc[0]) if len(o) else np.nan, g_med=float(np.median(gg)) if len(gg) else np.nan,
                     best_o=float(o.best.iloc[0]) if len(o) else np.nan))
D = pd.DataFrame(rows)
cols = ['d_o', 'd_med', 'd_lmean', 'g_o', 'g_med', 'best_o']
for c in cols:
    D['s_' + c] = item_scores(D[c], D.label)
pd.set_option('display.width', 250)
print(D.groupby('kind')[['s_' + c for c in cols]].mean().round(3))
print(D[['s_' + c for c in cols]].mean().round(3), len(D))
D['ev'] = D.video.str.replace(r'[sx]$', '', regex=True)
rng = np.random.default_rng(0); evs = D.ev.unique()
for a, b in (('d_med', 'd_o'), ('d_lmean', 'd_o')):
    diffs = []
    for _ in range(4000):
        s = rng.choice(evs, len(evs)); x = pd.concat([D[D.ev == e] for e in s]); diffs.append((x['s_' + a] - x['s_' + b]).mean())
    print('%s - %s: %.3f  90%% CI [%.3f, %.3f] (n=%d rows, %d events)' % (a, b, (D['s_' + a] - D['s_' + b]).mean(), *np.percentile(diffs, [5, 95]), len(D), len(evs)))
mot = D[D.kind.isin(['speed', 'path_length', 'displacement', 'acceleration'])]
print('motion only n=%d: d_o %.3f d_med %.3f d_lmean %.3f' % (len(mot), mot.s_d_o.mean(), mot.s_d_med.mean(), mot.s_d_lmean.mean()))
