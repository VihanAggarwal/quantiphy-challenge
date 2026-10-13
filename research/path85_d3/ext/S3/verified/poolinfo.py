import sys, os
sys.dont_write_bytecode=True
sys.argv=['x']
exec(open('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/merge/S3/verified/rebuild/build_merge_rebuild.py').read().split("if __name__ == '__main__':")[0])
log=[]
P=lab_pool(P4S3, log)
seen=set()
for q,(pv,label,inf) in sorted(P.items()):
    key=(label, tuple(sorted(inf['others'].items())))
    print(q, ti.loc[q,'video_id'], label, 'own=%.4g'%P4S3[q], 'pooled=%.4g'%pv, inf['n_events'], inf['others'])
for k, qs in GROUPS.items():
    g=ti.loc[qs]
    objs = sorted({x.lower().strip() for o in g.tobj for x in str(o).split('|')})
    if any(q in S3set for q in qs): print('GROUP', objs, g.tdim.iloc[0], sorted(set(g.video_id)))
