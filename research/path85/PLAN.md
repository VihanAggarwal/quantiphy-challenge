# Path to .85: synthesis and plan (2026-10-13, workflow wf_697c11d5-4f2)

Base: `submissions/trackA_cand_physb2_on_p21.csv` = .811 (S2 .817, D2 .859, S3 .766, D3 .803).
Leaderboard (Oct 12 21:00 UTC): 1 Perch AI .8517, 2 Cogworks RSI .8498, 3 Blindfolded .8293, 4 iMak .8231,
5 szerlok .8195. We show as .8083 until the next board refresh.

**Bottom line.** Six studies, a web sweep and adversarial verification found no lever worth +.005 on its own. The
levers that survived add up to about **+.003**, which should put us near **.814** on the leaderboard.
- If the user allows the paper's Table 6 prop sizes, add about +.0027.
- The U1-U4 method-switch and emulator rungs (built, not yet read) could add 0 to +.002.
- Realistic final score: **.813-.819**. Top 5 is about a 15-25% chance; .85 is under 2%.

The leaders are about .04 better on the validation videos as well (about .87 vs our .828). So the gap is a better
base predictor everywhere, not a trick we are missing (see section 4).

---

## 1. Levers that survived verification, and the combined candidate

"Survived" means not refuted and no rule violation once the noted fix is applied. Gains are verifier-adjusted
overall MRA gains: item gain x rows / (4 x N_category).

| # | Lever | Cat. | Rows (scored) | Adjusted gain | Source file (built on physb2) |
|---|---|---|---|---|---|
| 1 | **S2 simulation package minus qid 1874** | S2, D2 | S2 23, D2 28 | **+.0025** (range +.002 to +.0031) | `trackA_cand_s2all_on_physb2.csv` (1874 reverted in the combo) |
| 1a | Bird family 0088-0091: speeds stated by sibling clips anchor the scale; extents from sky masks | S2, D2 | S2 5, D2 14 | +.0015 | `trackA_cand_s2birdfam_on_physb2.csv` |
| 1b | Event and frame-edge fixes (0121 collision, 0253 corner entry) plus extrapolation past the end of the track | S2 | 10 (11 minus 1874) | +.0014 | `trackA_cand_s2events_on_physb2.csv` (contains 1874; do not upload as is) |
| 1c | Name-family stated facts, guarded to 0.8-1.25x | S2, D2 | S2 8, D2 14 | +.0002 | `trackA_cand_s2namefam_on_physb2.csv` |
| 2 | D3 family re-pool on the 3-run ensemble (fixes the probe-7a run-1 artefact) | D3 | 207 (201) | +.0005 to +.001 | `trackA_cand_d3repool_on_physb2.csv` |
| 3 | Lab motion: `is_stated()` unit bug (40 cm path protected by a "40mm" prior) plus pooling the 0034a/b cameras | S3 | 24 (20) | +.0006 | `trackA_cand_labmot_on_physb2.csv` |
| 4 | Teal-notebook pool (NBpool): 0023/0024 width and length = median of our own 0013/0014(/0023/0024) answers. Uses no Table-6 value. | D3 | 10 | +.0004 (range 0 to +.0007) | rows `rule=NBpool` of `trackA_cand_labT6_on_physb2.csv` |
| 5 | Internet micro-fixes: credit-card typo in 0040; one gym basketball pooled across 0048/0059/0064 | S2, D2 | S2 1, D2 3 | +.0001 | `trackA_cand_inet_micro_on_physb2.csv` |

**Rule fix applied: qid 1874 is reverted.** It is simulation_0171_segmented, speed at 0.5 s; the lever changed it from
2.088 to 1.67. Two verifiers (s2events, s2all) found that `conv_0171.py` / `conv2_0171.py` hard-code the 0171
validation labels, and the per-frame operator was kept only at the time where it matched the label. The event screen
does not flag 1874 itself. Reverting costs about .00014.

### Combined candidate: `submissions/trackA_cand_path85_combo.csv`
- **Build:** `research/path85/build_combo.py` writes the file through `scripts/make_submission.py`. No API calls; the
  env was nulled anyway. The per-row change log is `research/path85/changes_combo.csv`.
- **Checks passed:**
  - 3289 rows in template order with unique ids.
  - All 3289 answers are finite and > 0.
  - No conflicting row edits between levers.
