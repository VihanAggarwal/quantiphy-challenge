from eq import *
def comps_of(eq):
    seen=set(); comps=[]
    for q in eq:
        if q in seen: continue
        st=[q]; comp=set()
        while st:
            x=st.pop()
            if x in comp: continue
            comp.add(x); st.extend(eq.get(x,()))
        seen|=comp; comps.append(sorted(comp))
    return comps
def gmean(v):
    v=np.asarray([x for x in v if x>0 and np.isfinite(x)],float); return float(np.exp(np.mean(np.log(v))))
def gmed(v):
    v=np.asarray([x for x in v if x>0 and np.isfinite(x)],float); return float(np.exp(np.median(np.log(v))))
def to_si(ti,q,val):
    from qp.parse import canonical_unit,_UNITS
    tu=ti.loc[q,'target_unit']
    u=canonical_unit(str(tu)) if tu else None
    return val*(_UNITS[u][0] if u in _UNITS else 1.0)
def pool_values(t, col, cats_member=('S2','D2'), stat='median', motion_rule='scen', minb=2, kinds=('size','speed','acceleration','displacement')):
    """returns dict qid -> (pooled SI value, nbases, spread) for every member qid in a 2D group"""
    ti=t.set_index('qid')
    eq=groups(t,motion_rule=motion_rule,cats=cats_member)
    out={}
    for c in comps_of(eq):
        g=ti.loc[c]
        if g.tkind.iloc[0] not in kinds: continue
        per={}
        for q,r in g.iterrows():
            per.setdefault(r.base,[]).append(to_si(ti,q,r[col]))
        bv={b:gmean(v) for b,v in per.items()}
        if len(bv)<minb: continue
        vals=list(bv.values())
        pv=gmed(vals) if stat=='median' else gmean(vals)
        lv=np.log(vals); sp=float(lv.max()-lv.min())
        for q in c: out[q]=(pv,len(bv),sp)
    return out
