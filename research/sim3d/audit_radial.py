"""Candidates (a) and (b): does the 3D speed convention (full 3D origin speed, incl. motion toward / away
from the camera) cause a systematic deviation in our 3D non-lab answers? Test inputs only:
  1. stated speed priors vs the radial lower bound |dr/dt| from depth_info (labels include depth if
     every v_stated >= |dr/dt|);
  2. leave-one-fact-out (a question whose value a family clip states) speed answers vs the asked object's
     radial fraction f = |dr/dt| / v_stated;
  3. size answers in clips with a speed prior vs the prior object's radial fraction (if the prior were
     converted from image motion only, sizes would be inflated by 1/sqrt(1-f^2)).
    .venv/bin/python research/sim3d/audit_radial.py
"""
from common import *  # noqa: F401,F403
from common import ROOT, load_split, table, answers, depth_tracks, parse_prior_text, pp, np, pd
from qp.geometry import name_score


class _R:
    def __init__(self, c):
        self.correlation, self.pvalue = c, float("nan")


def spearmanr(a, b):
    ra, rb = pd.Series(list(a)).rank(), pd.Series(list(b)).rank()
    return _R(float(np.corrcoef(ra, rb)[0, 1]))


def radial(depth_info, obj):
    best = None
    for k, e in depth_tracks(depth_info).items():
        te = [x for x in e if x[0] is not None]
        s = name_score(k, obj)
        if s >= 0.5 and len(te) >= 2 and (best is None or s > best[0]):
            best = (s, te)
    if best is None:
        return np.nan
    (t0, r0), (t1, r1) = best[1][0], best[1][-1]
    return abs(r1 - r0) / (t1 - t0)


def lofo_table(t, a):
    full = load_split("test")
    c = pp.stated_facts(full, pp.FrameCache(pp.DEFAULT_CACHE))
    c = c[c.qid.isin(t.index)]
    rows = []
    for q, g in c.groupby("qid"):
        g = g[g.tier == g.tier.min()]
        v = np.unique(np.round(g.value, 9))
        if len(v) == 1:
            rows.append(dict(qid=q, stated=v[0]))
    return pd.DataFrame(rows).set_index("qid").join(t).join(a)


def main():
    t = table()
    a = answers(t)
    # 1. priors
    pri = []
    for (v, prior, di), _ in t.groupby(["video_id", "prior", "depth_info"]):
        p = parse_prior_text(str(prior).split("\n")[0])
        if p["kind"] == "speed" and p["objects"]:
            vr = radial(di, p["objects"][0])
            if np.isfinite(vr):
                pri.append(dict(video=v, v=p["value_si"], vr=vr, f=vr / p["value_si"]))
    pri = pd.DataFrame(pri)
    print(f"1. stated speed priors with a timed depth track of the same object: {len(pri)} clips; "
          f"radial fraction f = |dr/dt|/v: median {pri.f.median():.2f}, max {pri.f.max():.3f}, "
          f"f > 1.05: {(pri.f > 1.05).sum()}, f > 0.8: {(pri.f > 0.8).sum()}")
    f = lofo_table(t, a)
    sp = f[f.kind == "speed"].copy()
    sp["f"] = [radial(r.depth_info, r.objs[0]) / r.stated for r in sp.itertuples()]
    sp["r"] = sp.dmed / sp.stated
    s = sp.dropna(subset=["f"])
    rho = spearmanr(s.f, s.r)
    print(f"2. LOFO speed answers (median of 3 runs) / stated: n={len(sp)} (with depth track {len(s)}), "
          f"median {sp.r.median():.3f}; Spearman(f, ratio) = {rho.correlation:+.2f}")
    for lo, hi in [(0, .3), (.3, .7), (.7, 1.01)]:
        z = s[(s.f >= lo) & (s.f < hi)]
        print(f"     f in [{lo},{hi}): n={len(z)} median ratio {z.r.median():.3f}")
    # 3. sizes in speed-prior clips
    sz = f[(f.kind == "size") & (f.pkind == "speed")].copy()
    sz["f"] = [radial(r.depth_info, r.pobjs[0]) / r.pval for r in sz.itertuples()]
    sz["r"] = sz.dmed / sz.stated
    s = sz.dropna(subset=["f"])
    rho = spearmanr(s.f, s.r)
    print(f"3. LOFO size answers in speed-prior clips: n={len(s)}; Spearman(f_prior, ratio) = "
          f"{rho.correlation:+.2f}; image-motion-only scaling predicts a POSITIVE slope")
    for lo, hi in [(0, .3), (.3, 1.01)]:
        z = s[(s.f >= lo) & (s.f < hi)]
        print(f"     f in [{lo},{hi}): n={len(z)} clips={z.video_id.nunique()} median ratio {z.r.median():.3f} "
              f"(predicted if image-motion only: {np.median(1/np.sqrt(np.clip(1-z.f**2,1e-3,1))):.2f})")
    # 4. our answers vs the radial bound
    x = t.join(a)
    x = x[x.kind == "speed"].copy()
    x["vr"] = [radial(r.depth_info, r.objs[0]) if r.objs else np.nan for r in x.itertuples()]
    x = x.dropna(subset=["vr"])
    below = x[x.p8 < 0.95 * x.vr]
    print(f"4. speed questions whose object has a timed depth track: {len(x)}; p8 below 0.95 x |dr/dt|: {len(below)}"
          f" ({', '.join(f'{q}:{r.video_id}' for q, r in below.iterrows())}) -- all accelerating objects asked "
          f"outside the depth window")


if __name__ == "__main__":
    main()
