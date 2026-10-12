"""Adversarial check of research/labdist and the verified candidate (research/verify_labdist).

Validation labels are read only in the evaluation block (render-type table, R1 premise); nothing derived from them
sets a test answer. The verified candidate = labdist emu minus R2 on 2891 (0054bx soccer-ball displacement):
R3 trusts 0054bx because its soccer ball has boxes (depth follows the looming) while 0054b's does not, and the
same reason makes 0054b's 0.446 suspect for the 1.0-1.4 s displacement; probe 8's 0054bs value 0.444 is already a
copy of 0054b (its own raw geometry is 0.392, like 0054bx's 0.383), so the "family median" is one measurement twice.

    python research/verify_labdist/verify.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "research/labdist"))
from backproject import dist  # noqa: E402
from qp.mra import item_scores  # noqa: E402

BASE = ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv"
TEMPLATE = ROOT / "data/submission_template/quantiphy_submission_template.csv"
DROP = {2891: "R2 contradicts R3: 0054b soccer depth is the 2.0 s entry; 0054bs/bx looming geometry 0.39"}


def family(v):
    return re.sub(r"(captured_\d+[ab]?)[sxX]?$", r"\1", v)


def check(path, base, t):
    c = pd.read_csv(path)
    ok = (len(c) == 3289 and (c.id.values == t.id.values).all() and np.isfinite(c.parsed_value).all()
          and (c.parsed_value > 0).all())
    d = ~np.isclose(c.parsed_value.values, base.parsed_value.values, rtol=1e-9)
    cats = (t.inference_type.str[0] + t.video_type.str[1])[d].value_counts().to_dict()
    print(f"{path.name}: ok={ok} rows differ={int(d.sum())} {cats}")
    return set(c.id[d])


def render_table(t):
    """Validation (evaluation only): direct-answer item score by render type over every validation lab question."""
    val = pd.read_csv(ROOT / "data/QuantiPhy-validation/validation_dataset.csv")
    raw = pd.read_csv(ROOT / "runs/test_v1_high_854/test.csv").set_index("id")
    t = t.assign(direct=t.id.map(raw.direct_value), fam=t.video_id.map(family),
                 qn=t.question.str.strip().str.lower())
    rows = []
    for _, r in val[val.video_source == "lab"].iterrows():
        g = t[(t.fam == family(r.video_id)) & (t.qn == r.question.strip().lower())]
        for _, x in g.iterrows():
            rows.append(dict(fam=x.fam, typ=x.video_id[-1] if x.video_id[-1] in "sx" else "o",
                             own=x.video_id == r.video_id, lab=r.ground_truth_posterior, direct=x.direct))
    e = pd.DataFrame(rows).dropna()
    e["s"] = item_scores(e.direct, e["lab"])
    print("validation direct-answer score by render type (6 families):")
    print(e.pivot_table(index="fam", columns="typ", values="s").round(3).to_string())
    print(e.groupby("typ").s.agg(["mean", "count"]).round(3).to_string())
    # R1 premise, clustered by validation clip (4 s/x clips)
    own = e[e.own & (e.typ != "o")]
    cl = []
    for f, g in own.groupby("fam"):
        o = e[(e.fam == f) & (e.typ == "o")]
        cl.append(o.s.mean() - g.s.mean())
    rng = np.random.default_rng(0)
    boot = [np.mean(rng.choice(cl, len(cl))) for _ in range(4000)]
    print(f"R1 premise by clip: {np.round(cl, 3).tolist()}; clustered 90% CI [{np.percentile(boot, 5):+.3f}, "
          f"{np.percentile(boot, 95):+.3f}]")


def label_free_checks():
    # 0018 people: the pipeline put both people at the soccer ball's 2.8 m; stated near 2.002 / far 3.130 m
    a, b = (382, 375), (989, 405)   # left (far, 405 px tall) and right (near, 614 px) person clicks
    print(f"0018 two people: stated depths range {100 * dist((*a, 3.130), (*b, 2.002)):.0f} cm, Z "
          f"{100 * dist((*a, 3.130), (*b, 2.002), z=True):.0f} cm, both 2.8 m {100 * dist((*a, 2.8), (*b, 2.8)):.0f} cm "
          f"(p8 230 / 249 / 229; R1 sets 0018s 249 -> 230)")
    # 0009 bounce timing: contact frame 38, apex frame 46 at 24 fps
    T = 8 / 24
    print(f"0009 rebound timing: rise {0.5 * 9.8 * T ** 2:.3f} m (emulated apex-to-floor 0.646 - radius 0.116 = 0.530)")


def main():
    t = pd.read_csv(TEMPLATE)
    base = pd.read_csv(BASE)
    for n in ("fam", "emu"):
        check(ROOT / f"submissions/trackA_cand_labdist_{n}_on_p8.csv", base, t)
    render_table(t)
    label_free_checks()
    emu = pd.read_csv(ROOT / "submissions/trackA_cand_labdist_emu_on_p8.csv").set_index("id").parsed_value
    b = base.set_index("id").parsed_value
    out = emu.copy()
    for q, why in DROP.items():
        print(f"revert {q}: {emu[q]:g} -> {b[q]:g} ({why})")
        out[q] = b[q]
    tmp = HERE / "_tmp_verified.csv"
    pd.DataFrame({"id": out.index, "parsed_value": out.values}).to_csv(tmp, index=False)
    dst = ROOT / "submissions/trackA_cand_labdist_verified_on_p8.csv"
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), str(tmp), str(dst)], check=True)
    tmp.unlink()
    ch = check(dst, base, t)
    emu_ch = check(ROOT / "submissions/trackA_cand_labdist_emu_on_p8.csv", base, t)
    print("verified = emu minus", sorted(emu_ch - ch))


if __name__ == "__main__":
    main()
