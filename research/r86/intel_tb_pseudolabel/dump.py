import runpy, sys, io, contextlib, warnings, itertools, json, numpy as np, pandas as pd
warnings.filterwarnings('ignore'); sys.argv=['x']
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/pl/pseudo_tb.py')
fit, val, T, V, MEM, mra, lmed, mat, best = (g[k] for k in ['fit','val','T','V','MEM','mra','lmed','mat','best'])
rows = []
for cell, f in fit.groupby('cell'):
    n = len(f)
    if n < 25: continue
    sc = sorted([(mra(lmed(mat(f, T, ms)), f['pl'].values).mean(), ms) for k in (1, 2) for ms in itertools.combinations(MEM, k)], reverse=True)
    rows.append({'cell': cell, 'n_fit': n, 'members': '+'.join(sc[0][1]), 'pl_mra': round(sc[0][0], 3), 'runner_up': '+'.join(sc[1][1]), 'runner_up_pl': round(sc[1][0], 3)})
out = '/home/user/quantiphy-challenge/research/r86/intel_tb_pseudolabel/routing_base8_min25_k2.csv'
pd.DataFrame(rows).to_csv(out, index=False); print(pd.DataFrame(rows).to_string())
json.dump({c: m for c, m in best.items()}, open(out.replace('routing_base8_min25_k2.csv', 'fallback_category_sets.json'), 'w'), indent=1)
