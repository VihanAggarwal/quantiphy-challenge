"""Task 3: evaluate the label-noise candidate rules on validation lab motion questions (labels used for scoring only).

Rules (all parameters fixed before looking at validation: noise fitted on test priors, SIGMA_A a priori):
  base      our answer (direct = what the submission uses on lab motion; parsed also reported)
  labnoise  base * MRA-optimal factor from the label emulator (speed, path length, displacement)
  lat13     base * 1.3 for speed questions about a small/mid ball whose motion is lateral (sin psi >= 0.7)
Sensitivity: the emulator at the upper end of the test-prior CI (sigma_zb 0.06) and a validation-fitted sigma_zb
chosen leave-one-video-out (the only validation-tuned variant)."""
import numpy as np, pandas as pd
from common import tracks, mra_item, HERE, ROOT
from qp.data import load_split
import emulate as EM

d = tracks("val_hires")
v = load_split("val_hires").set_index("qid")
res = pd.read_csv(ROOT / "runs/val_hr_v1_high/val_hires.csv").set_index("id")
rows = []
for q, x in sorted(d.items()):
    kind = EM.motion_kind(x["question"])
    if kind is None:
        continue
    r = dict(qid=q, video=x["video"], kind=kind, answer=float(v.loc[q, "answer"]), direct=float(x["direct"]),
             parsed=float(res.loc[q, "parsed_value"]))
    for tag, params in (("fit", EM.PARAMS), ("hi", dict(EM.PARAMS, sigma_zb=0.06))):
        m = EM.row_model(x, r["direct"], v.loc[q, "target_unit"], params)
        r[f"f_{tag}"] = m["factor"] if m else 1.0
        if m and tag == "fit":
            r.update(cls=m["cls"], sin_psi=m["sin_psi"], exp_ratio=m["exp_ratio"], med_ratio=m["med_ratio"])
    rows.append(r)
df = pd.DataFrame(rows)
df["lat13"] = np.where((df.kind == "speed") & df.cls.isin(["small ball", "mid ball"]) & (df.sin_psi >= 0.7), 1.3, 1.0)

# validation-fitted sigma_zb, leave one video out (for comparison only)
grid = [0.0, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10]
fz = {}
for s in grid:
    fz[s] = []
    for q in df.qid:
        x = d[q]
        m = EM.row_model(x, df.set_index("qid").loc[q, "direct"], v.loc[q, "target_unit"], dict(EM.PARAMS, sigma_zb=s))
        fz[s].append(m["factor"] if m else 1.0)
F = pd.DataFrame(fz, index=df.qid)
lovo = []
for q, vid in zip(df.qid, df.video):
    tr = df[df.video != vid]
    sc = {s: np.mean([mra_item(a * F.loc[qq, s], g) for qq, a, g in zip(tr.qid, tr.direct, tr.answer)]) for s in grid}
    s_best = max(sc, key=sc.get)
    lovo.append(F.loc[q, s_best])
df["f_lovo"] = lovo

df["f_cap"] = df.f_fit.clip(upper=1.6)
for base in ("direct", "parsed"):
    for rule, f in (("base", 1.0), ("labnoise(fit)", df.f_fit), ("labnoise(fit, cap 1.6)", df.f_cap), ("labnoise(sigma_zb .06)", df.f_hi), ("lat13", df.lat13),
                    ("val-fitted sigma_zb LOVO", df.f_lovo)):
        s = np.array([mra_item(a * ff, g) for a, ff, g in zip(df[base], np.broadcast_to(f, len(df)), df.answer)])
        no_acc = (df.kind != "acceleration").to_numpy()
        print(f"{base:7s} {rule:26s} all {s.mean():.3f} (n={len(s)})  excl. accel {s[no_acc].mean():.3f} (n={no_acc.sum()})")
    print()
pd.set_option("display.width", 250)
df["mra_base"] = [mra_item(a, g) for a, g in zip(df.direct, df.answer)]
df["mra_fit"] = [mra_item(a * f, g) for a, f, g in zip(df.direct, df.f_fit, df.answer)]
df["mra_cap"] = [mra_item(a * f, g) for a, f, g in zip(df.direct, df.f_cap, df.answer)]
df["mra_lat13"] = [mra_item(a * f, g) for a, f, g in zip(df.direct, df.lat13, df.answer)]
df["label_over_direct"] = df.answer / df.direct
print(df.round(3).to_string())
for k, g in df[df.kind != "acceleration"].groupby(df.kind.where(df.kind == "speed", "path/disp")):
    print(k, "n", len(g), "base %.3f fit %.3f cap %.3f lat13 %.3f" % (g.mra_base.mean(), g.mra_fit.mean(), g.mra_cap.mean(), g.mra_lat13.mean()))
# per-video sums (bootstrap over videos)
g = df[df.kind != "acceleration"].groupby("video")[["mra_base", "mra_fit", "mra_cap", "mra_lat13"]].sum()
print(g)
rng = np.random.default_rng(0); vids = g.index.to_numpy(); n = df[df.kind != "acceleration"].groupby("video").size()
for col in ("mra_fit", "mra_cap", "mra_lat13"):
    bs = []
    for _ in range(4000):
        s = rng.choice(vids, len(vids))
        bs.append((g.loc[s, col].sum() - g.loc[s, "mra_base"].sum()) / n.loc[s].sum())
    print(col, "video-bootstrap delta per question: mean %.3f, 90%% CI [%.3f, %.3f]" % (np.mean(bs), *np.percentile(bs, [5, 95])))
df.to_csv(HERE / "out" / "val_eval.csv", index=False)
