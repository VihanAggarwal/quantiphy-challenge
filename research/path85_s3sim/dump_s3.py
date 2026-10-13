"""Dump S3 non-lab rows: 3 direct runs, old geometry, current answer, stated-fact label if any."""
from common import *  # noqa
r = pd.read_csv(REPLAY)
d = r.pivot_table(index="qid", columns="run", values="direct", aggfunc="first")[RUNS]
g = lmed(r.pivot_table(index="qid", columns="run", values="geo_old", aggfunc="first"))
t = test_df().set_index("qid")
cur = read_sub()
lf, _ = fact_labels(); lv = val_labels()
cat = sys.argv[1] if len(sys.argv) > 1 else "S3"
x = t[(t.category == cat) & t.video_source.isin(["simulation", "segmentation"])]
last = None
for q, row in x.iterrows():
    if row.video_id != last:
        print(f"\n## {row.video_id} | {row.prior.replace(chr(10),' ; ')} | {row.depth_info.replace(chr(10),' ; ')[:250]}")
        last = row.video_id
    runs = d.loc[q].round(3).tolist() if q in d.index else []
    tag = f"FACT {lf[q]:.4g}" if q in lf.index else ""
    tag += f" VAL {lv[q]:.4g}" if q in lv.index else ""
    print(f"  {q} {row.question[:95]:95s} runs {runs} geo {g.get(q, np.nan):.3g} cur {cur[q]:.4g} {tag}")
