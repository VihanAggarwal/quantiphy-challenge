"""Track B 'bootstrap' feasibility (FAQ: closed outputs may be used in development, disclosed).
Pseudo-labels = Track A combo2 test predictions (scored .817). Fit ONLY on test rows of the 544 non-validation
videos; validation labels are used ONLY to score the final strategies (kill test)."""
import sys, itertools
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path('/home/user/quantiphy-challenge'); sys.path.insert(0, str(ROOT))
from qp.data import load_split
from qp.mra import item_scores
TB = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/tmp/claude-0/tb3/x/trackb_v1')
MEM = {'caw': 'caw/caw.csv', 'cv_geo': 'cv/geometry.csv', 'cv_geo_only': 'cv/cv_geometry.csv',
       'cvq_geo': 'cvq/geometry.csv', 'qwen_geo': 'qwen/geometry.csv', 'qwen_direct': 'qwen/direct.csv',
       'qwen35': 'qwen35/direct.csv', 'gemma4': 'gemma4/direct.csv'}
def rd(p):
    d = pd.read_csv(p); return pd.to_numeric(d.set_index('id')['parsed_value'], errors='coerce')
test, val = load_split('test'), load_split('val')
def kind(u):
    u = str(u).lower()
    return 'A' if ('s^2' in u or 's2' in u or 's²' in u) else ('V' if '/s' in u or 'per s' in u else 'L')
for d in (test, val):
    d['src'] = d['video_source'].astype(str).str.split('_').str[0]
    d['tk'] = d['target_unit'].map(kind); d['pk'] = d['inference_type'].str[0]
    d['cell'] = d['category'] + '|' + d['src'] + '|' + d['tk']
pl = rd(ROOT / 'submissions/trackA_cand_combo2.csv')
T = {m: rd(TB / 'test' / p) for m, p in MEM.items()}
V = {m: rd(TB / 'val' / p) for m, p in MEM.items()}
val_vids = set(val['video_id'])
fit = test[~test['video_id'].isin(val_vids)].copy()
fit['pl'] = fit['qid'].map(pl)
print('fit rows', len(fit), 'val rows', len(val), 'members', list(MEM))
def ok(x): return np.isfinite(x) & (x > 0)
def lmed(cols):
    a = np.log(np.where(ok(cols), cols, np.nan)); return np.exp(np.nanmedian(a, axis=1))
def mra(pred, gt):
    pred = np.where(ok(pred), pred, 1e-9); return item_scores(pred, gt)
def macro(df, pred):
    s = pd.Series(mra(pred, df['answer'].values), index=df.index)
    return s.groupby(df['category']).mean().mean(), s.groupby(df['category']).mean().round(3).to_dict()
def mat(df, src, ms):
    return np.column_stack([df['qid'].map(src[m]).values.astype(float) for m in ms])
# per-member pseudo-MRA on fit and true MRA on val, by category
rows = []
for m in MEM:
    pf = fit['qid'].map(T[m]).values.astype(float); pv = val['qid'].map(V[m]).values.astype(float)
    r = {'member': m}
    for c in ['S2', 'D2', 'S3', 'D3']:
        f = (fit['category'] == c).values; v = (val['category'] == c).values
        r[f'pl_{c}'] = mra(pf[f], fit['pl'].values[f]).mean(); r[f'val_{c}'] = mra(pv[v], val['answer'].values[v]).mean()
    rows.append(r)
R = pd.DataFrame(rows).set_index('member').round(3); print(R.to_string())
for c in ['S2', 'D2', 'S3', 'D3']:
    print(c, 'spearman(pl,val) =', round(R[f'pl_{c}'].rank().corr(R[f'val_{c}'].rank()), 2))
# strategy A: v3 per-category median sets (chosen on validation)
V3 = {'S2': ['caw', 'cv_geo', 'qwen_direct'], 'D2': ['caw', 'cv_geo', 'qwen_geo', 'qwen_direct'],
      'S3': ['cv_geo', 'qwen_geo', 'qwen_direct'], 'D3': ['caw', 'qwen_geo', 'qwen_direct']}
