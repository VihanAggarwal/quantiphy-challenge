import sys, pandas as pd, numpy as np
sys.path.insert(0,'/home/user/quantiphy-challenge')
from qp.data import load_split
R='/home/user/quantiphy-challenge'
t=load_split('test')[['qid','category','video_id','question']]
cat=dict(zip(t.qid,t.category))
p5=pd.read_csv(R+'/submissions/trackA_probe5_families_merged.csv')
tmpl=None
import glob
print('p5 rows',len(p5), 'cols',list(p5.columns))
for f in sys.argv[1:]:
    s=pd.read_csv(f)
    ok=[]
    ok.append(('cols',list(s.columns)==['id','parsed_value']))
    ok.append(('n3289',len(s)==3289))
    ok.append(('ids==p5 order',(s.id.values==p5.id.values).all()))
    ok.append(('unique',s.id.is_unique))
    ok.append(('ids in test',set(s.id)==set(t.qid)))
    v=s.parsed_value.astype(float).values
    ok.append(('finite pos',bool(np.all(np.isfinite(v))&np.all(v>0))))
    ch=~np.isclose(v,p5.parsed_value.values,rtol=1e-12,atol=0)
    cats=pd.Series([cat[i] for i in s.id[ch]]).value_counts().to_dict()
    r=v[ch]/p5.parsed_value.values[ch]
    print(f.split('/')[-1], ok, 'changed',int(ch.sum()), cats, 'median ratio %.4f'%np.median(r), 'max |log| %.3f'%np.abs(np.log(r)).max(), 'n |log|>0.2:',int((np.abs(np.log(r))>0.2).sum()))
