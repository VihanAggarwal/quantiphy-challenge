import sys
ROOTP = __import__("pathlib").Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOTP / "research/newmodels")); sys.path.insert(0, str(ROOTP))
import numpy as np, pandas as pd
import evaluate as E
ROOT=E.ROOT
v = E.load_split("val_hires").set_index("qid")
t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
key_t = {(vid, E.pp.norm_question(q)): i for i, vid, q in zip(t.index, t.video_id, t.question)}
v["tq"] = [key_t.get((vid, E.pp.norm_question(q))) for vid, q in zip(v.video_id, v.question)]
v["cat"] = [t.category.get(i) if i is not None else None for i in v.tq]
v["src"] = [t.srcg.get(i) if i is not None else None for i in v.tq]
gt = v.answer.astype(float); clip = v.video_id.str.replace("_segmented", "", regex=False)
m = v.tq.notna()
c3 = pd.Series([t.combo3.get(i) for i in v.tq], index=v.index, dtype=float)
sol = E.col(ROOT/"runs/val_sol_high/val_hires.csv").reindex(v.index).fillna(c3)
arg = E.col(ROOT/"runs/val_argon_frames/val_hires.csv").reindex(v.index).fillna(c3)
L=lambda *xs: np.exp(np.mean([np.log(x) for x in xs],axis=0))
Md=lambda *xs: np.exp(np.median([np.log(x) for x in xs],axis=0))
cands={"gm(c3,sol,arg)":pd.Series(L(c3,sol,arg),index=v.index),"med(c3,sol,arg)":pd.Series(Md(c3,sol,arg),index=v.index),
       "gm(c3,sol)":pd.Series(L(c3,sol),index=v.index),"w.25 sol":pd.Series(np.exp(.75*np.log(c3)+.25*np.log(sol)),index=v.index)}
base=E.sc(c3,gt)
for n,s in cands.items():
    S=E.sc(s,gt); d=(S-base)[m]; lo,hi=E.boot(d,clip[m])
    per={c: round(d[v.cat[m]==c].mean(),3) for c in ["S2","D2","S3","D3"]}
    nonlab = m & (v.src!="lab")
    d2=(S-base)[nonlab]; lo2,hi2=E.boot(d2,clip[nonlab])
    print(f"{n:16s} all {d.mean():+.4f} [{lo:+.4f},{hi:+.4f}] {per} | non-lab n={int(nonlab.sum())} {d2.mean():+.4f} [{lo2:+.4f},{hi2:+.4f}]")
print("--- non-lab per category")
nonlab = m & (v.src!="lab")
for n,s in cands.items():
    S=E.sc(s,gt); d=(S-base)
    out=[]
    for c in ["S2","D2","S3","D3"]:
        mm=nonlab&(v.cat==c)
        lo,hi=E.boot(d[mm],clip[mm])
        out.append(f"{c} n={int(mm.sum())} {d[mm].mean():+.3f}[{lo:+.3f},{hi:+.3f}]")
    print(f"{n:16s}", " ".join(out))
print("clips nonlab", clip[nonlab].nunique())
