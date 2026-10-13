"""Build S2-only / D2-only family-pooling variants on probe 5.

Rule P2D (cross-camera pooling of 2D answers about the same object and quantity):
  - equivalence: same scene family (big/scenegraph/families.json), sizes: both simulation clips, same object
    (qp.geometry.name_score >= 0.6 after dropping motion adjectives), same dimension; motion: same scenario
    (families.json 'scenarios') and same time / window.
  - vote unit: camera view (clips whose high-pass edge maps correlate >= 0.6, or identical renders; segmented
    twins join their original). Unit value = geometric mean of its answers in SI units.
  - votes: 2D units (option A) or 2D + 3D units (option B, the 3D values are probe 5's answers, used only as votes).
  - pooled value: >= 3 votes: mean of log votes within 0.15 of the log median; 2 votes: geometric mean when they
    differ by <= cap2 in log, else no change. Every 2D member row takes the pooled value (in its unit).
  - guard: with <= 3 votes that differ by more than smax (0.5 in log, x1.65) the group is left unchanged.
  - groups containing a stated-fact (T) row are left to T.
  - optional D2 T: the 20 D2 rows the scene-graph T rule answers with a value stated by a family clip.
"""
import sys, argparse
from rule import *
from qp.parse import canonical_unit, _UNITS
ap=argparse.ArgumentParser()
ap.add_argument('--votes3d',action='store_true')
ap.add_argument('--tau',type=float,default=0.15)
ap.add_argument('--cap2',type=float,default=0.3)
ap.add_argument('--d2T',action='store_true')
ap.add_argument('--smax',type=float,default=0.5)
ap.add_argument('--kinds',default='size,speed,acceleration,displacement,path_length')
ap.add_argument('--name',required=True)
a=ap.parse_args()
t=pd.read_pickle(W+'/T.pkl'); ti=t.set_index('qid')
new=t.set_index('qid').p5.astype(float).copy()
why={}
# D2 T rows (stated family facts) from the scene-graph T list
Trows={}
cur=None
for line in open(SP+'/big/scene_graph/T_list.txt'):
    if line.startswith('====='): cur=line.split()[1]; continue
    q=int(line.split()[0]); Trows[q]=(cur,float(re.search(r'-> ([\d.eE+-]+)',line).group(1)))
if a.d2T:
    for q,(c,v) in Trows.items():
        if c=='D2' and ti.loc[q,'category']=='D2':
            if not np.isclose(new[q],v): why[q]='T'
            new[q]=v
cats=('S2','D2','S3','D3') if a.votes3d else ('S2','D2')
G=build_groups(t,unit='cam',cats=cats,kinds=tuple(a.kinds.split(',')))
def factor(q):
    tu=ti.loc[q,'target_unit']; u=canonical_unit(str(tu)) if tu else None
    return _UNITS[u][0] if u in _UNITS else 1.0
ng=0
for gr in G:
    qs=[q for mem in gr['members'].values() for q,_ in mem]
    if any(q in Trows for q in qs): continue            # T territory (stated values)
    cat_of={}
    for u,mem in gr['members'].items():
        cs=set(ti.loc[[q for q,_ in mem],'category'])
        cat_of[u]='2D' if cs<={'S2','D2'} else ('3D' if cs<={'S3','D3'} else 'mix')
    u2=[u for u in gr['ul'] if cat_of[u]=='2D']
    if not u2: continue
    votes=[v for u,v in gr['ul'].items() if cat_of[u] in ('2D','3D')]
    if not a.votes3d and len(u2)<2: continue
    if len(votes)<=3 and max(votes)-min(votes)>a.smax: continue   # few votes, wide disagreement: identity/definition in doubt
    pv=pooled_value(votes,a.tau,a.cap2,'trimmed')
    if pv is None: continue
    ng+=1
    for u in u2:
        for q,_ in gr['members'][u]:
            if ti.loc[q,'category'] not in ('S2','D2'): continue
            val=float(np.exp(pv))/factor(q)
            if not np.isclose(val,new[q],rtol=1e-9):
                why[q]=f'P({len(votes)} votes)'
                new[q]=val
assert np.all(np.isfinite(new.values)) and np.all(new.values>0)
p5=pd.read_csv(R+'/submissions/trackA_probe5_families_merged.csv')
out={}
for cat in ('S2','D2'):
    ids=set(t[t.category==cat].qid)
    sub=p5[['id','parsed_value']].copy()
    m=sub.id.isin(ids)
    sub.loc[m,'parsed_value']=sub.loc[m,'id'].map(new).values
    ch=(~np.isclose(sub.parsed_value.values,p5.parsed_value.values,rtol=1e-12))
    f=f'{W}/{a.name}_{cat}.csv'; sub.to_csv(f,index=False)
    chq=sub.id[ch].tolist()
    r=np.array([new[q]/ti.loc[q,'p5'] for q in chq]) if chq else np.array([1.0])
    out[cat]=dict(csv=f,rows_changed=int(ch.sum()),median_ratio=float(np.median(r)),median_abs_log=float(np.median(np.abs(np.log(r)))),
                  by_rule=pd.Series([why.get(q,'?')[:1] for q in chq]).value_counts().to_dict(),
                  by_kind=pd.Series([ti.loc[q,'tkind'] for q in chq]).value_counts().to_dict())
print(a.name,'groups pooled',ng, json.dumps(out,indent=1))
json.dump(dict(args=vars(a),out=out,changes={int(q):dict(old=float(ti.loc[q,'p5']),new=float(new[q]),why=why.get(q)) for q in why}),open(f'{W}/{a.name}.json','w'),indent=1)
