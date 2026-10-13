"""Build S3-only variants on probe 5 (submissions/trackA_probe5_families_merged.csv).
Rules (S3 simulation/segmentation rows answered by Claude's direct estimate; lab rows untouched):
  P   series pooling: a size/speed question takes the geometric median over the family's equivalent questions
      (same object + dimension; for speeds same time and proven motion identity: same scenario or identical timed
      depth entries), one value per base clip, >= 3 bases. Members: D3 direct answers corrected by probe 5's D3 K
      (size+speed facts of their clip); S3 direct answers corrected PER KIND (s3mode='kind': K_size from the clip's
      stated SIZE facts for sizes, K_speed from its SPEED facts for speeds; 'none' = raw); 2D geometry answers as is.
      Guard: skip a group when >= max(2, n/3) members lie > 1.6x on one side of the median (two conventions or
      objects: rock width seen top-down ~22-24 m vs side views 8-10 m).
  KD  per-kind K applied directly to the remaining (unpooled) S3 sim rows of clips with same-kind stated facts.
  DS  D3 fact sharing: an S3 question whose motion-identical (or same-asset size) D3 equivalent carries a stated
      fact in probe 5 takes that value (2x guard as the SIB rule).
  Rows that probe 5 set from stated facts (T / SIB) keep them. Segmented twins that probe 5 filled by twin copy
  copy their original's new value."""
from s3pool import *
import argparse
M3=pd.read_csv(SP+'/merge/S3/decisions.csv').set_index('qid')
M3D=pd.read_csv(SP+'/merge/D3/decisions.csv').set_index('qid')
S3=[q for q in P5.id if ti.loc[q,'category']=='S3']
SIMS3=[q for q in S3 if ti.loc[q,'video_source']!='lab']
def is_fact_row(q):
    if np.isclose(p5[q],v3[q],rtol=1e-9): return False
    src=M3.chosen_source.get(q) if q in M3.index else None
    return src!='P4'          # T / T=SIB / SIB (and verifier's SIB additions, absent from decisions)
def twin_pairs():
    """segmented row -> original row, for rows probe 5 filled by twin copy"""
    out={}
    for q in SIMS3:
        if q not in M3.index or M3.chosen_source.get(q)!='P4': continue
        r=ti.loc[q]
        if not r.video_id.endswith('_segmented'): continue
        nq=lambda s: re.sub(r'\s+',' ',str(s).strip().lower()).rstrip('?. ')
        c=t[(t.video_id==r.base)&(t.question.map(nq)==nq(r.question))&(t.prior==r.prior)&(t.depth_info==r.depth_info)&(t.target_unit==r.target_unit)]
        if len(c)==1 and np.isclose(p5[q],p5[c.qid.iloc[0]],rtol=1e-9): out[q]=int(c.qid.iloc[0])
    return out
TW=twin_pairs()
def build(rule_P=True, s3mode='kind', rule_KD=False, rule_DS=True, kinds=('size','speed'), d3share_pure=False, repl=None):
    new=dict(p5); why={}
    for q in SIMS3:
        r=ti.loc[q]
        if is_fact_row(q) or q in TW: continue
        if str(r.method)!='direct': continue
        val=None
        if d3share_pure:
            m=[p for p in eq[q] if p!=q and ti.loc[p,'category']=='D3' and ti.loc[p,'video_id'].startswith('simulation')]
            if m and r.tkind in kinds: val=gmed([p5[p]*usc(p) for p in m])/usc(q); why[q]='D3share'
        else:
            if rule_DS:
                fv=[p5[p]*usc(p) for p in eq[q] if p!=q and p in M3D.index and M3D.chosen_source.get(p)=='FACT']
                if fv and len(set(np.round(fv,6)))==1:
                    v=fv[0]/usc(q)
                    if 0.5<=v/v3[q]<=2.0: val=v; why[q]='DS'
            if val is None and rule_P and r.tkind in kinds:
                v,w=pooled(q,frozenset(),s3mode,repl=repl)
                if v is not None: val=v; why[q]='P'
            if val is None and rule_KD and r.tkind in ('size','distance','speed'):
                own=set(A[A.qid==q].fact)            # never K-correct a row from its own (rejected) stated fact
                v=corr(q,own,s3mode,'all')
                if not np.isclose(v,v3[q]): val=v; why[q]='KD'
        if val is not None: new[q]=float(val)
    for s,o in TW.items():
        if not np.isclose(new[o],p5[o],rtol=1e-9): new[s]=new[o]; why[s]='twin<'+why.get(o,'?')
    return new, why
def write(new, name):
    df=P5.copy()
    df['parsed_value']=df.id.map(new)
    v=df.parsed_value.values.astype(float)
    assert len(df)==3289 and list(df.id)==list(P5.id) and list(df.columns)==list(P5.columns)
    assert np.isfinite(v).all() and (v>0).all()
    ch=~np.isclose(v,P5.parsed_value.values,rtol=1e-9)
    assert set(ti.loc[df.id[ch],'category'])<={'S3'}, set(ti.loc[df.id[ch],'category'])
    path=f'{OUT}/{name}.csv'; df.to_csv(path,index=False)
    rat=v[ch]/P5.parsed_value.values[ch]
    return path,int(ch.sum()),float(np.median(rat)) if ch.any() else 1.0, list(df.id[ch])
VARIANTS={
 'S3_PK_DS':dict(rule_P=True,s3mode='kind',rule_DS=True),
 'S3_PKrepl115_DS':dict(rule_P=True,s3mode='kind',rule_DS=True,repl=1.15),
 'S3_PKrepl125_DS':dict(rule_P=True,s3mode='kind',rule_DS=True,repl=1.25),
 'S3_P0_DS':dict(rule_P=True,s3mode='none',rule_DS=True),
 'S3_PKsize_DS':dict(rule_P=True,s3mode='kind',rule_DS=True,kinds=('size',)),
 'S3_DS':dict(rule_P=False,rule_DS=True),
 'S3_D3share':dict(d3share_pure=True),
}
if __name__=='__main__':
    pd.set_option('display.width',260); pd.set_option('display.max_rows',300); pd.set_option('display.max_colwidth',40)
    res={}
    allch={}
    for name,cfg in VARIANTS.items():
        new,why=build(**cfg)
        path,n,med,ids=write(new,name)
        res[name]=dict(csv=path,changed=n,median_ratio=round(med,4),by_rule=pd.Series([why.get(q,'?') for q in ids]).value_counts().to_dict() if ids else {})
        allch[name]={q:new[q] for q in ids}
        print(name,res[name])
    pickle.dump((res,allch),open(OUT+'/build_res.pkl','wb'))
    main='S3_PK_DS'
    rows=[]
    for q,v in allch[main].items():
        r=ti.loc[q]
        rows.append(dict(qid=q,vid=r.video_id.replace('simulation_',''),kind=r.tkind,obj=str(r.tobj)[:22],dim=r.tdim,t=r.ttime,p5=p5[q],
                         **{k:allch[k].get(q,p5[q]) for k in VARIANTS}))
    print(pd.DataFrame(rows).round(3).to_string())
