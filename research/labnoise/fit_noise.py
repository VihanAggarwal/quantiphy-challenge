"""Task 1b: fit the label-noise parameters on the TEST speed priors (inputs, not labels of scored questions).

Each prior event gives (stated label s, measured physical velocity vector v and position p from our tracks).
Model: s ~ speed_labels(p, v * exp(e), sigma_px, sigma_z[class]), e ~ N(0, sigma_m) (our measurement error).
Two free parameters: sigma_z for balls under 0.3 m (sigma_zb) and for large objects / non-balls (sigma_zL);
sigma_px fixed (1, 2 or 4 px, reported). Likelihood by simulation + log-normal kernel. Writes out/fit_noise.json."""
import json, sys
import numpy as np, pandas as pd
from common import tracks, treal, track_real, local_fit, lateral_fraction, obj_class, HERE
import labmodel as LM

SIGMA_M = 0.10     # log-sd of our physical speed measurement (render spread ~0.05, plus f / depth model error)
d = tracks("test")
ev = []
for q, x in sorted(d.items()):
    if x["spec"].prior.kind != "speed" or "prior" not in x["cap"]:
        continue
    if x["video"] in ("captured_0062s", "captured_0062x"):   # no depth model for the receding whiteboard
        continue
    c = x["cap"]["prior"]
    tr, P = track_real(c)
    t0 = float(treal([float(x["spec"].prior.time)])[0])
    pos, vel, _ = local_fit(tr, P, t0, 0.25)
    ev.append(dict(video=x["video"], event=x["video"][:13] + ("a" if "0054a" in x["video"] else "b" if "0054b" in x["video"] else ""),
                   cls=obj_class(c["name"]), stated=float(x["spec"].prior.value_si), p=pos, v=vel,
                   speed=float(np.linalg.norm(vel)), sin_psi=lateral_fraction(pos, vel)))
