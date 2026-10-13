from build_s3 import *
from eval_famknown import known
seen=set()
for q in known:
    if q not in eq: continue
    grp=sorted(p for p in eq[q] if p in known)
    if len(grp)<2 or tuple(grp) in seen: continue
    seen.add(tuple(grp))
    print([(p,ti.loc[p,'video_id'][-14:],ti.loc[p,'category'],str(ti.loc[p,'tobj'])[:12],ti.loc[p,'tdim'],known[p]) for p in grp])
