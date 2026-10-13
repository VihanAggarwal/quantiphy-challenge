import sys, os
sys.dont_write_bytecode=True
exec(open('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/merge/S3/verified/rebuild/build_merge_rebuild.py').read().split("if __name__ == '__main__':")[0])
M=pd.read_csv('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/merge/S3/S3_merged.csv').set_index('id').parsed_value
print('LABFACTS:')
for f in LABFACTS: print('  ', f)
# which S3 lab-size groups have a direct-name stated fact
for k, qs in GROUPS.items():
    g = ti.loc[qs]
    objs = sorted({x.lower().strip() for o in g.tobj for x in str(o).split('|')})
    fv=[(po,si,v) for (po,pd_,si,v) in LABFACTS if dimnorm(pd_)==dimnorm(g.tdim.iloc[0]) and max(name_score(po,o) for o in g.tobj.iloc[0].split('|'))>=0.8]
    if fv: print('GROUP with fact', objs, g.tdim.iloc[0], fv, [ (q, ti.loc[q,'category'], round(M[q],4), round(TL[q],4)) for q in qs if q in S3set])
# TL lab changes not equal to merged
lab=[q for q in S3 if ti.loc[q,'video_source']=='lab' and ne(TL[q],v3[q])]
print('TL lab changes', len(lab))
nm=[q for q in lab if ne(TL[q],M[q])]
print('TL lab not taken', len(nm))
import collections
c=collections.Counter()
for q in nm:
    qq=ti.loc[q,'question']; c[re.sub(r'captured_\d+[ab]?[sx]?','',qq)[:50]]+=1
for k,v in c.most_common(): print('  ',v,k)
# also: lab S3 size rows in TL with value equal to a stated fact