def apply_sets(df, src, sets_by_cat):
    out = np.full(len(df), np.nan)
    for c, ms in sets_by_cat.items():
        f = (df['category'] == c).values; out[f] = lmed(mat(df[f], src, ms))
    return out
pa = apply_sets(val, V, V3); print('A v3 sets (val-chosen) val macro', macro(val, pa))
# strategy C: per-category best median subset chosen by pseudo-MRA on fit rows
best = {}
for c in ['S2', 'D2', 'S3', 'D3']:
    f = fit[fit['category'] == c]; sc = []
    for k in range(1, 5):
        for ms in itertools.combinations(MEM, k):
            sc.append((mra(lmed(mat(f, T, ms)), f['pl'].values).mean(), ms))
    sc.sort(reverse=True); best[c] = list(sc[0][1]); print(c, 'pl-best set', sc[0][1], round(sc[0][0], 3), '| v3 set pl', round(mra(lmed(mat(f, T, V3[c])), f['pl'].values).mean(), 3))
pc = apply_sets(val, V, best); print('C pl-chosen sets val macro', macro(val, pc))
# strategy D: per-cell set chosen by pseudo-MRA (cells with >= 25 fit rows), else category set
def cell_sets(minn=25):
    cs = {}
    for cell, f in fit.groupby('cell'):
        if len(f) < minn: continue
        sc = [(mra(lmed(mat(f, T, ms)), f['pl'].values).mean(), ms) for k in range(1, 4) for ms in itertools.combinations(MEM, k)]
        sc.sort(reverse=True); cs[cell] = list(sc[0][1])
    return cs
CS = cell_sets()
def apply_cells(df, src, cs, fallback):
    out = apply_sets(df, src, fallback)
    for cell, ms in cs.items():
        f = (df['cell'] == cell).values
        if f.any(): out[f] = lmed(mat(df[f], src, ms))
    return out
pdd = apply_cells(val, V, CS, best); print('D pl-chosen per-cell sets val macro', macro(val, pdd), 'cells', len(CS))
# strategy E: D + per-cell multiplicative calibration toward pseudo-labels (median log ratio, shrunk by n/(n+50))
def calib(pred_fit, fdf, pred_val, vdf):
    out = pred_val.copy()
    lr = np.log(fdf['pl'].values) - np.log(np.where(ok(pred_fit), pred_fit, np.nan))
    s = pd.Series(lr, index=fdf.index).groupby(fdf['cell'])
    for cell, g in s:
        g = g.dropna(); n = len(g)
        if n < 15: continue
        b = np.median(g) * n / (n + 50)
        f = (vdf['cell'] == cell).values; out[f] = out[f] * np.exp(b)
    return out
pf_d = apply_cells(fit, T, CS, best)
print('pl-MRA on fit rows: v3 sets', round(mra(apply_sets(fit, T, V3), fit['pl'].values).mean(), 3), '| D', round(mra(pf_d, fit['pl'].values).mean(), 3))
pe = calib(pf_d, fit, pdd, val); print('E = D + per-cell calibration val macro', macro(val, pe))
pa_fit = apply_sets(fit, T, V3); pe2 = calib(pa_fit, fit, pa, val); print('F = A(v3) + per-cell calibration val macro', macro(val, pe2))
# video-clustered bootstrap of E - A on validation
rng = np.random.default_rng(0); vids = val['video_id'].values; uv = np.unique(vids)
sa, se = mra(pa, val['answer'].values), mra(pe, val['answer'].values)
def mac(s, idx):
    d = val.iloc[idx]; return pd.Series(s[idx]).groupby(d['category'].values).mean().mean()
bs = []
for _ in range(2000):
    pick = rng.choice(uv, len(uv)); idx = np.concatenate([np.where(vids == v)[0] for v in pick]); bs.append(mac(se, idx) - mac(sa, idx))
print('E - A val macro delta', round(macro(val, pe)[0] - macro(val, pa)[0], 4), '90% CI', np.round(np.percentile(bs, [5, 95]), 4))
