import runpy, sys, itertools, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
sys.argv = ['x']
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/pl/pseudo_tb.py')
fit, val, T, V, MEM, mra, lmed, mat, macro, best, apply_sets, apply_cells = (g[k] for k in
    ['fit','val','T','V','MEM','mra','lmed','mat','macro','best','apply_sets','apply_cells'])
from pathlib import Path
D = Path('/home/user/quantiphy-challenge/research/trackb_dense/out')
for m in ['qwen_dyn2s','qwen_dyn2','qwen_sparse_labfov','qwen_dense_labfov']:
    if (D/'test'/f'{m}.csv').exists() and (D/'val'/f'{m}.csv').exists():
        T[m] = pd.to_numeric(pd.read_csv(D/'test'/f'{m}.csv').set_index('id')['geo_value'], errors='coerce')
        V[m] = pd.to_numeric(pd.read_csv(D/'val'/f'{m}.csv').set_index('id')['geo_value'], errors='coerce')
def run(members, minn, kmax, cellcol='cell'):
    cs = {}
    for cell, f in fit.groupby(cellcol):
        if len(f) < minn: continue
        sc = [(mra(lmed(mat(f, T, ms)), f['pl'].values).mean(), ms) for k in range(1, kmax+1) for ms in itertools.combinations(members, k)]
        sc.sort(reverse=True); cs[cell] = list(sc[0][1])
    out = apply_sets(val, V, best)
    for cell, ms in cs.items():
        ff = (val[cellcol] == cell).values
        if ff.any(): out[ff] = lmed(mat(val[ff], V, ms))
    pf = apply_sets(fit, T, best)
    for cell, ms in cs.items():
        ff = (fit[cellcol] == cell).values; pf[ff] = lmed(mat(fit[ff], T, ms))
    return macro(val, out), mra(pf, fit['pl'].values).mean(), len(cs)
fit['cell2'] = fit['category'] + '|' + fit['src']; val['cell2'] = val['category'] + '|' + val['src']
base = list(MEM)
ext = base + [m for m in ['qwen_dyn2s','qwen_dyn2','qwen_sparse_labfov','qwen_dense_labfov'] if m in T]
print('extra members:', [m for m in ext if m not in base])
for members, name in [(base, 'base8'), (ext, 'ext')]:
    for minn, kmax, cc in [(25,3,'cell'),(50,3,'cell'),(25,2,'cell'),(25,1,'cell'),(25,3,'cell2'),(60,2,'cell2')]:
        (v, cats), p, n = run(members, minn, kmax, cc)
        print(f'{name:6s} min{minn} k<={kmax} {cc:5s} cells {n:2d} | val macro {v:.4f} {cats} | fit pl-MRA {p:.3f}')
