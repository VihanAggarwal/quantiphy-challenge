import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
exec(open(Path(__file__).parent / "eval_pl.py").read().split("# v3 + rules")[0])
C = pd.read_pickle(Path(__file__).parent / "cache.pkl")
v3post = C["v3post"]
pl = rd(ROOT / "submissions/trackA_cand_combo2.csv")
tq = D.test[~D.dup].set_index("qid")
for cats in (["S2"], ["S2", "D2"], ["S2", "D2", "D3"]):
    cs = {k: v for k, v in CS.items() if k.split("|")[0] in cats}
    fb = {c: (FB[c] if c in cats else V3[c]) for c in CATS}
    rt, rv = raw_routed("test", cs, fb), raw_routed("val", cs, fb)
    post, _ = D.rules(combined_from_raw(rt, rv))
    b = D.boot(v3post, post)
    a2, b2 = v3post.reindex(tq.index), post.reindex(tq.index)
    ch = ~np.isclose(a2, b2, rtol=1e-6)
    print(cats, fmt(D.score(post)), "| boot", fmt(b), "| test rows changed", tq.category[ch].value_counts().to_dict())
