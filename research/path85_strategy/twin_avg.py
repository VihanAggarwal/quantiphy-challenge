"""Twin averaging: a segmented twin and its original ask the same question about pixel-aligned videos, so their two raw
answers are two estimates of one label. Base copies the original's answer into the twin. Check gm(orig, twin) vs the
original alone on (a) stated facts (label-free) and (b) validation overlap (eval only); clustered by original video."""
from common import *
import qp.postprocess as pp
t = pd.read_pickle(OUT / "table.pkl")
f = pd.read_csv(OUT / "facts_log.csv").drop_duplicates("qid").set_index("qid")
t["fact"] = f.new.reindex(t.index)
L = np.log(t[["d1", "d2", "d3"]].where(t[["d1", "d2", "d3"]] > 0))
t["med3"] = np.exp(L.median(axis=1))
# raw answer that the pipeline would use for this row (3D sim: med3 of direct runs; else run answer)
t["rawans"] = np.where((t.srcg == "sim") & t.category.str.endswith("3") & t.med3.notna(), t.med3, t.r_parsed_value)
key = {(v, pp.norm_question(q)): i for i, v, q in zip(t.index, t.video_id, t.question)}
seg = t[t.src == "seg"].copy()
seg["oq"] = [key.get((pp.twin_original(v), pp.norm_question(q))) for v, q in zip(seg.video_id, seg.question)]
seg = seg[seg.oq.notna()]; seg["oq"] = seg.oq.astype(int)
P = pd.DataFrame({"sq": seg.index, "oq": seg.oq.values, "cat": seg.category.values, "dim": seg.video_id.str[-1].values})
P["vid"] = t.video_id.reindex(P.oq).values
P["o"] = t.rawans.reindex(P.oq).values; P["s"] = t.rawans.reindex(P.sq).values
P["gm"] = np.sqrt(P.o * P.s)
P["lab_f"] = t.fact.reindex(P.oq).values; P["lab_f2"] = t.fact.reindex(P.sq).values
P["lab_v"] = t.val.reindex(P.oq).values; P["lab_v2"] = t.val.reindex(P.sq).values
P["lab_f"] = P.lab_f.fillna(P.lab_f2); P["lab_v"] = P.lab_v.fillna(P.lab_v2)
P["dim"] = P.cat.str[1]
print("pairs", len(P), "|log(s/o)| median by cat:", P.assign(d=np.abs(np.log(P.s / P.o))).groupby("cat").d.median().round(3).to_dict())
for lab in ("lab_f", "lab_v"):
    x = P[P[lab].notna() & (P.o > 0) & (P.s > 0)].copy()
    for c in ("o", "s", "gm"):
        x["sc_" + c] = item_scores(x[c], x[lab])
    for grp, g in list(x.groupby("dim")) + [("all", x)]:
        m, lo, hi = clustered_boot(g.sc_gm - g.sc_o, g.vid)
        print(f"{lab} {grp}D n={len(g)} vids={g.vid.nunique()} orig={g.sc_o.mean():.3f} twin={g.sc_s.mean():.3f} gm={g.sc_gm.mean():.3f} gm-orig={m:+.3f} [{lo:+.3f},{hi:+.3f}]")
P.to_pickle(OUT / "twin_pairs.pkl")
