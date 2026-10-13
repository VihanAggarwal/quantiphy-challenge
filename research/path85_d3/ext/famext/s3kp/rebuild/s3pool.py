"""S3 series pooling with per-kind K for S3 members (test inputs + cached run only)."""
from lofo_kind import *
def member_val(p, excl, s3mode):
    r=ti.loc[p]
    if r.category=='D3': return corr(p,excl,'none','all')          # probe-5 D3 K (sizes+speeds facts)
    if r.category=='S3': return corr(p,excl,s3mode,'all')          # per-kind (or none) for S3 clips
    return v3[p]                                                    # 2D geometry members as is
def pooled(q, excl=frozenset(), s3mode='kind', minb=3, guard='bimodal', gfac=1.6, gshare=1/3, repl=None):
    per=per_base_values(ti,eq,q,include_self=True)
    if len(per)<minb: return None, 'few_bases'
    mv={p:member_val(p,excl,s3mode)*usc(p) for b,(rk,vv,p) in per.items()}
    vals=np.array(list(mv.values()))
    gm=gmed(vals)
    if guard=='bimodal':
        n=len(vals); hi=(vals>gm*gfac).sum(); lo=(vals<gm/gfac).sum()
        if max(hi,lo)>=max(2,gshare*n): return None, 'bimodal'
    if repl:   # keep own answer when it already agrees with the others' consensus within a factor
        oth=[x for p,x in mv.items() if p!=q]
        if oth and abs(np.log(v3[q]*usc(q)/gmed(oth)))<=np.log(repl): return None, 'agrees'
    return gm/usc(q), 'pool'