- **What changed vs physb2:** 296 rows (S2 24, D2 31, S3 24, D3 217).
  - Scored: S2 24, D2 31, S3 20, D3 211. Test 137 and 138 (bird wingspan) are probably "reviewed equivalent" overlaps
    and unscored.
  - The 10 changed rows that are exact validation overlaps are all unscored (labmot 4, d3repool 6).
  - No changed row equals a validation label.
  - No stated-fact row is touched (verifiers ran `apply_rules` on facts, motionfam, freefall and labfacts).
- **Relation to U5.** It equals `trackA_u5_s2all_d2all_s3labmot_d3repool.csv` except qid 1874 (reverted) and the 10
  NBpool rows (added). The build asserts this. **Upload the combo instead of U5.** U5 still contains 1874.
- **Validation overlap rows, report only.** n=128, partly in-sample (0089 birds, 0034as), so this is not evidence:
  macro .8276 to .8334; 7 rows change score, +0.9 items; clustered 90% CI [+.000, +.017].
- **Expected leaderboard read vs physb2:**

  | Category | Expected change |
  |---|---|
  | S2 | +.006 to +.011 |
  | D2 | about +.001 |
  | S3 | +.001 to +.003 |
  | D3 | +.002 to +.005 |
  | **Overall** | **about +.003** (range +.0015 to +.0045), i.e. about .814 |

- **Decision rule.** Adopt the combo as the new base if overall is at least .811. If S2 rises by less than .004, the
  0121/0253 physics readings are the suspects. Then split by mechanism (events+extrapolation, 10 rows, vs bird+namefam,
  18 rows). Avoid reads of 5 rows or fewer.

### Row overlaps with the other built uploads (relative to physb2)

| Upload | Rows shared with the combo | Rule when composing |
|---|---|---|
| U1 | D2 7 (bird lengths), S3 16 (labmot) | D2: keep the combo values. S3: if U1 S3 sz4 wins, re-run `research/path85_lab/build_labmot.py` with the sz4 factors. |
| U2 | S2 10 (events, extrapolation, bird speeds), D2 3 (inet_micro), S3 9 (labmot) | Keep the combo values. If U2 S3 nopath wins, rebuild labmot without the path factor. |
| U3 / U4 | D3 5 (NBpool) | Keep NBpool. |
| U6 | its S2 slot = s2events including 1874 | Do not upload U6 as built. |
| U7 | its S2/D2 slots = birdfam, already in the combo | Do not upload U7 as built. |
| d2sizeenv, s3p, labsize_x097, d3simmot_x1035, sim3d_noguard | none | Can be read on top of the combo. |

Compose winners with
`python research/merge/merge_skip.py OUT submissions/trackA_cand_path85_combo.csv submissions/trackA_cand_physb2_on_p21.csv <winner>:<cats> ...`.
`merge_skip` keeps the combo's value wherever the combo already differs from physb2.

### Not refuted, but blocked by policy: Table 6 prop sizes (needs the user's decision)
- **What it is.** `trackA_cand_labT6_on_physb2.csv` (T6A 121 rows, T6B 33) sets lab prop sizes to the paper's App.
  Table 6 values.
- **Evidence.** 11/11 validation lab size labels equal Table 6, and 5/5 stated lab size priors on test do too
  (independent of validation).
- **Gain:** adjusted +.0022 to +.0027 overall (S3 about +.004, D3 about +.007).
- **Why it is blocked.** `research/gemini/HANDOFF.md` says "Do not use the prop sizes from the paper's Table 6", and
  the strategy verifier flagged it. The official rules have no clause on external data; it is in effect a lookup of
  the labels' source.
- **Other risks.** The notebook was excluded after its validation label (10.8) disagreed with Table 6's 8.8, so the
  honest count is 11 of 12. Tier B depends on judging the prop's identity from frames.
- **If approved:** `.venv/bin/python research/path85/build_combo.py --t6` writes `trackA_cand_path85_combo_T6.csv`
  (not built). Read its S3/D3 change against the combo.

### Built by the strategy agent and not verified: hedges to read on the leaderboard
These are not in the combo.

