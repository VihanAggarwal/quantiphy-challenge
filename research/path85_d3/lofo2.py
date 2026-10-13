"""LOFO variants with base-level ensembles (original + segmented twin = 6 Claude reads of one camera)."""
from lofo import *
# twin partner of each row: same base, other clip, same normalized question / prior / depth / unit
TSi = TS.set_index('qid')
key = TS.assign(nq=TS.question.map(pp.norm_question), pr=TS.prior.map(pp.exact_text), di=TS.depth_info.map(pp.exact_text))
grp = key.groupby(['base', 'nq', 'pr', 'di', 'target_unit']).qid.apply(list)
partner = {}
for qs in grp:
    if len(qs) >= 2:
        for q in qs:
            partner[q] = [p for p in qs if p != q]

def base_vals(q, col_runs=True):
    """all run values of q and its same-camera twin(s) (3D non-lab, direct only)"""
    out = []
    for p in [q] + partner.get(q, []):
        if ti.loc[p, 'method'] != 'direct' or not nl3[p]: continue
        out += [RV[r][p] for r in RUNS]
    return out

def corr_val(p, ex, val, useK=True):
    if useK and is_direct(p) and ti.loc[p, 'tkind'] in ('size', 'speed'):
        val = val * math.exp(clipK(ti.loc[p, 'video_id'], ex, ENS))
    return val

def ens6(q, ex, useK):
    vals = []
    for p in [q] + partner.get(q, []):
        if ti.loc[p, 'method'] != 'direct' or not nl3[p]: continue
        vals += [corr_val(p, ex, RV[r][p], useK) for r in RUNS]
    return gmed(vals) if vals else kcorr(q, ex, ENS, useK)

def kp6(q, ex, minb=3, useK=True, tm=False):
    per = per_base(q)
    if len(per) < minb:
        return ens6(q, ex, useK)
    votes = []
    for b, p in per.items():
        votes.append(ens6(p, ex, useK) * USC[p])
    return (trim_mean(votes) if tm else gmed(votes)) / USC[q]

def run2(cats=('D3',), minb=3):
    rows = []
    for fact, g in A.groupby('fact'):
        ex = {fact}
        for r in g.itertuples():
            if r.cat not in cats or r.method != 'direct' or r.src_type == 'lab': continue
            q = r.qid
            preds = dict(ens=ENS[q], ens6=ens6(q, ex, False), Kens=kcorr(q, ex, ENS, True), Kens6=ens6(q, ex, True),
                         cur=predict(q, ex, 'cur', 3), KPens=predict(q, ex, 'KPens', minb), KP6=kp6(q, ex, minb), KP6tm=kp6(q, ex, minb, tm=True),
                         P6=kp6(q, ex, minb, useK=False))
            row = dict(cat=r.cat, qid=q, fam=ti.loc[q, 'fam'], fact=fact, kind=r.kind, V=r.value, has_twin=q in partner)
            for k, p in preds.items():
                row[k] = mra1(p, r.value)
            rows.append(row)
    return pd.DataFrame(rows)

if __name__ == '__main__':
    M = ['ens', 'ens6', 'Kens', 'Kens6', 'cur', 'KPens', 'KP6', 'KP6tm', 'P6']
    for cats in (('D3',), ('S3',)):
        for mb in (3, 2):
            R = run2(cats, mb)
            print(cats, 'minb', mb, 'n', len(R), 'twin rows', R.has_twin.sum())
            print('  row ', R[M].mean().round(3).to_dict())
            print('  fam ', R.groupby('fam')[M].mean().mean().round(3).to_dict())
            for a, b in [('ens6', 'ens'), ('Kens6', 'Kens'), ('KP6', 'KPens'), ('KP6', 'cur'), ('KP6tm', 'cur')]:
                print('   ', a, '-', b, np.round(boot_delta(R[a], R[b], R.fam), 4))
            R.to_pickle(OUT / f"lofo2_{cats[0]}_mb{mb}.pkl")
