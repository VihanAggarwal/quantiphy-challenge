from eq import *
t=pd.read_pickle(W+'/T.pkl')
# base answers without stated-fact transfer: S2 -> p4, D2 -> p5, 3D -> v3
t['base_ans']=np.where(t.category=='S2',t.p4,np.where(t.category=='D2',t.p5,t.v3))
ti=t.set_index('qid')
from qp.claude_annotate import prior_si
def facts(t):
    P=t.assign(_pw=t.pwin.astype(str)).drop_duplicates(['video_id','prior'])
    out=[]
    for r in P.itertuples():
        lines=[l for l in re.split(r'\n|;',str(r.prior)) if l.strip()]
        if len(lines)!=1: continue
        if re.search(r'gravit|=\s*9\.8',r.prior,re.I): continue
        si=prior_si(lines[0])
        if not si: continue
        out.append(dict(video_id=r.video_id,base=r.base,fam=r.fam,scen=r.scen,category=r.category,prior=r.prior,tkind=r.pkind,tobj=r.pobj,tdim=r.pdim,ttime=r.ptime,twin=r.pwin,V=si[0]))
    return pd.DataFrame(out)
def gmed(v):
    v=[x for x in v if x and x>0 and np.isfinite(x)]
    return float(np.exp(np.median(np.log(v)))) if v else np.nan
def si_of(q):
    # convert base answer to SI using target unit
    from qp.parse import canonical_unit,_UNITS
    u=canonical_unit(str(ti.loc[q,'target_unit'] or '')) if ti.loc[q,'target_unit'] else None
    f=_UNITS[u][0] if u in _UNITS else 1.0
    return ti.loc[q,'base_ans']*f
if __name__=='__main__':
    F=facts(t[t.fam.notna()])
    print('facts',len(F)); print(F.groupby(['category','tkind']).size())
    rows=[]
    for f in F.itertuples():
        g=t[(t.fam==f.fam)&(t.base!=f.base)]
        m=[]
        for r in g.itertuples():
            if not qmatch(f,r): continue
            if f.tkind=='size':
                if not (is_sim(f.video_id) and is_sim(r.video_id)): continue
            else:
                if not (isinstance(f.scen,str) and f.scen==r.scen): continue
            m.append(r)
        if not m: continue
        # group members by base (twin = same base -> one vote: prefer original)
        per={}
        for r in m:
            rank=0 if r.video_id==r.base else 1
            if r.base not in per or rank<per[r.base][0]: per[r.base]=(rank,r.qid)
        for cats in [('S2','D2'),('S2','D2','S3','D3')]:
            mem=[q for _,q in per.values() if ti.loc[q,'category'] in cats]
            if not mem: continue
            pooled=gmed([si_of(q) for q in mem])
            for r in m:
                if r.category not in ('S2','D2'): continue
                rows.append(dict(fact=f.prior,fvid=f.video_id,fcat=f.category,kind=f.tkind,qid=r.qid,qcat=r.category,cats=len(cats),nb=len(mem),V=f.V,a=si_of(r.qid),pooled=pooled,
                                 raw=mra1(si_of(r.qid),f.V),pool=mra1(pooled,f.V)))
    D=pd.DataFrame(rows)
    D.to_pickle(W+'/lofo.pkl')
    for c in (2,4):
        d=D[D.cats==c]
        print('pool members cats', c)
        print(d.groupby(['qcat','kind']).agg(n=('qid','size'),facts=('fact','nunique'),raw=('raw','mean'),pool=('pool','mean')).round(3))
        d2=d[d.nb>=2]
        print(' with >=2 bases'); print(d2.groupby(['qcat','kind']).agg(n=('qid','size'),facts=('fact','nunique'),raw=('raw','mean'),pool=('pool','mean')).round(3))
