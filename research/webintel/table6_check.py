"""Read-only check: lab prop-size questions vs the paper's Table 6 (measured prop dimensions).
Validation is used only for evaluation (do Table 6 values equal the labels?). No API calls.
Usage: .venv/bin/python research/webintel/table6_check.py [submission.csv]"""
import re, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from qp.data import load_test, load_split, load_validation
sub = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "submissions/trackA_cand_physb2_on_p21.csv")
TH = np.array([.1, .2, .3, .4, .5, .6, .7, .8, .9, .95])
item = lambda p, g: float((abs(p - g) / g < 1 - TH).mean())
N = {"S2": 553, "D2": 1137, "S3": 538, "D3": 933}
RULES = [  # (question regex, Table 6 value in cm, name, confidence)
    (r"yoga ball.*diameter|diameter of the yoga ball|yoga ball's diameter", 52.2, "yoga ball d", "high"),
    (r"diameter of the soccer ball|soccer ball's diameter", 17.5, "soccer ball d", "high"),
    (r"height of the pink bottle", 19.5, "pink bottle h", "high"),
    (r"height of the glass jar", 8.5, "glass jar h", "high"),
    (r"height of the pencil bag", 6.7, "pencil case h", "high"),
    (r"length of the pencil bag", 21.0, "pencil case l", "high"),
    (r"height of the (white )?cup", 14.5, "white cup h", "high"),
    (r"rim of the white cup", 8.6, "white cup d", "high"),
    (r"diameter of the cookie", 8.0, "toy cookie d", "high"),
    (r"length of the pen\b", 14.5, "black pen l", "high"),
    (r"length of the slope", 30.8, "small whiteboard l", "high"),
    (r"width of the slope", 23.2, "small whiteboard w", "high"),
    (r"diameter of the tape", 10.1, "tape d", "high"),
    (r"basketball's diameter|diameter of the basketball", 23.2, "basketball d", "high"),
    (r"diameter of the tennis ball", 6.7, "tennis ball d", "high"),
    (r"length of the whiteboard", 81.0, "large whiteboard l", "check frames"),
    (r"width of the whiteboard", 60.0, "large whiteboard w", "check frames"),
]
def match(q):
    q = q.lower()
    for pat, v, name, conf in RULES:
        if re.search(pat, q): return v, name, conf
    return None
t = load_test().reset_index(drop=True)
vv = load_split("val_hires"); vk = set(zip(vv.video_id, vv.question.str.strip().str.lower()))
t["ov"] = [(a, b.strip().lower()) in vk for a, b in zip(t.video_id, t.question)]
s = pd.read_csv(sub); assert (s.video_id.values == t.video_id.values).all(); t["pred"] = s.parsed_value.values
rows = []
for i, r in t[t.video_source.eq("lab")].iterrows():
    m = match(r.question)
    if m: rows.append(dict(qid=i, vid=r.video_id, cat=r.category, name=m[1], conf=m[2], pred=r.pred, t6=m[0], ov=r.ov, gain=1 - item(r.pred, m[0])))
df = pd.DataFrame(rows); sc = df[~df.ov]
g = sc.groupby(["name", "conf", "cat"]).agg(n=("qid", "size"), pred_med=("pred", "median"), t6=("t6", "first"), gain=("gain", "sum")).reset_index()
g["overall"] = [a / (4 * N[c]) for a, c in zip(g.gain, g.cat)]
pd.set_option("display.width", 200)
print(g.sort_values("overall", ascending=False).round(4).to_string())
print("overall gain if Table 6 = label, high-confidence rules:", round(g[g.conf == "high"].overall.sum(), 4), "| all:", round(g.overall.sum(), 4))
v = load_validation(); hits = [(r.video_id, *match(r.question)[1:2], match(r.question)[0], r.answer) for _, r in v.iterrows() if match(r.question)]
print("validation rows matched (vid, prop, table6, label):"); [print(" ", h) for h in hits]
print("exact Table-6 = label:", sum(abs(h[2] - h[3]) < 1e-6 for h in hits), "of", len(hits))
