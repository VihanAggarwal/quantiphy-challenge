"""D3 sim extension on probe 5: extended families -> T (new stated facts), K (clip scale from facts), P (series pooling).
Only rows that probe 5 left at their v3 value are candidates for K/P; T applies to any D3 row not already a stated fact."""
import sys, os, pickle, json
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
W=SP+'/big/scenegraph/work'; EXT=SP+'/ext/d3rest'; R='/home/user/quantiphy-challenge'
sys.path.insert(0,R); sys.path.insert(0,W)
import numpy as np, pandas as pd
from qp.mra import item_scores
from pool2 import per_base_values, gmed
def mra(p,g): return float(item_scores([p],[g])[0])
t=pd.read_pickle(EXT+'/work/TS_ext.pkl'); ti=t.set_index('qid')
A=pd.read_pickle(EXT+'/work/transfers_ext.pkl'); A=A[~A.conflict].copy()
A_old=pd.read_pickle(W+'/transfers3.pkl')
eq=pickle.load(open(EXT+'/work/eq_ext.pkl','rb'))
p5=pd.read_csv(R+'/submissions/trackA_probe5_families_merged.csv').set_index('id').parsed_value
v3=ti.v3
dec=pd.read_csv(SP+'/merge/D3/decisions.csv').set_index('qid')
src=dec.chosen_source.reindex(ti.index).fillna('v3')
D3=ti[ti.category=='D3'].index
untouched=[q for q in D3 if np.isclose(p5[q],v3[q],rtol=1e-9)]
A['lk']=np.log(A.value/A.v3); A['kind']=ti.loc[A.qid,'tkind'].values
def is_direct(q):
    d=pd.to_numeric(ti.loc[q,'direct'],errors='coerce'); return bool(d>0 and abs(v3[q]/d-1)<1e-6)
KC={}
for v,g in A[A.kind.isin(('size','speed'))].groupby('video_id'): KC[v]=float(np.median(np.r_[g.lk.values,0.0]))
def corrected(q,useK):
    val=v3[q]
    if useK and is_direct(q) and ti.loc[q,'tkind'] in ('size','speed'): val*=np.exp(KC.get(ti.loc[q,'video_id'],0.0))
    return val
from qp.parse import canonical_unit, _UNITS
def usc(q):
    cu=canonical_unit(ti.loc[q,'target_unit'] or 'm') or 'm'
    return _UNITS[cu][0] if cu in _UNITS else 1.0
def pooled(q,useK,minb):
    per=per_base_values(ti,eq,q,col='v3',include_self=True)
    if len(per)<minb: return None,len(per)
    return gmed([corrected(x[2],useK)*usc(x[2]) for x in per.values()])/usc(q), len(per)
def build(useT=True,useK=True,useP=True,minb=3):
    new=dict(p5); why={}
    Tv={r.qid:r.value for r in A.itertuples() if r.cat=='D3'}
    for q in D3:
        if useT and q in Tv and not src[q].endswith('FACT') and not np.isclose(Tv[q],p5[q],rtol=1e-9):
            new[q]=Tv[q]; why[q]='T_ext'; continue
        if q not in untouched or q in Tv: continue
        r=ti.loc[q]
        if not r.video_id.startswith('simulation') or r.tkind not in ('size','speed') or not is_direct(q): continue
        val=None
        if useP:
            pv,nb=pooled(q,useK,minb)
            if pv is not None and np.isfinite(pv) and not np.isclose(pv,p5[q],rtol=1e-9): val=pv; why[q]='P_ext'
        if val is None and useK and KC.get(r.video_id,0)!=0:
            val=corrected(q,True); why[q]='K_ext'
        if val is not None: new[q]=val
    return new,why
# known rows
m=pd.read_csv(SP+'/hyp/S2/val_test_map.csv').sort_values('sim').drop_duplicates('tqid',keep='last'); m=m[m.sim>=0.9]
SUS={403,2349,2607,3049,3051,1123,1130,1354,1355,3054,139,2276}; m=m[~m.vqid.isin(SUS)]
known={q:a for q,a in zip(m.tqid,m.answer) if q in set(D3)}
if __name__=='__main__':
    for cfg in [dict(useT=True,useK=False,useP=False),dict(useT=True,useK=True,useP=False),dict(useT=True,useK=False,useP=True),dict(useT=True,useK=True,useP=True),dict(useT=True,useK=True,useP=True,minb=2),dict(useT=True,useK=False,useP=True,minb=2)]:
        new,why=build(**cfg)
        ch=[q for q in D3 if not np.isclose(new[q],p5[q],rtol=1e-9)]
        kq=list(known); k0=np.mean([mra(p5[q],known[q]) for q in kq]); k1=np.mean([mra(new[q],known[q]) for q in kq])
        kch=[q for q in kq if q in ch]
        tg=sum(1-mra(p5[q],new[q]) for q in ch if why[q]=='T_ext')/969
        print(cfg,'changed',len(ch),pd.Series([why[q] for q in ch]).value_counts().to_dict(),'known %.4f->%.4f (%d ch)'%(k0,k1,len(kch)),'T if-right +%.4f'%tg)
        for q in kch: print('    known',q,ti.loc[q,'video_id'],ti.loc[q,'question'][:60],'p5=%.3g new=%.3g gt=%.3g'%(p5[q],new[q],known[q]),why[q])