| Candidate | Cat. (rows) | Prior | Note |
|---|---|---|---|
| `trackA_cand_d2sizeenv_on_physb2.csv` | D2 (60) | +.0003 | The S2 sibling won +.002 S2 in probe 18. |
| `trackA_cand_s3p_on_physb2.csv` | S3 (42) | +.0003, low | 13 rows overlap U4's S3 lab static switch. Moot if Table 6 is approved (30 shared rows). |
| `trackA_cand_labsize_x097_on_physb2.csv` | D3 (71) | +.0002, low | First rung of a lab size-scale ladder; 8 rows overlap U3/U4. |
| `trackA_cand_d3simmot_x1035_on_physb2.csv` | D3 (42) | +.00015 | Below resolution; bundle it. |
| `trackA_cand_s3floorsplit_on_path85lab.csv` | S3 (69) | +.001, low, in-sample | Upload only after the U1/U3 reads. Built on path85lab, which includes Table 6, so rebuild it if Table 6 is refused. |
| `trackA_cand_sim3d_noguard_on_physb2.csv` | S3 (5) | coin flip, +-.0015 | **Not recommended.** It is the contested beach-person 1.3 m/s; two agents declined it, and a 5-row isolated read effectively reveals those labels. |

---

## 2. Refuted and dead ends, with reasons

### Rule problems
- **qid 1874** (0171_segmented, per-frame speed operator): selected against the 0171 validation label. Reverted.
- **Table 6:** blocked by policy (above), not refuted.
- **0041 ball-to-person distance:** deliberately not investigated, because the only reason to look was its validation
  label.

### S2 simulation (`research/path85_s2sim`)
- **Per-frame (Blender) acceleration emulation:** about 4.9 m/s² of pixel-quantisation noise; any gain is noise
  fitting.
- **Tangential acceleration:** probe 11's -.002 is explained by the paper airplanes. Stated priors are keyframed
  constants, so keep |a|.
- **Global per-frame speed operator:** it wins only at events (0171 at 0.5 s) and loses elsewhere (3 s). Use it only
  where an event is detected.
- **Max-extent for articulated size targets:** mixed (bird wingspan = max; shark height < median).
- **Raccoon family 0274-0277:** the masks disagree across views.
- **Pooling repeated S2 questions:** the large spreads are genuinely different events.
- **Twin geometric mean:** the copy direction is already right (validation 27.1 vs 24.8).
- **Duplicated-first-frame time offset:** inconclusive, at most 1-4%.
- **Frame-edge truncation:** rare; only 0253 qualifies.
- **0082-0084, 0224, 0153, 0012:** ambiguous or different events.

### S2/D2 internet (`research/path85_internet`)
No label-free lever worth more than about +.001 exists.
- **Small priors:** 9 S2 clips have priors under 40 px, so 1 px is a 3-11% scale error. This is measurement noise.
- **PHYSB analog for S2 size priors:** 14 standard objects give median |ln k| .014. No bias.
- **Container fps:** dataset fps confirmed on 0027 and 0019.
- **Twin fps, physical-anchor rescale of D2 gravity clips:** sd .047, no shared bias.
- **0070 wakeboard boat:** coin flip.
- **Switching S2 internet to direct:** direct is about equal to geometry; only 8 acceleration rows disagree.
- **Also dead:** longest-extent rule on deformable priors (coin flip), bathroom series (2 rows), 0067 acorn (pulled
  on a string, not falling), credit-card short side.

### S3/D3 simulation (`research/path85_s3sim`)
- **Diagnosis:** the remaining misses are definitional (pier deck 0.5 vs 0.26, pedestal 1.01 vs 0.6, lane 6 vs 11.8).
  Every view and the geometry share them. Scale, focal length, triangulation or pooling cannot fix them.
- **Size-from-depth-ratio estimator:** -.104 per row (CI [-.172, -.050]).
- **Multi-view consensus K:** its gains are all in clips that already have a fact-based K; elsewhere it picks up
  artefacts.
- **Cross-camera radial bound:** at most 3 rows.
- **Full triangulation:** the camera-rich families are already fact-saturated.
- **Per-kind bias:** none.
- **Foreshortening factor:** a real -3% to -13% bias on lengths, but correcting it loses (MRA punishes overestimates).
- **K variants:** none beat the current K.
- **Contested 1.3 m/s person speed:** coin flip.
- **0150/0151 pooling:** about 0.

