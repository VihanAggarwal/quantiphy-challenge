"""Guard for the scene-graph K rule (per-clip scale correction of Claude's direct sim answers) on SPEED answers:
drop K when (a) the family states a speed for the same object (any clip, name match) and K moves the answer further
from it than v3 is, or (b) the K-corrected speed is below the object's radial speed implied by its own depth_info."""
import sys, os, re, pickle
import numpy as np, pandas as pd
W='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/big/scenegraph/work'
def compute(ti, KC, tkp_why, tkp_vals, v3):
    cwd=os.getcwd(); sys.path.insert(0,W); os.chdir(W)
    try:
        import graph
        from qp.geometry import name_score
        t=pd.read_pickle(W+'/TS.pkl')
        F=graph.facts(t)
    finally:
        os.chdir(cwd)
    rows=[]
    for q,w in tkp_why.items():
        if w!='K' or ti.loc[q,'category']!='D3' or ti.loc[q,'tkind']!='speed': continue
        r=ti.loc[q]
        fam=r.fam
        objs=str(r.tobj).split('|')
        f=F[(F.fam==fam)&(F.pkind=='speed')&(~F.grav)]
        st=[]
        for x in f.itertuples():
            ns=max([name_score(a,b) for a in objs for b in str(x.pobj).split('|')]+[0])
            if ns>=0.6: st.append(x.si)
        # radial speed bound from own depth_info: max |dD/dt| between consecutive timed entries of the object
        rad=np.nan
        di=str(r.depth_info)
        ents={}
        for line in di.split('\n'):
            m=re.match(r'\s*t\s*=\s*([\d.]+)\s*s\s*,\s*distance_([a-z0-9_]+)_camera\s*=\s*([\d.]+)',line,re.I)
            if m: ents.setdefault(m.group(2).lower(),[]).append((float(m.group(1)),float(m.group(3))))
        alias={'person':'human','man':'human','woman':'human','pedestrian':'human'}
        o=objs[0].lower()
        toks=set(alias.get(w,w) for w in re.findall(r'[a-z]+',o))
        for name,pairs in ents.items():
            nt=set(alias.get(w,w) for w in name.split('_'))
            if (toks & nt) and len(pairs)>=2:
                pairs=sorted(pairs)
                v=[abs(pairs[i+1][1]-pairs[i][1])/(pairs[i+1][0]-pairs[i][0]) for i in range(len(pairs)-1) if pairs[i+1][0]>pairs[i][0]]
                if v: rad=float(np.min(v)) if 'at' not in str(r.question) else float(np.min(v))
        kv=tkp_vals[q]; old=v3[q]
        far=[s for s in st if abs(np.log(kv/s))>abs(np.log(old/s))+1e-9]
        drop_a=bool(st) and len(far)==len(st)
        drop_b=bool(np.isfinite(rad) and kv<rad*0.999)
        rows.append(dict(qid=q,vid=r.video_id,obj=objs[0],v3=old,K=kv,stated=st,radial=rad,drop_fact=drop_a,drop_radial=drop_b))
    return pd.DataFrame(rows)
if __name__=='__main__':
    MD='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/merge/D3'
    sg=pickle.load(open(MD+'/sg_why.pkl','rb'))
    v3=pd.read_csv('/home/user/quantiphy-challenge/submissions/trackA_v3_best_per_category.csv'); v3=dict(zip(v3.id,v3.parsed_value))
    new,why=sg['TKP']
    pd.set_option('display.width',250)
    print(compute(sg['ti'],sg['KC'],why,new,v3).round(3).to_string())
