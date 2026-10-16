import pandas as pd, numpy as np, re, sys
sys.path.insert(0, '.')
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 70); pd.set_option('display.max_rows', 900)
m = pd.read_pickle('research/r86/loss_audit/master.pkl')
b = pd.read_csv('submissions/trackA_probe_agent_sim2agent.csv').set_index('id')
m['best'] = b.loc[m.index, 'parsed_value'].values
lab = m[(m.srcg == 'lab') & (~m.motion)].copy()
lab['fam'] = lab.video_id.str.replace(r'(captured_\d+[ab]?)[sxX]?$', r'\1', regex=True)
lab['nq'] = lab.question.str.lower().str.replace(r'[^a-z0-9.]', '', regex=True)
rows = []
for (fam, nq), g in lab.groupby(['fam', 'nq']):
    vals = pd.concat([g.r_direct_value, g.r_geo_value]).dropna()
    vals = vals[vals > 0]
    sp = np.log(vals.max() / vals.min()) if len(vals) > 1 else 0
    bsp = np.log(g.best.max() / g.best.min())
    rows.append(dict(fam=fam, cat=g.category.iloc[0], kg=g.kg.iloc[0], n=len(g), nsc=int(g.scored.sum()), q=g.question.iloc[0][:70],
                     best=' '.join(f'{v:.3g}' for v in g.best), dirs=' '.join(f'{v:.3g}' for v in g.r_direct_value),
                     geos=' '.join(f'{v:.3g}' for v in g.r_geo_value), spread=round(sp, 2), bspread=round(bsp, 2), fact=g.fact.iloc[0]))
G = pd.DataFrame(rows).sort_values('spread', ascending=False)
G.to_csv('research/next/labstatic/groups.csv', index=False)
print(G[G.spread > 0.25].to_string())
