"""Seed-diversity proxy: cv (Grounding DINO box seeds SAM 2) and cvq (Qwen box seeds SAM 2) share SAM 2 + geometry and
differ only in the seed. If their log-mean / disagreement flag does not beat cvq alone, multi-seed TTA from the SAME
Qwen grounding (less diverse than cv vs cvq) will not either. Pseudo-labels = Track A combo2 (test, non-val videos);
validation labels only to score."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path('/home/user/quantiphy-challenge'); sys.path.insert(0, str(ROOT))
from qp.data import load_split
from qp.mra import item_scores
TB = Path('/tmp/claude-0/tb3/x/trackb_v1')
def rd(p):
    d = pd.read_csv(p); return pd.to_numeric(d.set_index('id')['parsed_value'], errors='coerce')
test, val = load_split('test'), load_split('val')
pl = rd(ROOT / 'submissions/trackA_cand_combo2.csv')
vv = set(val.video_id)
def sub(df):
    q = df.question.str.lower(); mot = q.str.contains('acceler|veloc|speed|travel')
    sim = df.video_source.isin(['simulation', 'segmentation'])
    return {'S2sim': (df.category == 'S2') & sim, 'D2simstatic': (df.category == 'D2') & sim & ~mot}
def ok(x): return np.isfinite(x) & (x > 0)
def sc(pred, gt):
    pred = np.where(ok(pred), pred, 1e-9); return item_scores(pred, gt)
for split, df, ref in (('test-pseudo', test[~test.video_id.isin(vv)], lambda d: d.qid.map(pl).values),
                       ('val-true', val, lambda d: d.answer.values)):
    S = sub(df)
    M = {m: df.qid.map(rd(TB / split.split('-')[0] / p)).values.astype(float) for m, p in
         {'cvq_only': 'cvq/cv_geometry.csv', 'cv_only': 'cv/cv_geometry.csv', 'cvq_fb': 'cvq/geometry.csv',
          'caw': 'caw/caw.csv'}.items()}
    for name, m in S.items():
        m = m.values; y = ref(df)[m]
        a, b, fb = M['cvq_only'][m], M['cv_only'][m], M['cvq_fb'][m]
        both = ok(a) & ok(b)
        gm = np.where(both, np.sqrt(np.where(both, a * b, 1)), fb)
        lr = np.abs(np.log(np.where(both, a / np.where(both, b, 1), 1)))
        flag = both & (lr > np.log(1.5))
        print(f'{split:11s} {name:12s} n={m.sum():4d} cvq geo cov={ok(a).mean():.2f} cv cov={ok(b).mean():.2f} both={both.mean():.2f}'
              f' | cvq_fb {sc(fb, y).mean():.3f}  gm(cv,cvq)|fb {sc(gm, y).mean():.3f}'
              f' | both rows: cvq {sc(a[both], y[both]).mean():.3f} cv {sc(b[both], y[both]).mean():.3f} gm {sc(gm[both], y[both]).mean():.3f}'
              f' | |log(cvq/cv)| med {np.median(lr[both]):.3f} >1.5x {flag.sum()/max(both.sum(),1):.2f}'
              f' | flagged rows cvq {sc(a[flag], y[flag]).mean() if flag.any() else np.nan:.3f} vs unflagged {sc(a[both & ~flag], y[both & ~flag]).mean():.3f}'
              f' | gross>2x cvq_fb {(np.abs(np.log(np.where(ok(fb), fb, 1e-9) / y)) > np.log(2)).mean():.2f}')
