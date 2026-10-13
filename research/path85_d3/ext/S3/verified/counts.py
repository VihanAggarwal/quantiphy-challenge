import pandas as pd, numpy as np
R='/home/user/quantiphy-challenge'; SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
D=pd.read_pickle(SP+'/merge/S3/decisions_raw.pkl').set_index('qid')
rd=lambda f: pd.read_csv(f).set_index('id').parsed_value
v3=rd(R+'/submissions/trackA_v3_best_per_category.csv'); P4=rd(SP+'/hyp/final/S3_split_full_depthfix.csv'); TL=rd(SP+'/big/scene_graph/S3_T_LABfix.csv')
SIB=rd(SP+'/big/priors_as_labels/S3_sibling_prior_transfer_noconflict.csv'); M=rd(SP+'/merge/S3/S3_merged.csv')
ne=lambda a,b: ~np.isclose(a,b,rtol=1e-9,atol=0)
S3=D.index
p4c=set(S3[ne(P4[S3],v3[S3])]); tlc=set(S3[ne(TL[S3],v3[S3])]); sbc=set(S3[ne(SIB[S3],v3[S3])]); mc=set(S3[ne(M[S3],v3[S3])])
print('P4 changes',len(p4c),'TL',len(tlc),'SIB',len(sbc),'M',len(mc))
ov=p4c&tlc; print('P4&TL overlap',len(ov),'same value',sum(not ne(P4[q],TL[q]) for q in ov))
src=D.chosen_source
import collections
c=collections.Counter()
for q in ov:
    m=M[q]
    tag = 'alias' if src[q]=='labfact_alias' else ('=P4' if not ne(m,P4[q]) else ('=TL' if not ne(m,TL[q]) else 'other'))
    c[tag]+=1
print(c)
lp=[q for q in S3 if src[q]=='LABpool_on_P4']
print('LABpool rows',len(lp),'P4&TL',sum(q in p4c and q in tlc for q in lp),'TL only',sum(q in tlc and q not in p4c for q in lp),'P4 only',sum(q in p4c and q not in tlc for q in lp),'neither',sum(q not in tlc and q not in p4c for q in lp))
print('M rows taking TL value', sum(q in tlc and not ne(M[q],TL[q]) for q in S3), 'P4 value', sum(q in p4c and not ne(M[q],P4[q]) for q in S3))
print('M changed not in any cand', [q for q in mc if q not in p4c|tlc|sbc])
print('M vs P4 differ', sum(ne(M[S3],P4[S3])))
