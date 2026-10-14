"""Free proxy for the proposal's 'spread flag -> route to another member': flags that exist TODAY without new GPU
runs (cv-vs-cvq seed disagreement > 1.5x; SAM 2 drift from Qwen's own boxes agree < 0.8). On flagged rows, what do
other members score vs cvq? Pseudo-labels = Track A combo2 (test, non-val videos)."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path('/home/user/quantiphy-challenge'); sys.path.insert(0, str(ROOT))
from qp.mra import item_scores
TB = Path('/tmp/claude-0/tb3/x/trackb_v1/test')
def rd(p):
    d = pd.read_csv(p); return pd.to_numeric(d.set_index('id')['parsed_value'], errors='coerce')
t = pd.read_csv(ROOT / 'research/r86/skeptic_tta/rows_gross_agree.csv')
MEM = {'cvq': 'cvq/geometry.csv', 'cv': 'cv/geometry.csv', 'caw': 'caw/caw.csv', 'qwen_geo': 'qwen/geometry.csv',
       'qwen_direct': 'qwen/direct.csv', 'qwen35': 'qwen35/direct.csv', 'gemma4': 'gemma4/direct.csv'}
for m, p in MEM.items():
    t[m] = t.qid.map(rd(TB / p))
cvonly = t.qid.map(rd(TB / 'cv/cv_geometry.csv')); cvqonly = t.qid.map(rd(TB / 'cvq/cv_geometry.csv'))
both = np.isfinite(cvonly) & np.isfinite(cvqonly) & (cvonly > 0) & (cvqonly > 0)
t['seedflag'] = both & (np.abs(np.log(cvqonly / cvonly)) > np.log(1.5))
t['driftflag'] = t.agree < 0.8
def sc(x, y):
    x = np.where(np.isfinite(x) & (x > 0), x, 1e-9); return item_scores(x, y)
others = ['caw', 'qwen_geo', 'qwen_direct', 'qwen35', 'gemma4']
t['med_others'] = np.exp(np.nanmedian(np.log(t[others].where(t[others] > 0)), axis=1))
for s, g in t.groupby('sub'):
    for fl in ('seedflag', 'driftflag'):
        f = g[g[fl]]
        r = {m: sc(f[m].values, f.pl.values).mean() for m in ['cvq', 'cv'] + others + ['med_others']}
        best = max((k for k in r if k != 'cvq'), key=r.get)
        print(f'{s:12s} {fl:9s} n={len(f):3d} ' + ' '.join(f'{k} {v:.3f}' for k, v in r.items()) +
              f' | best alt {best} {r[best]-r["cvq"]:+.3f}/row -> {len(f)*(r[best]-r["cvq"]):+.1f} item pts (in-sample pick)')
