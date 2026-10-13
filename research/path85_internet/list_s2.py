import sys; sys.path.insert(0,'.')
import pandas as pd
from qp.data import load_split, load_validation
from qp import postprocess as pp
df = load_split("test")
v = load_validation()
vkeys = {(a, pp.norm_question(b)) for a, b in zip(v.video_id, v.question)}
df["overlap"] = [(a, pp.norm_question(b)) in vkeys for a, b in zip(df.video_id, df.question)]
best = pd.read_csv("submissions/trackA_cand_physb2_on_p21.csv").set_index("id")["parsed_value"]
run = pd.read_csv("runs/test_v1_high_854/test.csv").set_index("id")
df["pred"] = df.qid.map(best)
df["geo"] = df.qid.map(run.geo_value); df["direct"]=df.qid.map(run.direct_value); df["method"]=df.qid.map(run.method)
s = df[(df.video_source.isin(["internet"])) | df.video_id.str.startswith("internet")]
pd.set_option("display.width",250); pd.set_option("display.max_colwidth",110); pd.set_option("display.max_rows",1000)
print(s.groupby("category").size())
print(s.groupby(["category","overlap"]).size())
for vid,g in s[s.category=="S2"].groupby("video_id"):
    print(f"== {vid} fps={g.fps.iloc[0]} type={g.video_type.iloc[0]} src={g.video_source.iloc[0]} | {g.prior.iloc[0]}")
    for _,r in g.iterrows():
        print(f"   {r.qid:5d} {'OV' if r.overlap else '  '} pred={r.pred:.4g} geo={r.geo:.4g} dir={r.direct:.4g} {r.method} | {r.question[:150]}")
