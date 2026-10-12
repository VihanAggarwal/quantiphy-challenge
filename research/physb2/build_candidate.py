"""PHYSB2: extend the leaderboard-confirmed PHYSB finding (self-filmed internet clips are labelled on the PHYSICAL
scale, not on the clip's own stated motion prior) to every other test clip where the inconsistency can be shown
label-free. Test inputs only; no labels (validation is read only for its video ids + question texts, to know which
test rows are validation-overlap = unscored).

    .venv/bin/python research/physb2/build_candidate.py

Base: submissions/trackA_best_p21.csv (includes PHYSB). Output: submissions/trackA_cand_physb2_on_p21.csv (written with
scripts/make_submission.py) and research/physb2/out/log_physb2.csv (one line per changed row).

GATE (fixed before building; a clip is rescaled only if ALL hold):
  G1 identity   - the anchor is the same physical object/person/setup, checked on frames (out/sheets/*.jpg), or a
                  physical constant (g) in a clip whose fps is right;
  G2 evidence   - either ONE exact family fact (a sibling clip's prior states the size of that same object), or TWO
                  independent lines (physics-anchored sibling measurement, regulation / standard object size,
                  physically plausible motion) that agree on the factor;
  G3 magnitude  - |ln k| >= max(0.10, 2 sigma_k), sigma_k from the spread of the anchor and of our own extents;
                  below that, only exact stated-fact rows themselves are set (no rescale);
  G4 rows       - only rows whose base value is our in-clip geometry (method geometry:2d_scale, value equal to the
                  run's geo value) are rescaled; exact family facts are set to the fact; PHYSB rows, stated-fact
                  rows and validation-overlap rows are never touched;
  G5 regime     - only self-filmed clips (annotators had the objects at hand: desk / campus / gym / mug series,
                  internet_0043-0070). Downloaded internet clips (0001-0042, 0073) are labelled in-clip
                  (validation internet clips agree with their in-clip prior), so their priors are left alone.
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
from qp import postprocess as pp  # noqa: E402
from qp.data import load_split, load_validation  # noqa: E402
from qp.mra import item_scores  # noqa: E402

BASE = ROOT / "submissions/trackA_best_p21.csv"
PHYSB = ROOT / "submissions/trackA_cand_internet_physb_on_p8.csv"
P8 = ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv"
RUN = ROOT / "runs/test_v1_high_854/test.csv"
OUTCSV = ROOT / "submissions/trackA_cand_physb2_on_p21.csv"
OUT = ROOT / "research/physb2/out"
OUT.mkdir(parents=True, exist_ok=True)

df = load_split("test").set_index("qid")
base = pd.read_csv(BASE).set_index("id")["parsed_value"]
run = pd.read_csv(RUN).set_index("id")
v = load_validation()
vkeys = {(a, pp.norm_question(b)) for a, b in zip(v.video_id, v.question)}
df["overlap"] = [(a, pp.norm_question(b)) in vkeys for a, b in zip(df.video_id, df.question)]
physb_rows = set((pd.read_csv(PHYSB).set_index("id").parsed_value - pd.read_csv(P8).set_index("id").parsed_value)
                 .pipe(lambda s: s[s.abs() > 1e-12]).index)


def rows(vid: str, pat: str = "") -> list[int]:
    return [q for q in df.index[df.video_id == vid] if re.search(pat, df.question[q], re.I)]


def one(vid: str, pat: str) -> int:
    r = rows(vid, pat)
    assert len(r) == 1, (vid, pat, r)
    return r[0]


def gmean(x) -> float:
    return float(np.exp(np.mean(np.log(np.asarray(x, float)))))


def sd_log(x) -> float:
    x = np.log(np.asarray(x, float))
    return float(np.std(x, ddof=1)) if len(x) > 1 else 0.0


# ----------------------------------------------------------------------------------------------- clip factors
CLIPS: list[dict] = []

# internet_0055: the "walking person" is the scooter rider of 0049-0056 (same cap, white top, khaki trousers; frames).
band = ["internet_0049", "internet_0050", "internet_0052", "internet_0056"]          # rider height in-clip, untouched
rider = [base[one(b, r"height of the person riding scooter")] for b in band]
anchor = float(np.median(rider))
q = one("internet_0055", r"height of the walking person")
ext_px = [115.0, 126.0, 134.0]       # her extents in the record (sent-frame px, frames 0/20/49): walking-pose noise
k = anchor / base[q]
CLIPS.append(dict(
    vid="internet_0055", k=k, sigma=float(np.hypot(sd_log(rider) / np.sqrt(len(rider)), sd_log(ext_px) / np.sqrt(3))),
    fact={q: anchor},
    lines=[f"family: same rider as 0049/0050/0052/0056, in-clip heights {np.round(rider, 3).tolist()} -> {anchor:.3f} m "
           f"(PHYSB anchor, leaderboard-confirmed); 0055 reads {base[q]:.3f} m under 'scooter speed 1.95 m/s'",
           f"physics: walking at {1.95 * k:.2f} m/s after rescale (adult walking 1.2-1.5) vs 1.95 m/s stated; "
           f"she covers ~0.89 body heights/s, i.e. 1.44 m/s at 1.62 m",
           f"standards: DO NOT ENTER {base[3152]:.2f} x {base[3153]:.2f} m -> {base[3152] * k:.2f} x {base[3153] * k:.2f} "
           f"(MUTCD R5-1 30/36 in = 0.76/0.91 m); YIELD width {base[3158]:.2f} -> {base[3158] * k:.2f} (30 in = 0.76)"]))

# internet_0069: same mug, same string-pull desk setup as internet_0046, whose prior states 'height of the cup = 10.5 cm'
q = one("internet_0069", r"height of the cup")
assert "height of the cup = 10.5 cm" in df.prior[df.video_id == "internet_0046"].iloc[0]
cup_px = {"0046 (prior)": [253, 254, 254], "0069": [248, 242, 246, 250]}
k = 10.5 / base[q]
CLIPS.append(dict(
    vid="internet_0069", k=k, sigma=sd_log(cup_px["0069"]) / np.sqrt(4) + 0.02, fact={q: 10.5},
    lines=[f"exact family fact: internet_0046 states the cup height 10.5 cm; 0069 reads {base[q]:.2f} cm under "
           f"'acceleration 0.32 m/s^2 over 2.0-2.3 s' (a 0.3 s window)",
           f"same camera geometry: cup is {np.mean(cup_px['0046 (prior)']):.0f} px tall in 0046 and "
           f"{np.mean(cup_px['0069']):.0f} px in 0069 (sent frames), so the mug is not a different size"]))

# internet_0045: same desk as 0043/0044. 0044 is gravity-anchored (physics); rigid objects shared with 0045.
pairs = [(r"height of the green bottle", r"height of the green bottle"),
         (r"height of the plastic bottle", r"height of the plastic bottle"),
         (r"height of the plate", r"height of the plate")]
rat = [base[one("internet_0044", a)] / base[one("internet_0045", b)] for a, b in pairs]
dist_ratio = base[one("internet_0044", "kettle and the plate")] / base[one("internet_0045", "kettle and the plate")]
k = float(np.median(rat))
CLIPS.append(dict(
    vid="internet_0045", k=k, sigma=float(np.hypot(sd_log(rat), 0.03)), fact={},
    lines=[f"physics-anchored sibling: 0044 (g = 9.8) vs 0045 (cylinder 107.3 cm/s) on the same green bottle, plastic "
           f"bottle and plate: ratios {np.round(rat, 3).tolist()}; pixel check: 0045 is zoomed in 11% (bottle 254 vs "
           f"229 px) yet its in-clip cm/px is 6% larger (0.136 vs 0.128), i.e. k = 0.128/1.11/0.136 = 0.85",
           f"anchor is physical: 0044 reads the ping-pong ball {base[3074]:.2f} cm (regulation 4.0) and the 500 ml PET "
           f"tea bottle {base[3078]:.1f} cm (typical 21-23); 0045's bottle {base[3086]:.1f} cm is not",
           f"kettle-plate distance ratio {dist_ratio:.3f} is not a scale line: the layout changed (cylinder removed, "
           f"kettle moved: 440 px apart in 0045 vs 454 px in 0044 at 11% more zoom)"]))

# internet_0047: overhead gym floor; same ball, lines and camera as 0065/0066. Basketball in the gravity clips of
# the same gym/person (0048 wall pads, 0059, 0064): physics-anchored diameters.
fam = {vid: base[one(vid, r"diameter of the ball")] for vid in ("internet_0048", "internet_0059", "internet_0064")}
anchor = gmean(list(fam.values()))
q = one("internet_0047", r"diameter of the rolling ball")
k = anchor / base[q]
CLIPS.append(dict(
    vid="internet_0047", k=k, sigma=float(np.hypot(sd_log(list(fam.values())) / np.sqrt(3), 0.03)), fact={},
    lines=[f"physics-anchored family: the basketball in the same-gym gravity clips reads "
           f"{ {a[-4:]: round(b, 2) for a, b in fam.items()} } cm -> {anchor:.2f} cm; 0047 reads {base[q]:.2f} cm "
           f"(vertical extent, blur-free) under 'ball 2.94 m/s at 0.5 s'",
           "regulation: size-7 basketball 23.8-24.8 cm, size 6 23.0-23.5 cm (k 0.83-0.89); the overhead twins "
           "0065/0066 (prior g, unusable top-down) were answered with a 24 cm ball and give 2.4-2.7 m/s rolls"]))

# exact stated facts only (G3 fails for a rescale): the toy acorn of internet_0067 ('height of the acorn = 8 cm')
FACT_ONLY = {one("internet_0061", r"height of the acorn"): (8.0, "internet_0067 states height of the acorn = 8 cm "
                                                              "(0061 gravity scale reads 8.6: k 0.93 < gate)"),
             one("internet_0068", r"height of the acorn"): (8.0, "internet_0067 states height of the acorn = 8 cm "
                                                              "(0068 accel prior reads 7.82: k 1.02, consistent)")}
assert "height of the acorn = 8 cm" in df.prior[df.video_id == "internet_0067"].iloc[0]

# ----------------------------------------------------------------------------------------------- screening table
SCREEN = [  # clip, prior regime, decision, reason (frames in out/sheets)
    ("internet_0005_segmented", "walking 1.4 m/s (twin of val 0005: 1.25)", "no",
     "downloaded clip (Stockholm metro) -> labels in-clip (G5); twin is SAM-masked, container 24 fps vs dataset 30; "
     "twin scale 0.87x original, but no physical anchor"),
    ("internet_0028", "conveyor 0.5 m/s", "no", "no family/physical anchor (bags only); container 20.5 vs 24 fps"),
    ("internet_0043", "ball 33.38 cm/s", "PHYSB", "already x2.35 (to 0044 alone x2.33: -1%, left)"),
    ("internet_0044", "g", "anchor", "physical by g; ping-pong ball 4.23 cm (4.0)"),
    ("internet_0045", "cylinder 107.3 cm/s", "RESCALE", "see clip table"),
    ("internet_0047", "ball 2.94 m/s", "RESCALE", "see clip table"),
    ("internet_0048/0057-0064", "g", "anchor", "physical by g (0060-0063 already rotated-gravity); no prior to fault"),
    ("internet_0049/0050/0052/0056", "scooter 3.8/2.9/2.91/2.64 m/s", "anchor", "rider 1.58-1.64 m, consistent"),
    ("internet_0051/0053/0054", "scooter 2.07/4.46/4.9 m/s", "PHYSB", "already on the 1.624 m anchor"),
    ("internet_0055", "scooter 1.95 m/s (she walks)", "RESCALE", "see clip table"),
    ("internet_0061", "g", "fact row", "acorn height -> 8 cm (0067); scale left (k 0.93 < gate)"),
    ("internet_0065/0066", "g (top-down, unusable)", "no", "answers already direct with a 24 cm ball = physical"),
    ("internet_0067", "acorn 8 cm", "anchor", "size prior = physical"),
    ("internet_0068", "acorn accel 0.77 m/s^2", "fact row", "acorn 7.82 vs 8 cm: k 1.02 (consistent; fact row only)"),
    ("internet_0069", "cup accel 0.32 m/s^2", "RESCALE", "see clip table"),
    ("internet_0070", "speedboat 11 m/s at 1 s", "no", "one weak line only (wake boat 6.4-7.6 m vs 5.06 read)"),
    ("internet_0001-0042, 0071-0074 (S2)", "stated sizes / lane widths", "no",
     "size priors are the anchor and are physical (credit card, dollar bill, court widths); 0073 conveyor: no anchor"),
    ("simulation_0041(+_segmented) S2", "person 1.75 m (top-down: foreshortened)", "no",
     "family facts read 0.68-0.82 (boat 10 m, 4 m/s) but the fact rows are already set and the non-fact rows "
     "pooled by the family rules; person-speed fact disagrees (0.82 / 0.98) -> fails G2"),
    ("simulation D2 (20 geometry fact rows)", "various", "no", "fact/in-clip median ratio -0.4%, none beyond 15%"),
    ("simulation/captured 3D", "various", "no", "fact mismatches there are direct-answer errors, not scale (no geometry)"),
]

# ----------------------------------------------------------------------------------------------- apply
cur = base.copy()
log = []
clip_rows = []
for c in CLIPS:
    lk = abs(np.log(c["k"]))
    passed = lk >= max(0.10, 2 * c["sigma"])
    clip_rows.append(dict(clip=c["vid"], k=round(c["k"], 4), sigma_log=round(c["sigma"], 4), ln_k=round(np.log(c["k"]), 3),
                          gate=passed, evidence=" | ".join(c["lines"])))
    if not passed:
        continue
    for q in df.index[df.video_id == c["vid"]]:
        if df.overlap[q] or q in physb_rows:
            continue
        if q in c["fact"]:
            new, why = c["fact"][q], "family fact"
        else:
            geo = run.geo_value.get(q)
            if not (str(run.method.get(q, "")).startswith("geometry:2d_scale") and np.isclose(geo, base[q], rtol=1e-6)):
                log.append((q, c["vid"], df.category[q], base[q], base[q], 1.0, "skip: not in-clip geometry"))
                continue
            new, why = base[q] * c["k"], "rescale"
        log.append((q, c["vid"], df.category[q], base[q], new, new / base[q], f"{why} x{c['k']:.4f}"))
        cur[q] = new
for q, (val, why) in FACT_ONLY.items():
    log.append((q, df.video_id[q], df.category[q], base[q], val, val / base[q], "family fact: " + why))
    cur[q] = val

lg = pd.DataFrame(log, columns=["qid", "video_id", "category", "old", "new", "ratio", "rule"])
lg["question"] = df.question.reindex(lg.qid).values
lg.to_csv(OUT / "log_physb2.csv", index=False)
pd.DataFrame(clip_rows).to_csv(OUT / "clips_physb2.csv", index=False)
pd.DataFrame(SCREEN, columns=["clip", "prior", "decision", "reason"]).to_csv(OUT / "screen_physb2.csv", index=False)

with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
    cur.rename("parsed_value").rename_axis("id").reset_index().to_csv(f.name, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), f.name, str(OUTCSV)], check=True)

# ----------------------------------------------------------------------------------------------- checks
cand = pd.read_csv(OUTCSV).set_index("id").parsed_value
tmpl = pd.read_csv(BASE).id
assert list(cand.index) == list(tmpl), "template order changed"
assert np.isfinite(cand).all() and (cand > 0).all()
chg = cand.index[~np.isclose(cand, base.reindex(cand.index), rtol=1e-12)]
assert set(chg) == set(lg.qid[lg.ratio != 1.0]), "unexpected rows changed"
assert not (set(chg) & physb_rows) and not df.overlap[chg].any()

# ----------------------------------------------------------------------------------------------- expected gain
rng = np.random.default_rng(0)
SIG = 0.08          # per-row measurement scatter of a good internet answer (validation internet rows score ~.91)


def exp_item(pred: np.ndarray, truth: np.ndarray, n: int = 4000) -> np.ndarray:
    g = truth[None, :] * np.exp(rng.normal(0, SIG, (n, len(truth))))
    return np.array([item_scores(pred, gi) for gi in g]).mean(axis=0)


n_d2 = int(((df.category == "D2") & ~df.overlap).sum())
n_s2 = int(((df.category == "S2") & ~df.overlap).sum())
ch = lg[lg.ratio != 1.0].copy()
old, new = ch.old.to_numpy(float), ch.new.to_numpy(float)
ch["gain_if_phys"] = exp_item(new, new) - exp_item(old, new)
ch["gain_if_inclip"] = exp_item(new, old) - exp_item(old, old)
ch.to_csv(OUT / "log_physb2.csv", index=False)

# calibration on PHYSB itself (observed D2 +.009 on 29 rows, +-.0005 rounding)
pb = pd.read_csv(ROOT / "research/internet/out/log_physb.csv")
po = pb.note.str.extract(r"^([\d.e+-]+) -> ([\d.e+-]+)").astype(float).to_numpy()
cal_phys = float((exp_item(po[:, 1], po[:, 1]) - exp_item(po[:, 0], po[:, 1])).sum())
cal_in = float((exp_item(po[:, 1], po[:, 0]) - exp_item(po[:, 0], po[:, 0])).sum())

pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 200)
print(f"scored rows: D2 {n_d2}, S2 {n_s2}; PHYSB observed +.009 D2 = {0.009 * n_d2:.1f} item pts "
      f"(range {0.0085 * n_d2:.1f}-{0.0095 * n_d2:.1f}); model: all-physical {cal_phys:+.1f}, all-in-clip {cal_in:+.1f}")
print("\nclip table\n" + pd.DataFrame(clip_rows).drop(columns="evidence").to_string(index=False))
for c in clip_rows:
    print(f"\n{c['clip']}: k={c['k']} (ln {c['ln_k']}, sigma {c['sigma_log']}, gate {'PASS' if c['gate'] else 'FAIL'})")
    for line in c["evidence"].split(" | "):
        print("   -", line)
print("\nchanged rows")
print(ch[["qid", "video_id", "category", "old", "new", "ratio", "rule", "gain_if_phys", "gain_if_inclip"]]
      .round(4).to_string(index=False))
by = ch.groupby("video_id").agg(rows=("qid", "size"), k=("ratio", "median"), phys=("gain_if_phys", "sum"),
                                inclip=("gain_if_inclip", "sum"))
print("\nper clip (item points)\n" + by.round(2).to_string())
for cat, n in (("D2", n_d2), ("S2", n_s2)):
    s = ch[ch.category == cat]
    if len(s):
        print(f"{cat}: {len(s)} rows; expected {cat} {s.gain_if_phys.sum() / n:+.4f} if physical, "
              f"{s.gain_if_inclip.sum() / n:+.4f} if in-clip; overall MRA /4")
print("\nscreen\n" + pd.DataFrame(SCREEN, columns=["clip", "prior", "decision", "reason"]).to_string(index=False))
