"""Per-member item means on segmented-clip rows (validation labels; test stated-fact rows) and on originals with a
segmented twin. Diagnostic for L6 (routing segmented questions to mask-based geometry)."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from harness import CATS, V3, Data, src_of  # noqa
from qp.mra import item_scores  # noqa
D = Data()
fl = pd.read_csv(HERE.parents[0] / "trackb_dense/out/fact_labels.csv", index_col=0)
fl = fl[fl.index < 100000]
vids = set(D.test.video_id)
def grp(v):
    if v.endswith("_segmented"):
        return "seg"
    return "orig_w_twin" if v + "_segmented" in vids else src_of(v)
rows = []
for split, frame, lab in (("val", D.val, pd.Series(D.val.answer.to_numpy(float), index=D.val.qid)),
                          ("facts", D.test, fl.lab)):
    f = frame.set_index("qid")
    q = lab.index.intersection(f.index)
    g = f.loc[q].video_id.map(grp)
    c = f.loc[q].category
    v3 = D.raw(V3, "test" if split == "facts" else "val").reindex(q)
    P = {m: pd.Series(D.P["test" if split == "facts" else "val"][m].to_numpy(), index=frame.qid).reindex(q) for m in D.P[split if split=="val" else "test"]}
    P["v3"] = v3
    for m, p in P.items():
        it = item_scores(p.to_numpy(float), lab.reindex(q).to_numpy(float))
        for (gg, cc), idx in pd.Series(range(len(q)), index=q).groupby([g.to_numpy(), c.to_numpy()]):
            rows.append(dict(split=split, grp=gg, cat=cc, m=m, n=len(idx), item=np.nanmean(np.nan_to_num(it[idx.to_numpy()]))))
R = pd.DataFrame(rows)
R = R[R.grp.isin(["seg", "orig_w_twin"])]
T = R.pivot_table(index="m", columns=["split", "grp", "cat"], values="item").round(2)
N = R.drop_duplicates(["split", "grp", "cat"]).set_index(["split", "grp", "cat"]).n
pd.set_option("display.width", 250)
print(T.to_string()); print(N.to_string())
