"""Share of S2 sim / D2 sim-static Track B rows whose v3 answer is NOT the member median (family rules overwrote it)."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path('/home/user/quantiphy-challenge'); sys.path.insert(0, str(ROOT))
TB = Path('/tmp/claude-0/tb3/x/trackb_v1/test')
def rd(p):
    d = pd.read_csv(p); return pd.to_numeric(d.set_index(d.columns[0])['parsed_value'], errors='coerce')
t = pd.read_csv(ROOT / 'research/r86/skeptic_tta/rows_gross_agree.csv')
v3 = rd(ROOT / 'submissions/trackB_v3_catmedian_famrules.csv')
SETS = {'S2': ['caw/caw.csv', 'cv/geometry.csv', 'qwen/direct.csv'],
        'D2': ['caw/caw.csv', 'cv/geometry.csv', 'qwen/geometry.csv', 'qwen/direct.csv']}
for s, g in t.groupby('sub'):
    c = 'S2' if s.startswith('S2') else 'D2'
    M = np.column_stack([g.qid.map(rd(TB / p)).values for p in SETS[c]]).astype(float)
    med = np.exp(np.nanmedian(np.log(np.where(M > 0, M, np.nan)), axis=1))
    fin = g.qid.map(v3).values
    same = np.isclose(med, fin, rtol=1e-3)
    print(s, 'rows', len(g), 'v3 = raw member median on', int(same.sum()), f'({same.mean():.2f}); rule-changed', int((~same).sum()))
