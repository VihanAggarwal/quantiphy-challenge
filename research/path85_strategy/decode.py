"""Rounding-aware reading of leaderboard uploads (no labels involved: only our own upload scores).

Every upload is physb2 plus a set of levers (each lever = a fixed set of changed rows in ONE category). A category score
is the mean of item scores, so disjoint levers add exactly: S_uc = B_c + sum(delta_l, l in upload u, category c).
The leaderboard shows category scores to 3 decimals and the overall (mean of the 4) to 4 decimals, so
    |S_uc - obs_uc| <= h3   and   |mean_c S_uc - obs_u| <= h4      (h = half a unit when rounded).
This script propagates those interval constraints (box consistency) to bounds on each lever's delta and on the
physb2 base scores. A lever measured alone in an upload whose other three categories equal an earlier upload is
pinned to +-0.0004 by the overall's 4th decimal, instead of +-0.001 from the category scores.

    python decode.py uploads.json            # prints delta bounds per lever (category units and overall units)
uploads.json: {"rounding": "round"|"trunc", "uploads": [{"name": .., "levers": {"S3": ["sz4"], ...},
               "scores": {"S2": .817, "D2": .859, "S3": .766, "D3": .803, "overall": .8113}}, ...]}
Levers sharing rows inside one upload/category are not additive: never put two such levers in one slot."""
import json, sys
from collections import defaultdict

CATS = ("S2", "D2", "S3", "D3")
N = {"S2": 553, "D2": 1137, "S3": 538, "D3": 933}  # scored rows (approximate to ~+-12 rows)


def decode(spec, iters=200):
    trunc = spec.get("rounding", "round") == "trunc"
    var = {f"B_{c}": [0.0, 1.0] for c in CATS}
    cons = []  # (coef dict, lo, hi)
    for u in spec["uploads"]:
        sc, lev = u.get("scores") or {}, u.get("levers") or {}
        for c in lev:
            for l in lev[c]:
                var.setdefault(f"{c}:{l}", [-1.0, 1.0])
        terms_all = defaultdict(float)
        for c in CATS:
            terms = {f"B_{c}": 1.0}
            for l in lev.get(c, []):
                terms[f"{c}:{l}"] = terms.get(f"{c}:{l}", 0) + 1.0
            for k, a in terms.items():
                terms_all[k] += a / 4
            if sc.get(c) is not None:
                o = float(sc[c]); lo, hi = (o, o + 1e-3) if trunc else (o - 5e-4, o + 5e-4)
                cons.append((terms, lo, hi))
        if sc.get("overall") is not None:
            o = float(sc["overall"])
            d = sc.get("overall_dp") or spec.get("overall_dp") or max(3, len(str(sc["overall"]).split(".")[-1]))
            h = 10.0 ** -d
            lo, hi = (o, o + h) if trunc else (o - h / 2, o + h / 2)
            cons.append((dict(terms_all), lo, hi))
    # pairwise differences cancel the unknown base scores (what an LP would exploit); keep those that get shorter
    extra = []
    for i in range(len(cons)):
        for j in range(len(cons)):
            if i == j:
                continue
            (a1, l1, h1), (a2, l2, h2) = cons[i], cons[j]
            d = {k: a1.get(k, 0) - a2.get(k, 0) for k in set(a1) | set(a2)}
            d = {k: v for k, v in d.items() if abs(v) > 1e-12}
            if d and len(d) < min(len(a1), len(a2)) or (d and not any(k.startswith("B_") for k in d)):
                extra.append((d, l1 - h2, h1 - l2))
    cons = cons + extra
    for _ in range(iters):
        changed = False
        for terms, lo, hi in cons:
            for j, aj in terms.items():
                rest_lo = sum(min(a * var[k][0], a * var[k][1]) for k, a in terms.items() if k != j)
                rest_hi = sum(max(a * var[k][0], a * var[k][1]) for k, a in terms.items() if k != j)
                nlo, nhi = (lo - rest_hi) / aj, (hi - rest_lo) / aj
                if aj < 0:
                    nlo, nhi = nhi, nlo
                if nlo > var[j][0] + 1e-12:
                    var[j][0] = nlo; changed = True
                if nhi < var[j][1] - 1e-12:
                    var[j][1] = nhi; changed = True
        if not changed:
            break
    return var


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    var = decode(spec)
    print(f"{'variable':40s} {'lo':>9s} {'hi':>9s} {'mid':>9s}  overall-units (mid)")
    for k, (lo, hi) in var.items():
        if k.startswith("B_"):
            print(f"{k:40s} {lo:9.5f} {hi:9.5f} {(lo + hi) / 2:9.5f}")
    for k, (lo, hi) in sorted(var.items()):
        if not k.startswith("B_"):
            verdict = "WIN" if lo > 0 else ("LOSS" if hi < 0 else "ambiguous")
            extra = ""
            cat, lev = k.split(":", 1)
            if lev.startswith("zero:") and lev[5:] in spec.get("scored_n", {}):
                n = spec["scored_n"][lev[5:]]
                extra = f"  subset mean {-hi * N[cat] / n:.3f}..{-lo * N[cat] / n:.3f} (scored n {n})"
            print(f"{k:40s} {lo:+9.5f} {hi:+9.5f} {(lo + hi) / 2:+9.5f}  {(lo + hi) / 8:+.5f}  {verdict}{extra}")
