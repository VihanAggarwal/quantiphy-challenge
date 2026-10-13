"""Cross-family asset candidates: a D3/S3 non-lab size question whose object a simulation clip OUTSIDE its family states
(same dimension, same head noun, name_score >= .6). Test inputs only."""
from lofo import *
from qp.geometry import name_score
facts = pp._parse_facts(pp._questions(load_split('test')))
sz = [f for f in facts if f.kind == 'size' and pp.is_simulation(f.video_id)]
famof = dict(zip(TS.video_id, TS.fam))
cur = read_sub()
rows = []
for q in ti.index:
    r = ti.loc[q]
    if r.category not in ('D3', 'S3') or not nl3[q] or r.tkind != 'size': continue
    s = pp._spec(r if hasattr(r, 'question') else None) if False else None
    t_ = pp._spec(type('R', (), dict(question=r.question, target_unit=r.target_unit))())
    if len(t_.objs) != 1: continue
    obj = t_.objs[0]
    for f in sz:
        if famof.get(f.video_id) == r.fam: continue
        if f.dimension != t_.dim: continue
        ns = pp._same_object(obj, f.obj)
        if ns < 0.6: continue
        rows.append(dict(qid=q, cat=r.category, video=r.video_id, fam=r.fam, obj=obj, dim=t_.dim, src=f.video_id, sobj=f.obj,
                         ns=round(ns, 2), stated=f.si / t_.to_si, cur=cur[q], ens=ENS[q]))
C = pd.DataFrame(rows)
C['ratio'] = C.stated / C.cur
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 400)
print(len(C), C.qid.nunique(), C.groupby('cat').qid.nunique().to_dict())
print(C.sort_values(['obj', 'video']).round(3).to_string())
C.to_pickle(OUT / 'asset_cands.pkl')
