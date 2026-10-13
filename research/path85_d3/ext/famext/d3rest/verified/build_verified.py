"""Verifier corrections to the d3rest variants (D3 only; built on probe 5).

Takes the investigator's rebuilt CSVs (byte-identical to ext/d3rest/D3ext_*.csv) and reverts to probe 5 the P/P_RE rows
the review rejected. Decisions use test inputs only (frames, depth_info, cached direct/geometry answers); no labels.

Rejected (reverted to probe 5):
  1089  sim_0017 'height of the freestanding art display panel' P 0.62 -> 1.96: pooled with 0015/0019, whose depth_info
        names 'the NEAREST freestanding art display panel' at 11-12 m (several panels exist); in 0017 and its twin 0017_seg
        both direct (0.62/0.71) and geometry (0.70/0.73) measure the 0017 panel at ~0.7 m, and the twin row 1658 stays
        0.71, so the pool mixes two panel instances and the row would disagree with its own twin.
  1680 1681 1682 1731 1732 1733 1734  beach-rock rows pooled across the new 0038_seg~0043_seg merge: the values are
        bimodal by camera view (top-down 0038_seg/0043/0044: width 22-25, length 28, direct and geometry agree, scale
        anchored by stated boat/eagle; water-level 0022_seg/0037_seg: height 3.7-4.3; oblique 0024/0027/0028: width 8-10,
        height 7-9), and the geometric median lands between the clusters (width 13.35, length 19.36, height 7.2), moving
        each clip away from the dimension its own view observes best. Revert all rock rows touched by the merge.
  1583  sim_0206 'length of the letter placed under the gun' P 0.17 -> 0.2588: the equivalence group is split by a
        parse artifact ('letter under the gun' 0203/0207/0206 vs 'letter' 0204/0208/0209); the same-camera clip 0209
        (identical depth_info) keeps 0.15 for the same letter, and the full 6-clip set is bimodal (0.15-0.17 vs 0.26).
"""
import numpy as np, pandas as pd
SP = '/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
E = SP + '/ext/d3rest'; V = E + '/verified'; R = '/home/user/quantiphy-challenge'
REJECT = {1089: 'panel instance mix', 1680: 'rock view mix', 1681: 'rock view mix', 1682: 'rock view mix',
          1731: 'rock view mix', 1732: 'rock view mix', 1733: 'rock view mix', 1734: 'rock view mix',
          1583: 'split letter group'}
P5 = pd.read_csv(R + '/submissions/trackA_probe5_families_merged.csv')
tm = pd.read_csv(R + '/data/submission_template/quantiphy_submission_template.csv')
cat = (tm.inference_type.str[0] + tm.video_type.str[1]).values
p5 = dict(zip(P5.id, P5.parsed_value))
out = {}
for name in ('B_TP', 'C_TP_KOBJ_HUMAN'):
    src = pd.read_csv(V + f'/rebuild/D3ext_{name}.csv')
    assert list(src.id) == list(tm.id)
    v = src.parsed_value.astype(float).values.copy()
    for i, q in enumerate(src.id):
        if q in REJECT: v[i] = p5[q]
    o = pd.DataFrame({'id': src.id, 'parsed_value': v})
    pv = o.parsed_value.values
    assert len(o) == 3289 and np.isfinite(pv).all() and (pv > 0).all()
    ch = pv != P5.parsed_value.values
    assert set(cat[ch]) <= {'D3'}
    path = V + f'/D3ext_{name}_verified.csv'
    o.to_csv(path, index=False)
    out[name] = dict(csv=path, rows_changed=int(ch.sum()), reverted=sorted(q for q in REJECT if q in set(src.id[src.parsed_value.values != P5.parsed_value.values])),
                     median_ratio=float(np.median(pv[ch] / P5.parsed_value.values[ch])))
    print(name, out[name])
