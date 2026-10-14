import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import Data, fmt  # noqa
from levers_a import l2_qwen_only, affected_val, changed_rows  # noqa
D = Data()
c = pd.read_pickle(Path(__file__).resolve().parent / "cache_levers_a.pkl")
p, lg = l2_qwen_only(D, c["post"])
n, s = affected_val(D, c["post"], p)
print("L2' qwen-only fov:", fmt(D.score(p)), "| boot", fmt(D.boot(c["post"], p)), f"| val rows {n} item sum {s:+.2f}",
      f"| test rows {changed_rows(D, c['post'], p)}")
pd.to_pickle(dict(post=p, log=lg), Path(__file__).resolve().parent / "cache_l2q.pkl")