### Lab (`research/path85_lab`)
- **f audit:** the pipeline's f (703-716) is already right.
- **Range vs Z:** unresolved, so no lever.
- **Render ensemble of direct answers:** -.034 (CI [-.072, -.005]).
- **Per-class method switch:** loses to the pooled answers.
- **0054a/b pooling:** the balls bounce and the depth_info is copied.
- **Reverting the emulator on table-top events:** hurts on 2 of 2 rows.
- **Table-6 notebook:** contradicted (10.8 vs 8.8).
- **Poker tower:** within the 5% bracket.
- **D3 mid-ball inflation:** only the in-sample 0061.
- **0018 at t = 3.0-3.4 s:** unanswerable (the clip is 2.04 s).
- **To do:** fix the `is_stated()` bug at the source in `research/labnoise/build_candidate.py` (compare in SI units)
  before any further ladder build.

### D3 families (`research/path85_d3`)
- **Coverage is saturated.** Every applicable fact is already applied. Moving all 124 scored raw-ensemble rows from
  .78 to .90 would add only about +.004.
- **Pooling variants:** run-level votes -.008, trimmed mean -.005, twin pooling -.004, S-vote weighting and 2-base
  pools inconclusive.
- **Cross-family asset transfer:** 0 of 3 exact.
- **New link types:** reach 5 rows or fewer.
- **Fall onset:** already right.
- **KOBJ recomputed on the ensemble:** worse.

### Strategy (`research/path85_strategy`)
- **Per-subset method switching beyond U1-U4:** exhausted; the sum of positive point estimates is +.0007 and every CI
  includes 0.
- **Geometry on 3D simulation:** loses in every stratum.
- **Other 3-run aggregates and twin averaging:** lose.
- **Uniform bias ladders:** only D3 sim motion (-3.5%) survives, and it is sub-resolution.
- **Validation as judge of method switches:** too few videos, and the base is in-sample.
- **Per-row or per-video leaderboard routing:** ruled out, because it extracts labels.

### Literature (web)
- **Test-time correction of a frozen model from rescaled priors** (EquiSD): -4.7 MRA.
- **Answer trust selection** (ATS): +.002 at partial coverage only.
- **Self-consistency and longer thinking:** saturated.
- **WildDet3D boxes** (14% median error) **and Orient Anything V2** (15-37° error): too coarse.
- **Single-image FOV:** already rejected in `research/simfov`.

---

## 3. Research leads on the top teams, and open leads

### Top teams: nothing public before the deadline
- **No method information anywhere** for the seven leading teams (paper, code, Hugging Face, X, LinkedIn, Discord).
  - Rules: the Track A top 3 must publish a reproducibility package within 14 days of the deadline; technical
    summaries come in November. https://quantiphy.stanford.edu/competition/
  - Weak, unconfirmed link: Perch AI may be https://perchai.app (a multi-model agent product); nothing ties it to
    QuantiPhy. https://github.com/szerlok has no public QuantiPhy repo.
- **What can be inferred.** Perch and Cogworks did not copy validation answers: their drop when overlap rows were
  removed implies about +.017 on the overlap rows, the same lift as ours. Blindfolded did copy them (about 1.0 on
  overlap rows), so its real level is .8293.
  - The leaders therefore score about .87 on the validation videos against our .828.
  - Track B suggests that open weights alone reach about .80 (IIIXR .8051, JX .7829 vs .8114 in Track A). Perch's own
    Track B entry is .68, so its lead comes from a closed frontier model plus a pipeline we cannot see.
- **Worth watching:**
  1. The board refreshes at 09:00 and 21:00 UTC; snapshot format is in
     `research/webintel/leaderboard_snapshot_2026-10-12T2100Z.json`. Watch for jumps; szerlok gained +.018 in a day.
  2. Open GitHub issue #6 on lab back-projection intrinsics: https://github.com/Paulineli/QuantiPhy/issues/6
  3. The dataset card's Measurement Conventions (flyer wingspan = maximum during flight; body length = axis-aligned
     box): https://huggingface.co/datasets/PaulineLi/QuantiPhy
     - 37 test rows ask a flyer's width or wingspan; check that they use the maximum over frames (well under +.001).
  4. The validation changelog removed row 2607 (captured_0027s shoulder breadth). **Drop it from local validation
     scoring.** https://huggingface.co/datasets/PaulineLi/QuantiPhy-validation
