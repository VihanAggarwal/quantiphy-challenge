"""Missed scene-family links: simulation clips with nearby ids (scenes are built in consecutive id blocks, paper
App. C.1.3: 81 base scenes -> 312 clips) that share >= 2 distinctive object nouns but are not in one code family.
For each question in such a clip asking the size / speed of an object that the neighbour STATES as a prior, compare
our current answer with the stated value. Test inputs only."""
import sys, pickle, re, itertools
sys.path.insert(0,'/home/user/quantiphy-challenge'); sys.path.insert(0,'/home/user/quantiphy-challenge/research/r86/dsc')
from common import *
from qp import postprocess as PP
from qp.geometry import name_score
from qp.open.qwen_vl import parse_question_text
F=pickle.load(open(f'{ROOT}/research/r86/dsc/fams.pkl','rb'))
d=load(); d['fam']=d.video_id.map(F['fam']); d['base']=d.video_id.map(PP.base_id)
df=PP._questions(d.assign(category=d.cg))
facts=PP._parse_facts(df)
STOP=set('the a an of in at to from and or with on between its it is what meters m s cm second seconds speed velocity length width height diameter distance average acceleration body total size time when how wide from beginning end moving walking left right big small first second two one this that which by for while along above below over under during horizontal vertical maximum minimum initial final side front back'.split())
def nouns(txt):
    return {w for w in re.findall(r'[a-z]+', str(txt).lower()) if w not in STOP and len(w)>2}
sim=d[d.video_id.str.startswith('simulation')]
bn={}
for b,g in sim.groupby('base'):
    t=' '.join(g.question)+' '+' '.join(g.prior.unique())+' '+' '.join(re.findall(r'distance_([a-z_ ]+?)_camera',' '.join(g.depth_info.fillna(''))))
    bn[b]=nouns(t.replace('_',' '))
num=lambda b:int(re.search(r'_(\d+)',b).group(1))
fam=dict(zip(d.base,d.fam))
pairs=[]
bases=sorted(bn)
for a,b in itertools.combinations(bases,2):
    if abs(num(a)-num(b))>12 or fam[a]==fam[b]: continue
    sh=bn[a]&bn[b]
    if len(sh)>=2: pairs.append((a,b,sh))
print('candidate cross-family neighbour pairs:',len(pairs))
fb={}
for f in facts: fb.setdefault(PP.base_id(f.video_id),[]).append(f)
rows=[]
for a,b,sh in pairs:
    for x,y in ((a,b),(b,a)):
        for f in fb.get(y,[]):
            g=d[(d.base==x)]
            for _,r in g.iterrows():
                t=parse_question_text(r.question)
                if t['kind']!=f.kind or not t['objects']: continue
                if f.kind=='size' and PP._DIM_SYN.get(t['dimension'],t['dimension'])!=f.dimension: continue
                if f.kind!='size' and (f.timed): continue
                s=max(name_score(o,f.obj) for o in t['objects'])
                if s<0.6: continue
                rows.append(dict(qid=r.qid,vid=r.video_id,cg=r.cg,q=r.question[:80],src=y,fact=f.line[:50],val=f.si,pred=r.pred,ratio=r.pred/f.si,shared=','.join(sorted(sh))[:60]))
R=pd.DataFrame(rows).drop_duplicates(['qid','src'])
R.to_csv(f'{ROOT}/research/r86/dsc/missed_links.csv',index=False)
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',80)
print(R.sort_values('vid').to_string())
