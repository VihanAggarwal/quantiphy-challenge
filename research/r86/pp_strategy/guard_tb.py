import sys,re; sys.path.insert(0,'/home/user/quantiphy-challenge')
import numpy as np, pandas as pd
from qp.data import load_split
from qp.mra import item_scores
R='/home/user/quantiphy-challenge/'
to_m={'m':1.0,'meters':1.0,'meter':1.0,'cm':0.01,'mm':0.001}
# (name, regex, lo, hi, sims_allowed)  world-knowledge ranges fixed a priori
C=[('person height',r'\bheight of the (?:\w+ )?(?:person|man|woman|pedestrian)\b',1.50,2.00,True),
   ('car length',r'\blength of the (?:\w+ )?car\b',3.3,6.0,True),
   ('car width',r'\bwidth of the (?:\w+ )?car\b',1.5,2.3,True),
   ('car height',r'\bheight of the (?:\w+ )?car\b',1.1,2.0,True),
   ('bike wheel',r'diameter of the (?:bicycle|bike) (?:wheel|tire)',0.5,0.75,True),
   ('basketball',r'diameter of the basketball',0.22,0.25,False),
   ('tennis',r'diameter of the tennis ball',0.063,0.07,False),
   ('pingpong',r'diameter of the (?:ping[- ]?pong|table tennis) ball',0.038,0.042,False)]
def guard(df,pred):
    out=pred.copy(); hit=pd.Series('',index=df.index)
    q=df.question.str.lower(); u=df.target_unit.str.lower().str.strip()
    for nm,rx,lo,hi,sims in C:
        msk=q.str.contains(rx,regex=True)&u.isin(to_m.keys())
        if not sims: msk&=~df.video_source.isin(['simulation','segmentation'])
        for i in df.index[msk]:
            f=to_m[u[i]]; v=pred[i]*f
            if np.isfinite(v) and v>0 and not(lo<=v<=hi):
                out[i]=np.clip(v,lo,hi)/f; hit[i]=nm
    return out,hit
# 1) validation (Track B v3 preds)
V=pd.read_csv(R+'research/trackb_v5/out_val_rows.csv').set_index('qid')
g,h=guard(V,V.pred)
hm=h!=''
print('VAL hits',hm.sum(), dict(h[hm].value_counts()))
if hm.sum(): print(pd.DataFrame({'q':V.question[hm].str[:50],'pred':V.pred[hm],'guard':g[hm],'ans':V.answer[hm]}).to_string())
for c in ['S2','D2','S3','D3']:
    mk=V.category==c
    print(c,'val base %.4f guard %.4f'%(item_scores(V.pred[mk],V.answer[mk]).mean(),item_scores(g[mk],V.answer[mk]).mean()))
# 2) test: Track B v3 submission vs Track A combo2 (proxy) and vs facts
t=load_split('test').set_index('qid')
def rd(p):
    d=pd.read_csv(p); d=d.rename(columns={d.columns[0]:'id'}); return pd.to_numeric(d.set_index('id')['parsed_value'],errors='coerce').reindex(t.index)
B=rd(R+'submissions/trackB_v3_catmedian_famrules.csv'); A=rd(R+'submissions/trackA_cand_combo2.csv')
gB,hB=guard(t,B); hm=hB!=''
print('TEST hits',hm.sum(),dict(hB[hm].value_counts()))
N={'S2':553,'D2':1137,'S3':538,'D3':933}
tot=0
for c in N:
    mk=hm&(t.category==c)
    d=(item_scores(gB[mk],A[mk])-item_scores(B[mk],A[mk])).sum()
    print(c,'hits',mk.sum(),'pseudo item gain %.1f'%d,'-> overall %+.4f'%(d/N[c]/4)); tot+=d/N[c]/4
print('total pseudo overall %+.4f'%tot)
F=pd.read_csv(R+'research/trackb_dense/out/fact_labels.csv').set_index('qid')
mk=hm.reindex(F.index).fillna(False)
print('fact rows hit',mk.sum())
# Track A's own rows: how many would the guard change (false-alarm rate proxy)
gA,hA=guard(t,A); print('Track A rows the guard would change',(hA!='').sum(),dict(hA[hA!=''].value_counts()))
