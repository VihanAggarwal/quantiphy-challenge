from tab import *
from qp.geometry import name_score
STOP={'the','turning','turing','walking','moving','running','flying','falling','rolling','swimming','sliding','driving','a','an'}
def onorm(o):
    o=str(o or '').lower()
    toks=[x for x in re.split(r'[^a-z0-9]+',o) if x and x not in STOP]
    return ' '.join(toks)
def dimnorm(d):
    d=str(d or '').lower().strip()
    d={'body length':'length','side length':'side','side':'side','edge length':'side','diameter':'diameter'}.get(d,d)
    return d
_QD=[('wingspan',r'wing\s*span|wingspan'),('side',r'side length|length of (?:a|each|one) side'),('diameter',r'diameter'),('radius',r'radius'),
     ('thickness',r'thickness'),('depth',r'\bdepth\b'),('height',r'\bheight\b|\btall\b'),('width',r'\bwidth\b|\bwide\b'),('length',r'\blength\b|\blong\b')]
def qdim(q):
    """dimension word of the question text (first by priority), None if none"""
    q=str(q).lower()
    for name,pat in _QD:
        if re.search(pat,q): return name
    return None
def fnum(x):
    try:
        x=float(x); return x if math.isfinite(x) else None
    except: return None
def objs(r): return [onorm(x) for x in str(r.tobj).split('|') if x]
def same_obj(a,b,thr=0.6):
    oa,ob=objs(a),objs(b)
    if len(oa)!=len(ob) or not oa: return 0.0
    if len(oa)==1: return name_score(oa[0],ob[0])
    s1=min(name_score(oa[0],ob[0]),name_score(oa[1],ob[1])); s2=min(name_score(oa[0],ob[1]),name_score(oa[1],ob[0]))
    return max(s1,s2)
def win(x): return tuple(x) if isinstance(x,(list,tuple)) else None
def qmatch(a,b,thr=0.6):
    """same object+quantity (physical)"""
    if a.tkind!=b.tkind: return False
    if a.tkind not in ('size','speed','acceleration','distance','displacement','path_length'): return False
    if same_obj(a,b)<thr: return False
    if a.tkind=='size':
        qa,qb=qdim(getattr(a,'question','')),qdim(getattr(b,'question',''))
        if qa and qb and qa!=qb: return False          # the question texts ask different dimensions
        return dimnorm(a.tdim)==dimnorm(b.tdim)
    ta,tb=fnum(a.ttime),fnum(b.ttime)
    if (ta is None)!=(tb is None): return False
    if ta is not None and abs(ta-tb)>1e-6: return False
    if win(a.twin)!=win(b.twin): return False
    return True
def is_sim(v): return v.startswith('simulation')
def groups(t, motion_rule='scen', cats=('S2','D2','S3','D3')):
    """eq[qid] = set of qids (other bases of same family) asking the same physical quantity"""
    t=t[t.category.isin(cats)]
    eq={}
    for f,g in t[t.fam.notna()].groupby('fam'):
        rows=list(g.itertuples())
        for i,a in enumerate(rows):
            for b in rows[i+1:]:
                if a.base==b.base: continue
                if not qmatch(a,b): continue
                if a.tkind=='size':
                    if not ((is_sim(a.video_id) and is_sim(b.video_id))): continue
                else:
                    if motion_rule=='scen':
                        if not (isinstance(a.scen,str) and a.scen==b.scen): continue
                    elif motion_rule=='none': continue
                eq.setdefault(a.qid,set()).add(b.qid); eq.setdefault(b.qid,set()).add(a.qid)
    return eq
