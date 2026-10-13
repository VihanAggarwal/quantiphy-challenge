import sys, os, pickle, re
import pandas as pd, numpy as np
W='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/big/scenegraph/work'
sys.path.insert(0,W); os.chdir(W)
import build as B
ti=B.ti; eq=B.eq; v3=B.v3
pd.set_option('display.width',300); pd.set_option('display.max_colwidth',90)
qs=[int(x) for x in sys.argv[1:]]
for q in qs:
    print('====',q,ti.loc[q,'video_id'],ti.loc[q,'question'].strip()[:90],'v3',v3[q],'KC',round(np.exp(B.KC[ti.loc[q,'video_id']]),3))
    per=B.per_base_values(ti,eq,q,col='v3',include_self=True)
    for b,(rk,val,p) in sorted(per.items()):
        print('   ',b,p,ti.loc[p,'video_id'],'v3=',v3[p],'corr=',round(B.corrected(p,True),4),'direct?',B.is_direct(p),'|',ti.loc[p,'question'].strip()[:80])
    print('   pooled', B.pooled_value(q,True))
    print('   eq members', sorted(eq[q]))
