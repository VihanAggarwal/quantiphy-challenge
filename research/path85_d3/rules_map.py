"""Which Track A rule set each D3 non-lab row's current value (physb2_on_p21)."""
from common import *
SP = '/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
d5 = pd.read_csv(SP + '/merge/D3/decisions.csv').set_index('qid')
dx = pd.read_csv(SP + '/ext/d3rest/decisions_ext.csv').set_index('qid')
S = {s: read_sub(ROOT / f'submissions/{s}.csv') for s in ['trackA_v3_best_per_category', 'trackA_probe5_families_merged',
     'trackA_probe7a_p5_ensemble3dnl', 'trackA_probe7b_p5_ens_famext', 'trackA_cand_physb2_on_p21']}
R = pd.read_pickle(OUT / 'repool_D3.pkl')
t = test_df().set_index('qid')
R['rule5'] = d5.chosen_source.reindex(R.index).fillna('')
R['rule7b'] = dx.rule.reindex(R.index).fillna('')
for k, s in S.items():
    R[k.replace('trackA_', '')[:10]] = s.reindex(R.index)
R['same_7b'] = np.isclose(R.cur, S['trackA_probe7b_p5_ens_famext'].reindex(R.index), rtol=1e-9)
R['rule'] = np.where(R.rule7b != '', '7b:' + R.rule7b, np.where(R.rule5 != '', '5:' + R.rule5, ''))
R.loc[R.fact & (R.rule == ''), 'rule'] = 'fact?'
print(pd.crosstab(R.rule, R.same_7b))
R.to_pickle(OUT / 'rules_D3.pkl')
x = R[~R.same_7b]
pd.set_option('display.width', 250)
print(x[['video', 'kind', 'rule', 'ens', 'cur', 'probe7b_p5']].round(3).head(40).to_string())
