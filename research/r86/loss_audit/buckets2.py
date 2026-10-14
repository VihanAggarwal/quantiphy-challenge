"""Bucket loss map v2 (analysis only). Subset means: leaderboard-decoded (diagE/F on p21) + category deltas since p21
(combo2 scored, combo3 = expected from the U1-U4 reads), allocated to the subsets whose rows changed.
Within a subset, each bucket gets an a-priori item mean from labelled evidence (validation rows scored with combo3;
stated-fact rows scored with the raw answer; Table-6 / stated-prior evidence for lab sizes); fact rows (final =
stated value) are set to .97; then one additive shift per subset makes the bucket means reproduce the decoded mean.
Output: buckets2.csv + printed table."""
import numpy as np, pandas as pd
from pathlib import Path
OUT = Path(__file__).parent
t = pd.read_pickle(OUT / "master.pkl")
NC = {"S2": 553, "D2": 1137, "S3": 538, "D3": 933}
dec = {"S2:sim+seg": .828, "S2:internet": .796, "D2:sim-static": .851, "D2:rest": .857,
       "S3:sim+seg": .742, "S3:lab": .782, "D3:lab-static": .799, "D3:rest": .805}
dcat = {"S2:sim+seg": .015, "S2:internet": .002, "D2:sim-static": .002, "D2:rest": .008,
        "S3:sim+seg": 0, "S3:lab": .004, "D3:lab-static": .001, "D3:rest": .010}
s = t[t.scored].copy()
ns = s.groupby("subset").size()
m3 = {k: dec[k] + dcat[k] * NC[k[:2]] / ns[k] for k in dec}

def bucket(r):
    c, src, kg = r.category, r.srcg, r.kg
    if c == "S2":
        if src == "sim": return f"S2 sim {kg}"
        return "S2 internet " + ("motion" if kg in ("speed", "accel") else kg)
    if c == "D2":
        if r.subset == "D2:sim-static": return f"D2 sim-static {kg}"
        if src == "internet": return "D2 internet (all)"
        if src == "lab": return "D2 lab (all)"
        return f"D2 sim motion {kg}" if kg in ("speed", "accel") else "D2 sim motion other"
    if c == "S3":
        if src == "sim": return f"S3 sim {kg}"
        return f"S3 lab {kg}"
    if c == "D3":
        if r.subset == "D3:lab-static": return f"D3 lab-static {kg}"
        if src == "lab": return "D3 lab motion"
        if kg == "size": return f"D3 sim size (prior {r.pk})"
        return f"D3 sim {kg}"
s["bucket"] = s.apply(bucket, axis=1)
# a-priori item means (non-fact rows), with the evidence they come from
PRIOR = {
 "S2 sim size": (.86, "val S2 .50 (2, one label oddity), val D2 sim .90 (9), facts D2 sim 1.00 (16)"),
 "S2 sim speed": (.87, "val .90 (6), facts raw .78 (6, top-down 0041)"),
 "S2 sim accel": (.68, "val .45 (6, 0171 astronaut), Blender d|v|/dt labels"),
 "S2 sim distance": (.85, "no labels"),
 "S2 internet size": (.86, "val .95 (4)"), "S2 internet motion": (.80, "val speed .88 (5), accel .30 (1)"),
 "S2 internet distance": (.86, "val 1.0 (2)"),
 "D2 sim-static size": (.86, "val .90 (9), facts 1.00 (16)"), "D2 sim-static distance": (.84, "no labels"),
 "D2 internet (all)": (.88, "val .92 (17)"), "D2 lab (all)": (.80, "no labels"),
 "D2 sim motion speed": (.88, "facts .95 (2)"), "D2 sim motion accel": (.85, "facts 1.0 (2)"),
 "D2 sim motion other": (.86, "no labels"),
 "S3 sim size": (.74, "val .745 (11), facts raw .83 (8)"), "S3 sim speed": (.80, "val .97 (7), facts raw .85 (24)"),
 "S3 sim accel": (.72, "val .93 (4), facts raw .57 (3)"), "S3 sim distance": (.74, "val 1.0 (1)"),
 "S3 lab size": (.93, "val .98 (5); Table-6 read implies ~.95 on T6 props; stated ball sizes 1.056x"),
 "S3 lab speed": (.74, "val .79 (8), under-read x.64-.76 on 0034as/0061/0027s"),
 "S3 lab distance": (.76, "val .97 (3); path/displacement rows"), "S3 lab accel": (.60, "val .40 (1)"),
 "D3 lab-static size": (.90, "val .88 (10, incl. desk 857.9 oddity), labfacts raw .90 (15)"),
 "D3 lab-static distance": (.70, "val .50 (3: ball-person .198 oddity, 0061 x.75, displacement x.82)"),
 "D3 lab motion": (.74, "val 0061 speeds .64 (4) + 0013 .7; emulator x1.00 on 107/150"),
 "D3 sim size (prior accel)": (.86, "val D3 sim .835 (17); facts raw .965 (26)"),
 "D3 sim size (prior speed)": (.70, "facts raw .63 (28; eagle/boat/person families, K-corrected in family)"),
 "D3 sim size (prior size)": (.80, "n/a"),
 "D3 sim speed": (.80, "facts raw .84 (26)"), "D3 sim accel": (.78, "facts raw .93 (4)"),
 "D3 sim distance": (.76, "val .50 (1)"),
}
s["isfact"] = s.prov == "fact"
FACT = .97
rows = []
for sub, g in s.groupby("subset"):
    nf = g[~g.isfact]
    pri = nf.bucket.map(lambda b: PRIOR[b][0])
    shift = (m3[sub] * len(g) - FACT * g.isfact.sum()) / len(nf) - pri.mean()
    for b, h in g.groupby("bucket"):
        hn = h[~h.isfact]
        p = PRIOR[b][0]
        est_nf = min(.99, max(.2, p + shift))
        est = (est_nf * len(hn) + FACT * h.isfact.sum()) / len(h)
        w = 1 / (4 * NC[sub[:2]])
        rows.append(dict(subset=sub, bucket=b, n=len(h), fact=int(h.isfact.sum()), est=est, est_nonfact=est_nf,
                         shift=shift, loss_pts=len(h) * (1 - est) * w,
                         gain_per_05=len(hn) * .05 * w, gain_cut30=len(hn) * (1 - est_nf) * .30 * w,
                         dgd40=int((hn.dgd > .4).sum()), evidence=PRIOR[b][1]))
B = pd.DataFrame(rows).sort_values("loss_pts", ascending=False)
B.to_csv(OUT / "buckets2.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
print({k: round(v, 3) for k, v in m3.items()})
print(B.groupby("subset")["shift"].first().round(3).to_dict())
print(B.drop(columns=["evidence", "shift"]).round(4).to_string(index=False))
print("total loss %.4f  total 30%% cut %.4f" % (B.loss_pts.sum(), B.gain_cut30.sum()))
