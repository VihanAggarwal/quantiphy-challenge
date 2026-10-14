"""Error analysis of the current Track B (v3 sets + preset trackb) on validation."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import Data, V3, VAL_OFFSET, src_of, CATS  # noqa

D = Data()
pred = D.combined(V3)
post, log = D.rules(pred)
print("v3 raw", D.score(pred), "\n+rules", D.score(post))
it = D.items(post)
val = D.val.copy()
val["q"] = val.qid + VAL_OFFSET
val["pred"] = post.reindex(val.q).to_numpy()
val["item"] = it.reindex(val.q).to_numpy()
val["lerr"] = np.log(val.pred / val.answer)
val["src"] = val.video_id.map(src_of)
for m in D.P["val"]:
    val["m_" + m] = D.P["val"][m].to_numpy()
g = val.groupby(["category", "src", "tk"]).agg(n=("item", "size"), item=("item", "mean"),
                                                 medlerr=("lerr", "median"), gross=("lerr", lambda s: (s.abs() > np.log(2)).mean()))
print(g.round(3).to_string())
# per-category lost points by subset
for c in CATS:
    x = val[val.category == c]
    print(c, "lost by (src,tk):", ((1 - x.item).groupby([x.src, x.tk]).sum() / len(x)).round(3).to_dict())
# oracle best member per row
ms = [c for c in val.columns if c.startswith("m_")]
from qp.mra import item_scores
I = pd.DataFrame({m: item_scores(val[m].to_numpy(float), val.answer.to_numpy(float)) for m in ms}).fillna(0)
I.index = val.index
print("member item means per category:")
print(pd.concat([I, val.category], axis=1).groupby("category").mean().round(3).T.to_string())
val.to_csv(Path(__file__).resolve().parent / "out_val_rows.csv", index=False)
