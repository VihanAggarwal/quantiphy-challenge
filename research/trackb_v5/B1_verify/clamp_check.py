import sys, re
from pathlib import Path
import numpy as np, pandas as pd
sys.argv=["x"]; sys.path.insert(0, str(Path(__file__).parent))
import indep_b1 as I
tq=I.tq
raw, post, fin, stated, info = I.build(True, True, True, True, True, False)
_,_,finc,_,infoc = I.build(True, True, True, True, True, True)
hits=infoc["clamp"]
d=pd.DataFrame({"q":[tq.question[q][:60] for q in hits],"cat":[tq.category[q] for q in hits],"pre":[fin[q] for q in hits],"post":[finc[q] for q in hits],"cls":list(hits.values())},index=list(hits))
print("clamp rows",len(d),d.cls.value_counts().to_dict(),"down",int((d.post<d.pre).sum()),"up",int((d.post>d.pre).sum()), d.groupby('cat').size().to_dict())
# skips
q=tq.question.str.lower(); p=tq.prior.astype(str).str.lower()
for nm,rx,lo,hi in I.CLAMP:
    m=q.str.contains(rx,regex=True)
    toy=m&(q.str.contains("toy")|p.str.contains("toy"))
    st=m&tq.index.isin(list(stated))
    print(nm,"regex rows",int(m.sum()),"toy-skip rows",int(toy.sum()),"stated-skip rows",int(st.sum()),
          "would-clamp among stated", int(sum(1 for i in tq.index[st] if not lo<=fin[i]*I.TOM.get(str(tq.target_unit[i]).lower().strip(),np.nan)<=hi)))
# S2 car-width rows out of range because of routing: v3-sets raw (no routing) in range but routed out of range
r0,p0,f0,_,_=I.build(True, False, True, True, True, False)
s2=[i for i in hits if tq.category[i]=="S2"]
print("S2 clamp rows",len(s2),"of which in range without routing:",sum(1 for i in s2 if 1.5<=f0[i]<=2.3 or hits[i]!='car width'))
# stated priors: person heights / car widths mentioned in test priors
pri=tq.prior.astype(str)
ph=pri.str.extractall(r"(?i)(?:person|man|woman|pedestrian)[^.]*?(?:height|tall)[^.]*?([0-9]+\.?[0-9]*)\s*(m|cm)\b")
print("prior person-height mentions (sample):", ph.head(10).values.tolist())
V3=pd.read_csv(I.ROOT/"submissions/trackB_v3_catmedian_famrules.csv").set_index("id").parsed_value
d["v3"]=[V3[i] for i in d.index]
print("vs v3: down",int((d.post<d.v3).sum()),"up",int((d.post>d.v3).sum()),"equal",int(np.isclose(d.post,d.v3).sum()))
print("vs pre-clamp: down",int((d.post<d.pre).sum()),"up",int((d.post>d.pre).sum()))
print(d[d.post>d.pre].to_string())
