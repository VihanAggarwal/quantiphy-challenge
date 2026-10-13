"""Re-derive K / P on the 3-run ensemble for D3 non-lab rows and compare with the current submission."""
from lofo import *
cur = read_sub().reindex(ti.index)
nlD3 = ti[(ti.category == 'D3') & nl3].index
facts_q = set(A.qid)
rows = []
for q in nlD3:
    per = per_base(q)
    K_ens = clipK(ti.loc[q, 'video_id'], set(), ENS); K_v1 = clipK(ti.loc[q, 'video_id'], set(), V3)
    kp_ens = predict(q, set(), 'KPens', 3); kp_ens2 = predict(q, set(), 'KPens', 2)
    kp_runs = predict(q, set(), 'KPruns', 3); kp_runs2 = predict(q, set(), 'KPruns', 2)
    curstyle = predict(q, set(), 'cur', 3)
    rows.append(dict(qid=q, video=ti.loc[q, 'video_id'], kind=ti.loc[q, 'tkind'], method=ti.loc[q, 'method'], nb=len(per),
                     fact=q in facts_q, K_ens=K_ens, K_v1=K_v1, v1=V3[q], ens=ENS[q], cur=cur[q], curstyle=curstyle,
                     KPens=kp_ens, KPens2=kp_ens2, KPruns=kp_runs, KPruns2=kp_runs2, val=np.nan))
R = pd.DataFrame(rows).set_index('qid')
R['val'] = val_labels().reindex(R.index)
R['cur_eq_ens'] = np.isclose(R.cur, R.ens, rtol=1e-6)
R['cur_eq_style'] = np.isclose(R.cur, R.curstyle, rtol=1e-3)
R.to_pickle(OUT / 'repool_D3.pkl')
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 600)
x = R[~R.fact & (R.method == 'direct')]
print('non-fact direct D3 nl rows', len(x), ' cur==ens', x.cur_eq_ens.sum(), ' cur==curstyle', x.cur_eq_style.sum())
print('nb dist', x.nb.value_counts().sort_index().to_dict())
d = np.log(x.KPens / x.cur)
print('|log KPens/cur| > .02:', (d.abs() > .02).sum(), ' >.05:', (d.abs() > .05).sum(), ' >.10', (d.abs() > .1).sum())
d2 = np.log(x.KPens2 / x.cur)
print('KPens2: |log/cur| > .02:', (d2.abs() > .02).sum(), ' >.05:', (d2.abs() > .05).sum(), ' >.10', (d2.abs() > .1).sum())
# validation (overlap rows; evaluation only)
v = R[R.val.notna() & ~R.fact]
for c in ['v1', 'ens', 'cur', 'curstyle', 'KPens', 'KPens2', 'KPruns', 'KPruns2']:
    v['m_' + c] = [mra1(p, g) for p, g in zip(v[c], v.val)]
print('val overlap rows', len(v), v[[c for c in v.columns if c.startswith('m_')]].mean().round(3).to_dict())
