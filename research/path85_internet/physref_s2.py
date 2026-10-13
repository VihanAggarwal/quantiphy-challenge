"""S2 internet: does the stated size prior disagree with physical references in the same clip?
k = physical / in-clip answer (current best submission trackA_cand_physb2_on_p21). Test inputs only; no labels.
Physical values are public standards (ISO 7810 card, US bill, Apple specs, USA Pickleball, monitor 24in 16:9)."""
import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd
best = pd.read_csv("submissions/trackA_cand_physb2_on_p21.csv").set_index("id")["parsed_value"]
REF = [  # qid, clip, object, physical value (answer unit), source
    (3032, "internet_0036", "US $1 bill length (mm), prior width 66.3", 155.96, "BEP 6.14 in"),
    (3041, "internet_0038", "Magic Mouse 2 length (cm), prior width 5.71", 11.35, "Apple spec 11.35 x 5.71"),
    (3042, "internet_0038", "MacBook Pro 16in length (cm)", 35.57, "Apple spec"),
    (3043, "internet_0038", "MacBook Pro 16in width (cm)", 24.81, "Apple spec"),
    (3282, "internet_0074", "pickleball court length (m), prior width 6.1", 13.41, "USA Pickleball 44 ft"),
    (3288, "internet_0074", "pickleball net length (m)", 6.71, "22 ft post to post"),
    (2112, "internet_0022", "monitor width (cm), 24in 16:9", 53.13, "24in diagonal"),
    (2121, "internet_0024", "AirPods (3rd gen) case length (mm), prior width 45", 54.4, "Apple spec 54.40 x 46.40"),
    (2122, "internet_0024", "pencil length (cm)", 19.0, "standard unsharpened 19 cm"),
    (3271, "internet_0072", "credit card short side (cm), prior length 8.56", 5.398, "ISO 7810 ID-1"),
    (3051, "internet_0040", "credit card 'length' (cm), prior 'width = 83.98 mm' (read as long side)", 5.398, "ISO 7810 ID-1 (if width=long side)"),
    (3060, "internet_0042", "car width (m), prior white car length 4.572", 1.80, "mid-size sedan 1.78-1.85"),
    (2118, "internet_0023", "deck chair / sun lounger length (m), prior swimmer 1.8", 1.95, "typical 1.9-2.0"),
    (3050, "internet_0039", "lane-rope spacing (m), prior swimmer 1.68", 2.5, "FINA 2.5 m (club pools 2.0-2.5)"),
]
rows = []
for q, clip, obj, phys, src in REF:
    p = float(best[q]); rows.append(dict(qid=q, clip=clip, object=obj, in_clip=round(p, 4), physical=phys,
                                         k=round(phys / p, 3), ln_k=round(np.log(phys / p), 3), source=src))
t = pd.DataFrame(rows)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70)
print(t.to_string(index=False))
print(f"\nn={len(t)}  median |ln k| = {t.ln_k.abs().median():.3f}  |ln k|>0.10: {(t.ln_k.abs()>0.10).sum()}  "
      f"|ln k|>0.05: {(t.ln_k.abs()>0.05).sum()}  mean ln k = {t.ln_k.mean():+.3f}")
t.to_csv("research/path85_internet/out/physref_s2.csv", index=False)
