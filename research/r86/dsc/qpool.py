"""Same-question pooling inside eye-verified extended families (TS_ext): a STATIC question (no time, size or static
distance) asked with identical normalised text in >= 3 base clips of one family has one Blender label (world AABB /
origin distance of one asset, camera-independent). Candidate: rows > OUT x off the log-median of the OTHER base clips,
whose other answers agree within AGREE, move to that median. Test inputs + our own answers only."""
import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/r86/dsc')
from common import *
OUT=float(sys.argv[1]) if len(sys.argv)>1 else 1.3
AGREE=float(sys.argv[2]) if len(sys.argv)>2 else 1.3
W='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ext/d3rest/verified/rebuild/work/'
t=pd.read_pickle(W+'TS_ext.pkl')
d=load().set_index('qid')
t['cur']=t.qid.map(d.pred)
t=t[t.video_id.str.startswith('simulation')]
t['nq']=t.question.str.lower().str.replace(r'[^a-z0-9.]','',regex=True)
static=~t.question.str.contains(r'speed|veloc|accel|displace|\bat\s*[\d.]+\s*s|t=|time|travel|walked|path',case=False)
t=t[static]
rows=[]
for (f,q),g in t.groupby(['fam','nq']):
    per=g.groupby('base').cur.median()
    if len(per)<3: continue
    for _,r in g.iterrows():
        oth=per.drop(r.base)
        if len(oth)<2 or oth.max()/oth.min()>AGREE: continue
        m=float(np.exp(np.log(oth).mean()))
        if abs(np.log(r.cur/m))>np.log(OUT):
            rows.append(dict(qid=r.qid,vid=r.video_id,cat=r.category,q=r.question[:80],cur=r.cur,new=m,ratio=r.cur/m,others=' '.join(f'{b[-4:]}:{x:.3g}' for b,x in oth.items())))
R=pd.DataFrame(rows)
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',80)
print(R.to_string()); print(R.cat.value_counts().to_dict())
R.to_csv('/home/user/quantiphy-challenge/research/r86/dsc/qpool_cands.csv',index=False)
