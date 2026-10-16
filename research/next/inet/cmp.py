"""Compare agent (current best) vs base (C1_solS2S3) on internet rows, by kind and video type."""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, '/home/user/quantiphy-challenge')
t = pd.read_pickle('/home/user/quantiphy-challenge/research/r86/loss_audit/master.pkl')
def L(f):
    d = pd.read_csv('/home/user/quantiphy-challenge/submissions/' + f)
    return d.set_index(d.columns[0])['parsed_value'].reindex(t.index)
cur = L('trackA_probe_agent_sim2agent.csv'); base = L('trackA_cand_C1_solS2S3.csv')
t['cur'] = cur; t['base'] = base
t['lr'] = np.log(cur / base)
i = t[t.srcg.eq('internet') & t.scored].copy()
i['cam'] = i.video_type.str[3]
i['pri'] = i.video_type.str[0]
i['objs'] = i.video_type.str[2]
pd.set_option('display.width', 250)
def summ(g):
    return pd.Series({'n': len(g), 'med_lr': g.lr.median(), 'mean_lr': g.lr.mean(), 'mad': g.lr.abs().median(),
                      'gt15': (g.lr.abs() > np.log(1.15)).mean(), 'up': (g.lr > 0.02).mean(), 'dn': (g.lr < -0.02).mean()})
for keys in [['category'], ['category', 'kind'], ['category', 'pri'], ['category', 'cam'], ['category', 'pri', 'kind'], ['category','motion']]:
    print(i.groupby(keys).apply(summ).round(3))
print()
g = i.groupby(['category', 'video_id']).agg(vt=('video_type', 'first'), prior=('prior', 'first'), n=('lr', 'size'),
                                           med=('lr', 'median'), mn=('lr', 'min'), mx=('lr', 'max'))
pd.set_option('display.max_colwidth', 60); pd.set_option('display.max_rows', 500)
print(g[g.index.get_level_values(0) == 'D2'].round(3).to_string())
