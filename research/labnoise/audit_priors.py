"""Task 1a: label-free audit of the TEST lab speed priors (stated values are labels made by the lab procedure).

For each test lab clip whose prior is a velocity/speed, the prior object's speed is measured from Claude's
(post-processed) track at the fixed lab camera (f = 722 px @ 1280, depth_info range + looming, capture clock) and
compared with the stated value; the motion is classified by the lateral fraction sin(psi) of the velocity.
Also checks the slope acceleration priors (central second differences in the label procedure).
Writes out/prior_audit.csv."""
import numpy as np, pandas as pd
from common import tracks, treal, track_real, local_fit, lateral_fraction, obj_class, HERE

d = tracks("test")
rows = []
seen = set()
for q, v in sorted(d.items()):
    k = v["spec"].prior.kind
    if k not in ("speed", "acceleration") or v["video"] in seen:
        continue
    c = v["cap"].get("prior")
    if c is None:
        continue
    seen.add(v["video"])
    t0 = float(v["spec"].prior.time) if v["spec"].prior.time is not None else np.nan
    stated = float(v["spec"].prior.value_si)
    t0r = float(treal([t0])[0]) if np.isfinite(t0) else np.nan
    tr, Preal = track_real(c)
    out = dict(video=v["video"], qid=q, kind=k, object=c["name"], cls=obj_class(c["name"]), stated=stated, t0=t0,
               n=len(tr), span=f"{c['t'].min():.2f}-{c['t'].max():.2f}", depth_m=float(np.median(c["rng"])),
               depth_varies=bool(np.ptp(c["rng"]) > 1e-6), pipeline=v["debug"].get("prior_measured_si"))
    for half in (0.17, 0.25, 0.35):
        f = local_fit(tr, Preal, t0r, half)
        if f is None:
            continue
        pos, vel, acc = f
        if k == "speed":
            out[f"meas_h{half}"] = float(np.linalg.norm(vel))
        else:
            # tangential acceleration along the path, and the vector norm
            out[f"meas_h{half}"] = float(np.linalg.norm(acc))
        if half == 0.25:
            fv = local_fit(c["t"], c["P"], t0, half)
            out["meas_video"] = float(np.linalg.norm(fv[1] if k == "speed" else fv[2]))
            out["sin_psi"] = lateral_fraction(pos, vel)
            out["speed_t0"] = float(np.linalg.norm(vel))
            out["px_per_frame"] = float(np.linalg.norm(vel) / out["depth_m"] * 722 / 25)
    if k == "acceleration":
        f = local_fit(tr, Preal, t0r, 0.6)
        if f is not None:
            out["meas_h0.6"] = float(np.linalg.norm(f[2]))
    rows.append(out)
res = pd.DataFrame(rows)
res["ratio"] = res.stated / res["meas_h0.25"]
res["ratio_pipeline"] = res.stated / res.pipeline
res["ratio_video"] = res.stated / res.meas_video
# renders without a depth model for the prior (constant range although the object moves radially in the
# original render) cannot measure radial motion: 0062s/x (the original 0062 looms) -> excluded from the event
res["use"] = ~res.video.isin(["captured_0062s", "captured_0062x"])
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
cols = ["video", "kind", "object", "cls", "stated", "t0", "n", "span", "depth_m", "depth_varies", "pipeline",
        "meas_h0.17", "meas_h0.25", "meas_h0.35", "meas_h0.6", "meas_video", "ratio", "ratio_pipeline", "ratio_video", "use", "sin_psi", "speed_t0",
        "px_per_frame"]
print(res[[c for c in cols if c in res]].round(3).to_string())
res.to_csv(HERE / "out" / "prior_audit.csv", index=False)
sp = res[(res.kind == "speed") & res.use].copy()
sp["event"] = sp.video.str.replace(r"(captured_\d+[ab]?).*", r"\1", regex=True)
ev = sp.groupby("event").agg(object=("object", "first"), cls=("cls", "first"), stated=("stated", "first"),
                             ratio=("ratio", lambda x: float(np.exp(np.log(x).median()))),
                             ratio_video=("ratio_video", lambda x: float(np.exp(np.log(x).median()))),
                             ratio_pipe=("ratio_pipeline", lambda x: float(np.exp(np.log(x).median()))),
                             sin_psi=("sin_psi", "median"), speed=("speed_t0", "median"), depth=("depth_m", "median"),
                             px_per_frame=("px_per_frame", "median"), renders=("video", "count"))
print("\nper event (median over renders):"); print(ev.round(3).to_string())
ev.to_csv(HERE / "out" / "prior_audit_events.csv")
