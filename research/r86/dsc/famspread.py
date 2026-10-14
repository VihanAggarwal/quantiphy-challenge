"""Cross-camera disagreement of combo3 answers inside the eye-verified extended scene families (TS_ext, built for D3
in path85_d3) for EVERY category. A row is an outlier when its answer is > 1.35x off the median of the OTHER base clips'
answers to the same (object, dimension, kind) question (>= 2 other base clips, which agree within 1.25x)."""
import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/r86/dsc')
from common import *
W='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ext/d3rest/verified/rebuild/work/'
t=pd.read_pickle(W+'TS_ext.pkl')
d=load().set_index('qid')
t['cur']=t.qid.map(d.pred)
t=t[t.video_id.str.startswith('simulation')]
t['key']=t.tkind.astype(str)+'|'+t.tobj.astype(str).str.lower().str.replace(r'\b(the|moving|walking)\b','',regex=True).str.split().str.join(' ')+'|'+t.tdim.astype(str)+'|'+t.ttime.astype(str)
rows=[]
for (f,k),g in t.groupby(['fam','key']):
    if g.base.nunique()<3: continue
    for _,r in g.iterrows():
        oth=g[g.base!=r.base].groupby('base').cur.median()
        if len(oth)<2: continue
        m=np.exp(np.log(oth).median()); spread=oth.max()/oth.min()
        rows.append(dict(qid=r.qid,vid=r.video_id,cat=r.category,key=k,cur=r.cur,others=m,n_oth=len(oth),spread=spread,ratio=r.cur/m))
R=pd.DataFrame(rows)
R.to_csv('/home/user/quantiphy-challenge/research/r86/dsc/famspread.csv',index=False)
out=R[(np.abs(np.log(R.ratio))>np.log(1.35))&(R.spread<1.25)]
print(len(R),'rows with >=2 other clips;',len(out),'outliers')
print(out.cat.value_counts())
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',60)
print(out.sort_values(['cat','vid']).to_string())
