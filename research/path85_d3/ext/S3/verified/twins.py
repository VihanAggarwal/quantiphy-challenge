import sys, os
sys.dont_write_bytecode=True
exec(open('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/merge/S3/verified/rebuild/build_merge_rebuild.py').read().split("if __name__ == '__main__':")[0])
M=pd.read_csv('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/merge/S3/S3_merged.csv').set_index('id').parsed_value
pairs=segtwin_pairs()
print('n pairs', len(pairs))
bad=[(tw,o,M[tw],M[o],v3[tw],v3[o]) for tw,o in pairs.items() if ne(M[tw],M[o])]
for b in bad: print('twin',b[0],'orig',b[1],'M',b[2],b[3],'v3',b[4],b[5], ti.loc[b[0],'question'][:60])
# segmented clips whose question text differs from original but same quantity (normalised loosely)
S=t[t.category=='S3'].copy()
S['twin']=S.video_id.str.replace('_segmented','',regex=False)
def loose(q): 
    q=q.lower(); q=re.sub(r'from the beginning to the end|average|body','',q); return re.sub(r'[^a-z0-9.]','',q)
S['lq']=S.question.map(loose)
orig=S[~S.video_id.str.endswith('_segmented')&(S.video_source!='lab')]
for r in S[S.video_id.str.endswith('_segmented')].itertuples():
    if r.qid in pairs: continue
    o=orig[(orig.twin==r.twin)&(orig.lq==r.lq)]
    if len(o):
        oq=int(o.qid.iloc[0])
        print('loose pair', r.qid, oq, 'M', round(M[r.qid],4), round(M[oq],4), 'v3', v3[r.qid], v3[oq], '|', r.question[:55], '|', o.question.iloc[0][:55], '| same prior/depth', o.prior.iloc[0]==r.prior, o.depth_info.iloc[0]==r.depth_info)
