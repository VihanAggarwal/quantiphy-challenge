"""Independent checks of the candidate CSV against the base (format, scope, group consistency)."""
from common import *
import sys
cand = ROOT / 'submissions' / sys.argv[1]
b = pd.read_csv(BASE, float_precision='round_trip'); c = pd.read_csv(cand, float_precision='round_trip')
tm = pd.read_csv(ROOT / 'data/submission_template/quantiphy_submission_template.csv')
assert list(c.id) == list(tm.id) and list(c.columns) == list(b.columns)
assert (c.drop(columns='parsed_value').fillna('').astype(str).values == b.drop(columns='parsed_value').fillna('').astype(str).values).all()
pv = c.parsed_value.astype(float)
assert np.isfinite(pv).all() and (pv > 0).all()
t = test_df().set_index('qid')
ch = ~np.isclose(pv.values, b.parsed_value.values, rtol=1e-9)
ids = c.id[ch]
print('changed', ch.sum(), t.loc[ids].groupby(['category', 'video_source']).size().to_dict())
vl = val_labels()
print('changed rows that are validation overlaps (unscored):', int(ids.isin(vl.index).sum()))
r = pv[ch].values / b.parsed_value[ch].values
print('ratio quantiles', np.round(np.quantile(r, [0, .1, .25, .5, .75, .9, 1]), 3))
# scored-row impact by category (for the overall formula)
n = int((~ids.isin(vl.index)).sum())
print('scored changed D3 rows', n, ' -> overall gain = item_gain_per_row * %d / (4*933) = %.5f x item gain' % (n, n / (4 * 933)))
