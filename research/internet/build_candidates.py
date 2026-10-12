"""Internet-clip candidates on probe 8 (test inputs only; validation labels are used only in eval_val.py).

Rules (each a separate candidate; `main` = FWD + WINACC + TWIN + ACORN):
  FWD    internet label convention for speeds at a time: forward one-frame difference |p(i+1) - p(i)| * fps at
         i = round(t * fps) (paper App. D.3), on the same fitted track (research/internet/fwd_emulate.py replay,
         refine off = the D2 setting; S2 internet rows are identical with refine on). Applies to timed speed
         targets and, through the scale, to every row of a clip whose PRIOR is a timed speed (0043, 0047, 0070).
         Ratio on/off applied to probe 8; gated |ratio - 1| <= 15% (an apex / bounce makes the one-frame
         difference volatile); a segmented twin whose probe-8 value is its original's copy takes the original's
         ratio; stated-fact rows are never touched.
  WINACC acceleration questions phrased over the windows whose average speeds sibling questions ask
         ("from 0s-2s to 2s-4.5s", "over 0-7s" with windows 0-2 / 2-4.5 / 4.5-7 asked): the annotators' natural
         estimate (v2 - v1) / (midpoint2 - midpoint1) from the probe-8 window speeds, instead of the curvature of a
         parabola fitted to positions over the whole span (which picks up stroke / wave oscillations: 0039 swimmer
         0.079 vs 0.012).
  TWIN   segmented internet twins whose question text differs from the original's only in wording ("speed" vs
         "average speed", "9.8m/s" vs "9.8m/s^2") were not copied by probe 8's twin rule; the twin labels reuse the
         original annotation (paper App. C.4), so both rows take the log-mean of the two measurements (only when
         they agree within 15%; 0005_segmented states a different prior and is left alone).
  ACORN  the same toy acorn appears in internet_0061 / 0067 / 0068; 0067 states its height (8 cm). The two
         "height of the acorn" questions (0061 gravity, 0068 acceleration prior) take 8.0 cm (family stated fact).
Hypothesis probe (separate file, D2 only): PHYSB = internet labels are physical (the stated motion prior was
derived by the annotators, with an error that their labels do not inherit). Rescales the clips whose in-clip
scale contradicts their own scene family: 0043 (same desk, bottles and kettle as 0044 gravity / 0045 rolling
cylinder: x2.35) and the scooter series 0051 / 0053 / 0054 (same rider and scooter as 0049/0050/0052/0056:
rider height anchored to their median 1.62 m). Opposite of D2-static's "answers stay in-clip"; one upload decides.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.data import load_split  # noqa: E402

BASE = ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv"
OUT = ROOT / "research/internet/out"
FWD_TAG = "test_test_v1_high_854_refoff_fwd1"
FWD_CAP = 0.15
TWIN_MAX = 0.15

df = load_split("test").set_index("qid")
base = pd.read_csv(BASE).set_index("id")["parsed_value"]
off = pd.read_csv(OUT / f"{FWD_TAG}_off.csv").set_index("id")
on = pd.read_csv(OUT / f"{FWD_TAG}_on.csv").set_index("id")
internet = [q for q in df.index if str(df.video_id[q]).startswith("internet")]


def stated_numbers() -> np.ndarray:
    vals = []
    for p in df.prior.astype(str):
        for m in re.findall(r"\d+(?:\.\d+)?", p):
            v = float(m)
            if v > 0:
                vals += [v * f for f in (1, 100, 0.01, 1000, 0.001, 10, 0.1)]
    return np.array(vals)


STATED = stated_numbers()


def is_stated(v: float) -> bool:
    return bool(np.any(np.isclose(STATED, v, rtol=1e-6)))


def norm_q(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower().replace("average ", ""))


def twin_source() -> dict[int, int]:
    """segmented-twin qid -> original qid with the same normalised question."""
    out = {}
    for q in internet:
        v = str(df.video_id[q])
        if not v.endswith("_segmented"):
            continue
        o = df[(df.video_id == v[: -len("_segmented")]) & (df.question.map(norm_q) == norm_q(df.question[q]))]
        if len(o) == 1:
            out[q] = int(o.index[0])
    return out


TWINS = twin_source()


def rule_fwd(cur: pd.Series, log: list) -> None:
    ratio = (on.geo_value / off.geo_value).reindex(internet)
    for q in internet:
        src = q
        if q in TWINS and np.isclose(base[q], base[TWINS[q]], rtol=1e-9):
            src = TWINS[q]                         # probe 8 copied the original's answer: follow its ratio
        r = ratio.get(src)
        if r is None or not np.isfinite(r) or abs(r - 1) <= 0.002:
            continue
        if abs(r - 1) > FWD_CAP:
            log.append((q, "FWD", "skip: ratio %.3f beyond cap" % r)); continue
        if is_stated(base[q]):
            log.append((q, "FWD", "skip: stated-fact value")); continue
        new = cur[q] * r
        log.append((q, "FWD", f"{cur[q]:.4g} -> {new:.4g} (x{r:.4f}{', twin of %d' % src if src != q else ''})"))
        cur[q] = new


# (target qid, [(window speed qid, t0, t1), ...]): accelerations between asked windows
WINACC = {
    3019: [(3016, 0.0, 2.0), (3017, 2.0, 4.5)],
    3020: [(3017, 2.0, 4.5), (3018, 4.5, 7.0)],
    3021: [(3016, 0.0, 2.0), (3018, 4.5, 7.0)],
    3039: [(3036, 0.0, 2.07), (3037, 2.07, 5.20)],
    3049: [(3046, 0.0, 1.0), (3047, 1.0, 2.33)],
}


def rule_winacc(cur: pd.Series, log: list) -> None:
    for q, ((a, a0, a1), (b, b0, b1)) in WINACC.items():
        dv = abs(cur[b] - cur[a])
        dt = (b0 + b1) / 2 - (a0 + a1) / 2
        new = dv / dt
        log.append((q, "WINACC", f"{cur[q]:.4g} -> {new:.4g} (x{new / cur[q]:.3f}; v {cur[a]:.4g} -> {cur[b]:.4g} over {dt:.3f} s)"))
        cur[q] = new


def rule_twin(cur: pd.Series, log: list) -> None:
    for q, o in TWINS.items():
        if np.isclose(base[q], base[o], rtol=1e-9):
            continue                                   # already copied
        if df.prior[q].replace(" ", "").rstrip("^2") != df.prior[o].replace(" ", "").rstrip("^2") and \
                re.findall(r"\d+(?:\.\d+)?", df.prior[q]) != re.findall(r"\d+(?:\.\d+)?", df.prior[o]):
            log.append((q, "TWIN", f"skip: prior differs ({df.prior[q]} / {df.prior[o]})")); continue
        a, b = cur[q], cur[o]
        if abs(np.log(a / b)) > np.log(1 + TWIN_MAX):
            log.append((q, "TWIN", f"skip: twin values {a:.4g} / {b:.4g} disagree")); continue
        new = float(np.exp((np.log(a) + np.log(b)) / 2))
        log.append((q, "TWIN", f"{a:.4g} -> {new:.4g} (pooled with {o}: {b:.4g})"))
        log.append((o, "TWIN", f"{b:.4g} -> {new:.4g} (pooled with {q}; validation-overlap row, unscored)"))
        cur[q] = new
        cur[o] = new


def rule_acorn(cur: pd.Series, log: list) -> None:
    for q in (3196, 3243):          # 0061 / 0068 "height of the acorn"; 0067 states "height of the acorn = 8 cm"
        assert "height of the acorn" in df.question[q] and "acorn = 8 cm" in str(df.prior[df.video_id == "internet_0067"].iloc[0])
        log.append((q, "ACORN", f"{cur[q]:.4g} -> 8.0 (stated in internet_0067)"))
        cur[q] = 8.0


PHYSB = {  # clip -> (anchor description, factor)
    "internet_0043": None, "internet_0051": None, "internet_0053": None, "internet_0054": None,
}


def physb_factors(cur: pd.Series) -> dict[str, float]:
    v = lambda vid, pat: [q for q in df.index if df.video_id[q] == vid and re.search(pat, df.question[q])]  # noqa: E731
    k = {}
    # desk scene: shared objects of 0043 vs the log-mean of 0044 (gravity) and 0045 (rolling cylinder)
    pats = [r"diameter of the white ball", r"height of the kettle", r"height of the white cylinder",
            r"height of the green bottle", r"height of the plastic bottle", r"height of the plate",
            r"distance between the kettle and the plate", r"distance between the cylinder and the plastic bottle"]
    ratios = []
    for p in pats:
        a = v("internet_0043", p)
        ref = [cur[q] for vid in ("internet_0044", "internet_0045") for q in v(vid, p)]
        if a and ref:
            ratios.append(float(np.exp(np.mean(np.log(ref)))) / cur[a[0]])
    k["internet_0043"] = float(np.median(ratios))
    # scooter series: rider height anchored to the clips whose rider height is in the series' band
    rider = {vid: cur[v(vid, r"height of the person riding scooter")[0]]
             for vid in ("internet_0049", "internet_0050", "internet_0051", "internet_0052", "internet_0053",
                         "internet_0054", "internet_0056")}
    band = [h for vid, h in rider.items() if vid not in ("internet_0051", "internet_0053", "internet_0054")]
    anchor = float(np.median(band))
    for vid in ("internet_0051", "internet_0053", "internet_0054"):
        k[vid] = anchor / rider[vid]
    print("PHYSB desk ratios", np.round(ratios, 3), "rider heights", {a: round(b, 3) for a, b in rider.items()},
          "anchor", round(anchor, 3))
    return k


def rule_physb(cur: pd.Series, log: list) -> None:
    for vid, f in physb_factors(cur).items():
        for q in df.index[df.video_id == vid]:
            if is_stated(cur[q]):
                continue
            log.append((q, "PHYSB", f"{cur[q]:.4g} -> {cur[q] * f:.4g} (x{f:.3f} {vid})"))
            cur[q] = cur[q] * f


def write(name: str, rules) -> None:
    cur = base.copy()
    log: list = []
    for r in rules:
        r(cur, log)
    out = ROOT / f"submissions/trackA_cand_internet_{name}_on_p8.csv"
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
        cur.rename("parsed_value").rename_axis("id").reset_index().to_csv(f.name, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), f.name, str(out)], check=True,
                   stdout=subprocess.DEVNULL)
    cand = pd.read_csv(out).set_index("id").parsed_value
    chg = ~np.isclose(cand, base.reindex(cand.index), rtol=1e-9)
    ids = cand.index[chg]
    lg = pd.DataFrame(log, columns=["qid", "rule", "note"])
    lg.to_csv(OUT / f"log_{name}.csv", index=False)
    by = df.category[ids].value_counts().to_dict()
    rat = (cand[ids] / base[ids])
    print(f"== {name}: changed {len(ids)} {by}; median ratio {rat.median():.4f}; "
          f"median |log| {np.median(np.abs(np.log(rat))) if len(ids) else 0:.4f} -> {out.name}")
    for c in ("S2", "D2"):
        ii = [i for i in ids if df.category[i] == c]
        if ii:
            print(f"   {c}: {len(ii)} rows, ratio range {rat[ii].min():.3f}..{rat[ii].max():.3f}")


if __name__ == "__main__":
    write("fwd", [rule_fwd])
    write("winacc", [rule_winacc])
    write("fam", [rule_twin, rule_acorn])
    write("main", [rule_twin, rule_acorn, rule_fwd, rule_winacc])
    write("physb", [rule_physb])
    for name in ("fwd", "winacc", "fam", "physb"):
        print(f"\n-- log {name}")
        print(pd.read_csv(OUT / f"log_{name}.csv").to_string(index=False))