- **Public competitor repos.** All are Track B at .575-.603 and add no method hints:
  - https://github.com/ferrousowl/quantiphy-trackb
  - https://github.com/Tangxiaoxiao1992/quantiphy-qpm (shows validation gains of +6.5 shrinking to about +1 on test)
  - https://github.com/kuotunyu/quantiphy-geo-vlm
  - https://github.com/prarabdhmisra/quantiphy
- **Papers:**
  - QuantiPhy, https://arxiv.org/abs/2512.19526, and its CVPR supplement:
    https://openaccess.thecvf.com/content/CVPR2026/supplemental/Puyin_QUANTIPHY_A_Quantitative_CVPR_2026_supplemental.pdf
  - EquiSD, https://arxiv.org/abs/2609.00658 (Claude's prior-following slope by source: internet .56, lab .90,
    rendered .85)
  - Code-as-World, https://arxiv.org/abs/2608.27549
  - ATS, https://arxiv.org/abs/2608.19807
  - Seeing Is Not Measuring, https://arxiv.org/abs/2609.29073
- **Exposure to flag for the user (not acted on):** https://github.com/VihanAggarwal/quantiphy-challenge is PUBLIC.
  It includes `research/PROBES.md` with every lever, and our leaderboard team name is "VihanAggarwal". Teams at
  .81-.82 could copy the family rules. Consider making it private until Oct 24.

### Open research leads for Oct 14-20 (free, CPU or Colab)
Each has a label-free kill test.

