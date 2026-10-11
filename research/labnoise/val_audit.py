"""Validation lab motion questions: label vs our answers vs physical measurement on Claude's target track
(fixed lab camera, capture clock), with the lateral fraction sin(psi). Evaluation-only use of labels.
Writes out/val_motion.csv."""
import numpy as np, pandas as pd
from common import tracks, treal, track_real, local_fit, lateral_fraction, obj_class, motion_kind, mra_item, HERE, ROOT
from qp.data import load_split

d = tracks("val_hires")
v = load_split("val_hires").set_index("qid")
res = pd.read_csv(ROOT / "runs/val_hr_v1_high/val_hires.csv").set_index("id")
rows = []
for q, x in sorted(d.items()):
    kind = motion_kind(x["question"])
    if kind is None:
        continue
    sp = x["spec"].target
    c = x["cap"].get("target")
    out = dict(qid=q, video=x["video"], category=x["category"], kind=kind, question=x["question"][:70],
               object=(c or {}).get("name", sp.objects[0] if sp.objects else ""), t=sp.time,
               window=sp.window, answer=float(v.loc[q, "answer"]), direct=x["direct"],
               parsed=float(res.loc[q, "parsed_value"]), geo=float(res.loc[q, "geo_value"]))
    out["cls"] = obj_class(out["object"])
    unit = 100.0 if ("cm" in str(v.loc[q, "target_unit"])) else 1.0
    out["unit"] = unit
    if c is not None:
        tr, P = track_real(c)
        out["depth_m"] = float(np.median(c["rng"]))
        out["depth_varies"] = bool(np.ptp(c["rng"]) > 1e-6)
        out["n"] = len(tr)
        if kind == "speed" and sp.time is not None:
            t0 = float(treal([float(sp.time)])[0])
            f = local_fit(tr, P, t0, 0.25)
            out["phys"] = float(np.linalg.norm(f[1])) * unit
            out["sin_psi"] = lateral_fraction(f[0], f[1])
        elif kind in ("path_length", "displacement"):
            if kind == "displacement" and sp.window:
                w = [float(treal([w])[0]) for w in sp.window]
                p0 = local_fit(tr, P, w[0], 0.25)[0]; p1 = local_fit(tr, P, w[1], 0.25)[0]
                out["phys"] = float(np.linalg.norm(p1 - p0)) * unit
                mid = local_fit(tr, P, 0.5 * (w[0] + w[1]), 0.25)
            else:
                # smoothed path: fitted positions at each obs time (local quadratic, +-0.25 s)
                Q = np.array([local_fit(tr, P, ti, 0.25)[0] for ti in tr])
                out["phys"] = float(np.linalg.norm(np.diff(Q, axis=0), axis=1).sum()) * unit
                mid = local_fit(tr, P, float(np.median(tr)), 0.25)
            dP = P[-1] - P[0]
            out["sin_psi"] = lateral_fraction(np.median(P, axis=0), dP) if np.linalg.norm(dP) > 0 else np.nan
        elif kind == "acceleration" and sp.time is not None:
            t0 = float(treal([float(sp.time)])[0])
            f = local_fit(tr, P, t0, 0.35)
            out["phys"] = float(np.linalg.norm(f[2])) * unit
            out["sin_psi"] = lateral_fraction(f[0], f[1])
    rows.append(out)
df = pd.DataFrame(rows)
df["r_label_direct"] = df.answer / df.direct
df["r_label_phys"] = df.answer / df.phys
df["r_direct_phys"] = df.direct / df.phys
df["mra_direct"] = [mra_item(p, g) for p, g in zip(df.direct, df.answer)]
pd.set_option("display.width", 260); pd.set_option("display.max_columns", 40)
print(df.drop(columns=["question", "window"]).round(3).to_string())
df.to_csv(HERE / "out" / "val_motion.csv", index=False)
