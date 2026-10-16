"""Per-row D2 internet table: p8 (pre-PHYSB, in-clip), p16, physb(p18), p21, physb2, combo3, base C1_solS2S3, agent."""
import sys
import numpy as np
import pandas as pd
R = '/home/user/quantiphy-challenge/'
t = pd.read_pickle(R + 'research/r86/loss_audit/master.pkl')
def L(f):
    d = pd.read_csv(R + 'submissions/' + f)
    return d.set_index(d.columns[0])['parsed_value'].reindex(t.index)
cols = {'p8': 'trackA_probe8_p7b_d2fixes_d3labphys.csv', 'p16': 'trackA_best_p16_p8_labnoiseS3D3.csv',
        'p18': 'trackA_probe18_p16_physb_sizeenv_sim3d.csv', 'p21': 'trackA_best_p21.csv',
        'pb2': 'trackA_cand_physb2_on_p21.csv', 'c3': 'trackA_combo3_on_combo2.csv',
        'base': 'trackA_cand_C1_solS2S3.csv', 'cur': 'trackA_probe_agent_sim2agent.csv'}
for k, f in cols.items():
    t[k] = L(f)
t.to_pickle('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/t_inet.pkl')
cat = sys.argv[1] if len(sys.argv) > 1 else 'D2'
vids = sys.argv[2].split(',') if len(sys.argv) > 2 else None
i = t[t.srcg.eq('internet') & t.category.eq(cat)].copy()
if vids:
    i = i[i.video_id.isin(vids)]
pd.set_option('display.width', 260); pd.set_option('display.max_colwidth', 70); pd.set_option('display.max_rows', 900)
for k in cols:
    if k != 'p8':
        i['r_' + k] = (i[k] / i['p8']).round(3)
print(i[['video_id', 'scored', 'kind', 'question', 'p8', 'r_p18', 'r_pb2', 'r_base', 'r_cur']].to_string())
