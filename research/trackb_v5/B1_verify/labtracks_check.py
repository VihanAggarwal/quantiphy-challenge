import sys, pickle
from pathlib import Path
import numpy as np
sys.path[:0]=['/home/user/quantiphy-challenge','/home/user/quantiphy-challenge/research/trackb_dense']
import labnoise_open as LN
LN.CACHE = Path(sys.argv[1])
new = LN.build_tracks("test", "qwen")
old = pickle.load(open("/tmp/claude-0/trackb_dense_cache/labtracks_test_qwen.pkl","rb"))
print("qids same:", set(new)==set(old), len(new))
bad=0
for q in old:
    a,b=old[q]["cap"],new[q]["cap"]
    if set(a)!=set(b): bad+=1; continue
    for role in a:
        if role.endswith("_err"): continue
        for k in ("t","uv","P","rng"):
            if not np.allclose(a[role][k],b[role][k],equal_nan=True): bad+=1; break
        if a[role]["name"]!=b[role]["name"]: bad+=1
print("records differing:", bad)