ev = pd.DataFrame(ev).drop_duplicates("video")
# one row per event: the render whose measured speed is the median of the event's renders
rows = []
for e, g in ev.groupby("event"):
    g = g.sort_values("speed"); rows.append(g.iloc[len(g) // 2])
E = pd.DataFrame(rows).reset_index(drop=True)
E["ball"] = E.cls.isin(["small ball", "mid ball"])
print(E[["event", "video", "cls", "stated", "speed", "sin_psi"]].assign(ratio=E.stated / E.speed).round(3).to_string())


def loglik(sig_px, szb, szL, events, n=3000):
    ll = []
    for _, r in events.iterrows():
        sz = szb if r.ball else szL
        L = LM.speed_labels(r.p, r.v, sig_px, sz, n=n, seed=1)
        # our measurement error: true speed = measured * exp(-e); labels scale ~ with speed for small noise only,
        # so integrate by re-simulating at a few scaled velocities
        dens = []
        for e in (-1.5, -0.5, 0.5, 1.5):
            k = np.exp(e * SIGMA_M)
            Lk = LM.speed_labels(r.p, r.v * k, sig_px, sz, n=n // 4, seed=2)
            dens.append(Lk)
        L = np.concatenate(dens)
        h = 0.04   # kernel log-bandwidth
        z = (np.log(r.stated) - np.log(L)) / h
        ll.append(np.log(np.mean(np.exp(-0.5 * z * z)) / (h * np.sqrt(2 * np.pi)) + 1e-12))
    return float(np.sum(ll)), ll


grid_b = np.r_[0.0, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10, 0.12, 0.15]
grid_L = np.r_[0.0, 0.005, 0.01, 0.02, 0.03, 0.05]
out = {}
for sig_px in (1.0, 2.0, 4.0):
    best = None
    tab = {}
    for szb in grid_b:
        for szL in grid_L:
            ll, per = loglik(sig_px, szb, szL, E)
            tab[(szb, szL)] = ll
            if best is None or ll > best[0]:
                best = (ll, szb, szL, per)
    # profile likelihood over sigma_zb (max over sigma_zL)
    prof = {b: max(tab[(b, L)] for L in grid_L) for b in grid_b}
    profL = {L: max(tab[(b, L)] for b in grid_b) for L in grid_L}
    ci_b = [b for b in grid_b if prof[b] >= best[0] - 1.92]
    ci_L = [L for L in grid_L if profL[L] >= best[0] - 1.92]
    print(f"sigma_px={sig_px}: best sigma_zb={best[1]} sigma_zL={best[2]} ll={best[0]:.2f}; "
          f"95% profile CI sigma_zb {min(ci_b)}..{max(ci_b)}, sigma_zL {min(ci_L)}..{max(ci_L)}")
    print("   profile ll sigma_zb:", {float(b): round(v - best[0], 2) for b, v in prof.items()})
    print("   per-event ll at best:", dict(zip(E.event, np.round(best[3], 2))))
    out[str(sig_px)] = dict(sigma_zb=best[1], sigma_zL=best[2], ll=best[0], ci_zb=[min(ci_b), max(ci_b)],
                            ci_zL=[min(ci_L), max(ci_L)], profile_zb={str(b): v - best[0] for b, v in prof.items()})
# sensitivity: which events carry the ball-noise fit
for name, sub in (("no 0054 events", E[~E.event.isin(["captured_0054a", "captured_0054b"])]),
                  ("0054b camera only (0054a dropped)", E[E.event != "captured_0054a"]),
                  ("0054a camera only (0054b dropped)", E[E.event != "captured_0054b"])):
    best = max(((loglik(2.0, b, L, sub)[0], b, L) for b in grid_b for L in grid_L))
    print(f"sensitivity [{name}]: best sigma_zb={best[1]} sigma_zL={best[2]}")
    out["sens_" + name] = dict(sigma_zb=best[1], sigma_zL=best[2])
# acceleration labels: a raw central second difference of the same clicks would carry noise
# sqrt(6) * sigma * fps^2 (radial axis), far above the slope-acceleration priors (2.8-4.6 m/s^2)
print("raw central-difference acceleration noise at the fit: sd %.1f m/s^2 (balls), so acceleration labels must be "
      "smoothed differently -> accelerations are left alone" % (np.sqrt(6) * out["2.0"]["sigma_zb"] * 25 ** 2))
# expected inflation for reference geometries at the fit (sigma_px = 2)
b = out["2.0"]
print("\nexpected median label/physical at the fit (sigma_px=2):")
for nm, sp, sn, dep, sz in (("tennis lateral 0.62 m/s @0.75 m", 0.62, 1.0, 0.75, b["sigma_zb"]),
                            ("soccer lateral 1.9 m/s @1.8 m", 1.9, 0.77, 1.8, b["sigma_zb"]),
                            ("basketball lateral 3.1 m/s @2.5 m", 3.1, 0.94, 2.5, b["sigma_zb"]),
                            ("ping pong radial 1.2 m/s @1.2 m", 1.2, 0.15, 1.2, b["sigma_zb"]),
                            ("orange ball 1.6 m/s sin .74 @2.1 m", 1.6, 0.74, 2.1, b["sigma_zb"]),
                            ("trashbin lateral 1.0 m/s @2.7 m", 1.0, 1.0, 2.7, b["sigma_zL"])):
    p, v = LM.geom(sp, sn, dep)
    L = LM.speed_labels(p, v, 2.0, sz, n=20000)
    print(f"   {nm}: median {np.median(L) / sp:.2f}, mean {L.mean() / sp:.2f}, p10-p90 {np.percentile(L, 10) / sp:.2f}-{np.percentile(L, 90) / sp:.2f}")
json.dump(out, open(HERE / "out" / "fit_noise.json", "w"), indent=1, default=float)
E.drop(columns=["p", "v"]).to_csv(HERE / "out" / "fit_events.csv", index=False)
