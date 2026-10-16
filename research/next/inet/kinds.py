"""Agent vs base on scored internet rows by kind / prior type / camera motion (from agent notes), with and without
the PHYSB clips, current best vs candidate. Test inputs only (no labels)."""
import re
import numpy as np
import pandas as pd
R = '/home/user/quantiphy-challenge/'
t = pd.read_pickle(R + 'research/r86/loss_audit/master.pkl')
def L(f):
    d = pd.read_csv(R + 'submissions/' + f); return d.set_index(d.columns[0])['parsed_value'].reindex(t.index)
t['cur'] = L('trackA_probe_agent_sim2agent.csv'); t['base'] = L('trackA_cand_C1_solS2S3.csv'); t['new'] = L('trackA_cand_next_inet.csv')
i = t[t.srcg.eq('internet') & t.scored].copy()
cam = {}
for v in i.video_id.unique():
    s = open(f'{R}research/blind/out/blind_test/{v}/notes.md').read().lower()
    moving = bool(re.search(r'\bpans?\b|panning|handheld|tracking shot|camera (moves|follows)|moving camera', s))
    cam[v] = 'moving' if moving else 'static'
i['cam'] = i.video_id.map(cam)
i['physb'] = i.video_id.isin(['internet_00%s' % x for x in ('43', '45', '47', '51', '53', '54', '55', '69')])
i['selff'] = i.video_id.str[-4:].astype(int).between(43, 70)
i['lr_cur'] = np.log(i.cur / i.base); i['lr_new'] = np.log(i.new / i.base)
def s(g):
    return pd.Series({'n': len(g), 'med|lr| cur': g.lr_cur.abs().median(), '>15% cur': (g.lr_cur.abs() > np.log(1.15)).mean(),
                      'mean lr cur': g.lr_cur.mean(), '>15% new': (g.lr_new.abs() > np.log(1.15)).mean(), 'mean lr new': g.lr_new.mean()})
pd.set_option('display.width', 250)
for keys in (['category', 'kind'], ['category', 'cam'], ['category', 'selff', 'physb'], ['category', 'pk']):
    print(i.groupby(keys).apply(s).round(3).to_string(), "\n")
