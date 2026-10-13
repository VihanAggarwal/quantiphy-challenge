from build_s3 import *
from rules import obj_depth_identical
for vs in [['simulation_0299','simulation_0300','simulation_0301','simulation_0310','simulation_0311'],['simulation_0039','simulation_0040','simulation_0025','simulation_0031','simulation_0034']]:
    for v in vs:
        g=t[t.video_id==v]
        print('---',v,'scen=',g.scen.iloc[0],'fam=',g.fam.iloc[0],'base=',g.base.iloc[0])
        print('  prior:',g.prior.iloc[0]); print('  depth:',repr(g.depth_info.iloc[0])[:900])
        for r in g.itertuples(): print('   Q',r.qid,r.category,r.question[:90],'| v3=',round(v3[r.qid],3),'p5=',round(p5[r.qid],3))