| Lead | Expected gain | Cost | Kill test |
|---|---|---|---|
| A. Extend the bird-family method to D2/D3 families: a stated motion fact in a consecutive-id sibling sharing at least 2 object names, confirmed by the scale-free pixel-speed ratio | up to +.002 | CPU, hours | Pixel-speed ratio matches the stated ratio within 3% |
| B. Event-gated per-frame speed operator plus extrapolation outside the track on D2 simulation timed-speed rows (screen already lists 0203/0204/0257-0262) | +.001 to +.002 | CPU, hours | Event detected on the pipeline's own track; the move goes toward the independent direct answer; no validation tuning |
| C. Pooled f for same-camera groups (6 groups, S3 45 + D3 46 rows): predict each clip's stated prior from the other clips' pooled f | up to +.002 | CPU, minutes | Median error under 7% |
| D. Multi-view reconstruction (MapAnything https://arxiv.org/abs/2509.13414, weights facebook/map-anything-apache; π3; DA3 https://arxiv.org/abs/2511.10647) on 3D-sim families with at least 2 depth-distinct cameras (11 families) | up to +.005, speculative | Colab, about 1 day | Reconstruction reproduces stated priors within 10% median. Low odds: the s3sim study found the residual misses are definitional and shared by every view. |
| E. 3D ballistic fit with known g for the 62 D3 sim rows with gravity priors | up to +.002 | CPU | Must reproduce stated motion facts |
| F. Paid only, outside this workflow's rules: a definitional re-ask on the 61 raw S3 static-size rows | up to +.002 | about $3-5 | User decision |

---

## 4. Honest projected score, and what .85 would need

| Step | Overall gain | Running total |
|---|---|---|
| physb2 (scored) | | .811 |
| + path85 combo (verified) | +.003 (+.0015 to +.0045) | about .814 |
| + U1-U4 winners only | 0 to +.002 | .814-.816 |
| + Table 6 (if approved) | +.0022 to +.0027 | +.0025 |
| + hedges (d2sizeenv, s3p, x0.97, x1.035) | 0 to +.001 | |
| + leads A-E, if they pass their kill tests | 0 to +.005 | |

- **Projected final: .813-.819.** Central estimate about .815 without Table 6 and about .818 with it.
- **Top 5** (now .8195 and rising, since the .81-.82 cluster is moving +.005 to +.025 per day): about 15-25%.
- **.85 needs +.039**, i.e. about .87 macro on the validation videos, everywhere at once. Everything found here sums
  to under +.01.
  - Reaching .85 would need a qualitatively better base predictor for 3D (S3 non-lab .742, S3 lab .782, D3 .80) and
    S2 internet. In practice that means new model output: a stronger or different closed model, or a new
    measurement modality that passes the multi-view kill test.
  - Our own tests say re-asks, more runs, other frontier models (GPT-6 Astra, Gemini 3.1 Pro), agent loops and
    single-image FOV do not supply it.
  - Paid calls are excluded under this workflow's rules, so .85 is not reachable within the current constraints.

---

## 5. Upload plan, day by day (5 successful uploads per UTC day, shared with Track B)

Rules for every upload:
- One change per category slot, read against the latest scored base.
- Record the scores (3 decimals per category, 4 overall) in `research/path85_strategy/uploads_registry.json` and run
  `decode.py`.
- Rebase new levers on the latest scored composite.
- Never upload 5 rows or fewer in isolation.
- The final file must be a composite whose score has already been observed, and it should be our **last** successful
  upload. Confirm whether the board keeps the best or the last submission.
- Confirm the deadline. Oct 23 23:59 AoE = Oct 24 11:59 UTC; do not rely on the extra UTC day.

| Day (UTC) | Uploads |
|---|---|
| **Oct 13** | 1-4: U1, U2, U3, U4 (built; read vs physb2). 5: **`trackA_cand_path85_combo.csv`** (replaces U5; read vs physb2). Not U5, U6 or U7 as built: U5 and U6 contain 1874, and U7's S2/D2 slots duplicate the combo. |
| **Oct 14** | 1: **C1** = combo plus the U1-U4 winners via `merge_skip.py`. Rebuild labmot if an S3 lab-noise rung won; keep combo values on shared rows. Check each category is within +-.0015 of base plus the sum of the deltas; otherwise bisect. 2: U6r on C1: D2 d2sizeenv, S3 s3p (skip if Table 6 is approved), D3 labsize_x097; S2 slot empty or lead B if ready. 3: if Table 6 is approved, C1 + T6 (S3/D3 slots); otherwise the U8 loss-map diagnostic (on C1). 4: adaptive rung (next S3 lab-noise / D3 emulator step around the U1/U2 winners; stop a ladder after its first loss on each side). 5: Track B, if a v4 candidate exists (task #34); otherwise spare. |
| **Oct 15** | 1: U9 diagnostic (completes the 16-cell loss map with diagE/F and U8). 2: D3 precision upload: C1 + d3simmot_x1035 + labsize rung (single category, so the 4th decimal pins the change to +-.0004). 3-4: research leads A/B, if their kill tests pass (one mechanism per slot). 5: spare or Track B. |
| **Oct 16** | Up to 4 research uploads (leads A, B, C, E as each passes its kill test), each on the latest composite. 1 spare. |
| **Oct 17** | **C2** composite of all winners so far, plus 2-3 research uploads. |
| **Oct 18** | Research uploads (lead D only if its kill test passed on Colab); 2+ spares. |
| **Oct 19** | **C3** composite, plus 1-3 research uploads. |
| **Oct 20** | Last day for new mechanisms (2-3 uploads). No new levers after this. |
| **Oct 21** | Up to 5 single-category precision uploads: C3 plus one marginal bundle each, to confirm sub-.001 bundles. Adopt only if the decoded interval is above 0. |
| **Oct 22** | **F** = final composite. Also upload one alternative (F minus its riskiest bundle) so both are observed; then re-upload F last so it is the latest submission. |
| **Oct 23** | Re-upload F only if anything changed; otherwise keep the slots spare. Prepare the reproducibility package (all rule scripts and cached runs, no API needed to rebuild). |
| Oct 24 to 11:59 UTC | Emergency only, if the AoE deadline is confirmed. |

Slots are not the bottleneck: about 55 remain against about 15 real levers. Days without new levers should leave
their slots unused rather than invent uploads.

### Next actions (for the parent)
1. Upload `trackA_cand_path85_combo.csv` today together with U1-U4. Do not upload U5, U6 or U7 as built.
2. User decisions:
   - (a) Table 6 allowed? If yes, run `build_combo.py --t6`.
   - (b) Make the GitHub repo private until Oct 24?
   - (c) Any paid budget for lead F?
3. Fix `is_stated()` in `research/labnoise/build_candidate.py`. Drop validation row 2607 from local scoring.
4. Launch leads A, B, C (CPU, free) now. Start lead D on Colab only as a kill test first.
