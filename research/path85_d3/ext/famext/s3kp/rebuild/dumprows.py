from build_s3 import *
from eval_famknown import known, SUSPECT_T
res,allch=pickle.load(open(OUT+'/build_res.pkl','rb'))
F=pd.read_pickle(W+'/work/facts.pkl')
ch=allch['S3_PK_DS']
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',80)
for q,v in ch.items():
    r=ti.loc[q]
    print('='*100)
    print(f"Q{q} {r.video_id} [{r.category}] {r.question!r} | prior={r.prior!r} | unit={r.target_unit} | tkind={r.tkind} tobj={r.tobj} tdim={r.tdim} t={r.ttime} | v3={v3[q]:.4g} p5={p5[q]:.4g} new={v:.4g} known={known.get(q)}")
    per=per_base_values(ti,eq,q,include_self=True)
    for b,(rk,vv,p) in sorted(per.items()):
        rp=ti.loc[p]
        mv=member_val(p,frozenset(),'kind')
        print(f"   member Q{p} {rp.video_id} {rp.category} m={rp.method} {rp.question[:70]!r} prior={str(rp.prior)[:50]!r} v3={v3[p]:.4g} p5={p5[p]:.4g} member={mv:.4g} unit={rp.target_unit} known={known.get(p)}")
    others=[p for p in eq[q] if p not in [x[2] for x in per.values()]]
    if others: print('   non-member eq:',[(p,ti.loc[p,'video_id'],ti.loc[p,'category']) for p in others])
