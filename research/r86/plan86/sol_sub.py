import sys
ROOTP = __import__("pathlib").Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOTP / "research/newmodels"))
sys.path.insert(0, str(ROOTP))
import numpy as np, pandas as pd
from pathlib import Path
import evaluate as E
ROOT = E.ROOT
v = E.load_split("val_hires").set_index("qid")
t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
key_t = {(vid, E.pp.norm_question(q)): i for i, vid, q in zip(t.index, t.video_id, t.question)}
v["tq"] = [key_t.get((vid, E.pp.norm_question(q))) for vid, q in zip(v.video_id, v.question)]
v["cat"] = [t.category.get(i) if i is not None else None for i in v.tq]
v["src"] = [t.srcg.get(i) if i is not None else None for i in v.tq]
gt = v.answer.astype(float); clip = v.video_id.str.replace("_segmented", "", regex=False)
m = v.tq.notna()
c3 = pd.Series([t.combo3.get(i) for i in v.tq], index=v.index, dtype=float)
for p in sys.argv[1:]:
    s = E.col(p).reindex(v.index)
    gm = np.exp((np.log(c3) + np.log(s.fillna(c3))) / 2)
    base = E.sc(c3, gt); new = E.sc(gm, gt); alone = E.sc(s.fillna(c3), gt)
    print("==", Path(p).parent.name)
    for cat in ["S2","D2","S3","D3"]:
        for src in ["sim","internet","lab"]:
            mm = m & (v.cat==cat) & (v.src==src)
            if mm.sum()==0: continue
            d = (new-base)[mm]; da=(alone-base)[mm]
            lo,hi = E.boot(d, clip[mm])
            print(f"{cat} {src:8s} n={int(mm.sum()):3d} clips={clip[mm].nunique():2d} combo3 {base[mm].mean():.3f} model {alone[mm].mean():.3f} gm {new[mm].mean():.3f} d_gm {d.mean():+.3f} [{lo:+.3f},{hi:+.3f}]")
