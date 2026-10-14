import sys; sys.path.insert(0,'/home/user/quantiphy-challenge')
import numpy as np, pandas as pd
from qp.mra import item_scores
m=pd.read_pickle('/home/user/quantiphy-challenge/research/r86/loss_audit/master.pkl')
d=pd.read_csv('/home/user/quantiphy-challenge/research/simfov/out/replay.csv')
d=d[d.run=='test_v1_high_854'].set_index('qid')
s=m[(m.category.isin(['S3','D3']))&(m.srcg=='sim')].copy()
s['geo']=d.geo_old.reindex(s.index); s['sens']=d.sens_old.reindex(s.index); s['gflags']=d.flags_old.reindex(s.index)
s['lr']=np.log(s.geo/s.dmed)
good=s.lr.notna()&np.isfinite(s.lr)&(s.sens.abs()<1.5)&s.gflags.isna()
s['base_vid']=s.video_id.str.replace('_segmented','',regex=False)
print('rows with usable geo',good.sum(),'of',len(s))
res=[]
for alpha in [0.25,0.5,1.0]:
    for lab in ['fact','val']:
        out=[]
        for i,r in s[s[lab].notna()].iterrows():
            oth=s[(s.base_vid==r.base_vid)&good&(s.index!=i)]
            if len(oth)<3: continue
            K=np.median(oth.lr)
            new=r.dmed*np.exp(alpha*K)
            out.append((item_scores([new],[r[lab]])[0]-item_scores([r.dmed],[r[lab]])[0],K))
        o=np.array(out)
        if len(o): print('alpha',alpha,lab,'n',len(o),'mean item change %+.4f'%o[:,0].mean(),'median|K| %.3f'%np.median(np.abs(o[:,1])))
