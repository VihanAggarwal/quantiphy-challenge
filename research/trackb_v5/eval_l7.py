import sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from harness import Data, V3, VAL_OFFSET, fmt  # noqa
from levers_a import labnoise, affected_val, changed_rows  # noqa
D = Data()
c = pd.read_pickle(HERE / "cache_levers_a.pkl")
post, log = c["post"], c["log"]
l7, F = labnoise(D, post, log, D.df, 0.02, 0.02, cats=("D3",))
n, s = affected_val(D, post, l7)
print("L7 D3 labnoise:", fmt(D.score(l7)), "| boot", fmt(D.boot(post, l7)), f"| val rows {n} item sum {s:+.2f}",
      f"| test rows {changed_rows(D, post, l7)} | test factor median {F[F.qid < VAL_OFFSET].factor.median():.3f}")
print(F[F.qid < VAL_OFFSET].groupby(["cls", "kind"]).factor.agg(["size", "median"]).round(3).to_string())
