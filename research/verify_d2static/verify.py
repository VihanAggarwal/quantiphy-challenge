"""Adversarial check of research/d2static (rotated-gravity candidate) and the verified rebuild.

1. Integrity of submissions/trackA_cand_d2static_rotgrav_on_p8.csv vs probe 8 (rows, order, finite, diff set).
2. Re-solve internet_0060-0063 with rotated tracks (d2static/rotated_gravity.py), with and without the internet
   forward-difference speed convention (research/internet/fwd_emulate.py hook, paper App. D.3).
3. Verified candidates (test inputs only; no validation labels):
   - verified:     rotgrav minus qid 3196 (acorn height; the internet family candidate sets it to the 8 cm stated in
                   internet_0067 - a stated-fact row in any composed upload, so rotgrav must not touch it).
   - verified_fwd: verified + forward-difference velocities on the 6 'velocity at t' rows (internet convention).
"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research/d2static")); sys.path.insert(0, str(ROOT / "scripts"))
import qp.geometry as G  # noqa: E402
from qp.data import load_split  # noqa: E402
import rotated_gravity as RG  # noqa: E402

OUT = ROOT / "research/verify_d2static/out"
BASE = ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv"
CAND = ROOT / "submissions/trackA_cand_d2static_rotgrav_on_p8.csv"
TEMPLATE = ROOT / "data/submission_template/quantiphy_submission_template.csv"
PROTECT = {3196: "acorn height: stated 8 cm in internet_0067 (internet_fam / internet_main set 8.0)"}

# --- 1. integrity
b = pd.read_csv(BASE); c = pd.read_csv(CAND); t = pd.read_csv(TEMPLATE)
assert len(c) == 3289 and (c.id.values == t.id.values).all() and (c.id.values == b.id.values).all()
assert np.isfinite(c.parsed_value).all() and (c.parsed_value > 0).all()
diff = c.id[~np.isclose(c.parsed_value, b.parsed_value, rtol=1e-9)].tolist()
print("rotgrav: 3289 rows in template order, finite>0; changed", len(diff), "ids", min(diff), "-", max(diff))

# --- 2. re-solve, plain (central/ICI) and forward-difference speeds
def fwd(fit, t0, fps, cols, n):
    if n != 1:
        return None
    i = int(round(t0 * fps)); ts = np.array([i, i + 1]) / fps - t0
    pts = np.column_stack([np.polyval(fit[7][:, j], ts) for j in cols])
    return [float(np.linalg.norm(pts[1] - pts[0]) * fps)]

res = RG.run(RG.ROTATED)
orig_solve, orig_emu = G.solve, G._emu_speeds
RG.solve = lambda spec, *a, **kw: orig_solve(spec, *a, label_emulation=True, **kw)
G._emu_speeds = fwd
try:
    res_f = RG.run(RG.ROTATED)
finally:
    RG.solve, G._emu_speeds = orig_solve, orig_emu
res["rot_fwd"] = res_f.rot.values; res["fwd_flags"] = res_f.rot_flags.values
old = pd.read_csv(ROOT / "research/d2static/out/rotated_gravity.csv")
assert np.allclose(old.rot, res.rot, rtol=1e-9), "rotated_gravity.csv not reproduced"
res.to_csv(OUT / "resolve.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 55)
print(res[["qid", "video_id", "question", "direct", "rot", "rot_fwd", "fwd_flags"]].round(4).to_string(index=False))

# --- 3. verified candidates
base = b.set_index("id").parsed_value
cats = load_split("test").set_index("qid").category
def build(name, col):
    new = base.copy(); log = []
    for r in res.itertuples():
        if r.qid in PROTECT:
            log.append(f"{r.qid} keep {base[r.qid]:.4g}: {PROTECT[r.qid]}"); continue
        v = getattr(r, col)
        if not (np.isfinite(v) and v > 0):
            continue
        new[r.qid] = v; log.append(f"{r.qid} {base[r.qid]:.4g} -> {v:.4g} ({v / base[r.qid]:.3f})")
    out = ROOT / f"submissions/trackA_cand_d2static_{name}_on_p8.csv"
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
        new.rename("parsed_value").rename_axis("id").reset_index().to_csv(f.name, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), f.name, str(out)], check=True)
    cc = pd.read_csv(out)
    assert len(cc) == 3289 and (cc.id.values == t.id.values).all() and np.isfinite(cc.parsed_value).all() and (cc.parsed_value > 0).all()
    ch = cc.id[~np.isclose(cc.parsed_value, b.parsed_value, rtol=1e-9)]
    print(name, "changed", len(ch), cats[ch].value_counts().to_dict(), "ids", sorted(set(ch) - set(res.qid)) or "only 0060-0063")
    (OUT / f"log_{name}.txt").write_text("\n".join(log) + "\n")
    return cc

build("verified", "rot")
build("verified_fwd", "rot_fwd")
