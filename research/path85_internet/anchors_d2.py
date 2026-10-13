"""D2 internet self-filmed gravity clips: physical anchors (regulation sizes) read on the g-derived in-clip scale
of the current best submission. Shared bias would justify a per-clip / per-series rescale; none is found."""
import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd
best = pd.read_csv("submissions/trackA_cand_physb2_on_p21.csv").set_index("id")["parsed_value"]
A = [(3102, "internet_0048", "basketball diameter cm", 24.3), (3180, "internet_0059", "basketball diameter cm", 24.3),
     (3220, "internet_0064", "basketball diameter cm", 24.3), (3163, "internet_0057", "rim height m", 3.05),
     (3172, "internet_0058", "rim height m", 3.05), (3074, "internet_0044", "ping-pong ball cm", 4.0)]
t = pd.DataFrame([dict(qid=q, clip=c, anchor=a, read=round(float(best[q]), 3), physical=p,
                       ln_k=round(np.log(p / best[q]), 3)) for q, c, a, p in A])
print(t.to_string(index=False))
print(f"mean ln k {t.ln_k.mean():+.3f}  sd {t.ln_k.std(ddof=1):.3f}  n={len(t)}")
t.to_csv("research/path85_internet/out/anchors_d2.csv", index=False)
