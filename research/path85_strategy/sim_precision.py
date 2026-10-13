"""Monte Carlo: interval width of a decoded lever delta under the leaderboard's rounding, for upload designs:
 A) base + upload both with 4 changed categories, overall shown to 3 decimals
 B) same with overall shown to 4 decimals
 C) single-category upload (other 3 categories identical to base), overall to 4 decimals."""
import numpy as np
from decode import decode
rng = np.random.default_rng(0)
def run(design, n=300):
    w = []
    for _ in range(n):
        B = rng.uniform(.75, .87, 4); d = rng.normal(0, .002, 4)
        if design == "C": d[[0, 1, 3]] = 0
        S = B + d
        r4 = design in "BC"
        f = (lambda x: round(x, 4)) if r4 else (lambda x: round(x, 3))
        cats = ("S2", "D2", "S3", "D3")
        ups = [{"name": "base", "levers": {}, "scores": {**{c: round(b, 3) for c, b in zip(cats, B)}, "overall": f(B.mean())}},
               {"name": "u", "levers": ({"S3": ["x"]} if design == "C" else {c: ["x"] for c in cats}),
                "scores": {**{c: round(s, 3) for c, s in zip(cats, S)}, "overall": f(S.mean())}}]
        v = decode({"uploads": ups, "overall_dp": 4 if r4 else 3})
        lo, hi = v["S3:x"]; assert lo - 1e-9 <= d[2] <= hi + 1e-9
        w.append(hi - lo)
    return np.mean(w), np.quantile(w, .9)
for dsg in "ABC":
    m, q = run(dsg); print(dsg, f"mean width of the S3 delta interval {m:.5f} (90th pct {q:.5f})")
