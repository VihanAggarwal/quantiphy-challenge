# Loss audit: where the remaining ~.04 lives (2026-10-14)

Analysis only. Validation labels and stated test facts were used only to measure errors. No answer was set from them,
no API was called, and no repo code was changed. Scripts and tables are in `research/r86/loss_audit/`:
- `master.py` builds a per-row table (`master.pkl`) for all 3,289 test rows.
- `buckets2.py` builds the bucket map (`buckets2.csv`).
- `trackb_map.py` builds the Track B map (`trackb_map.csv`).
- `classes.csv` holds my hand labels of error classes for every labelled row with more than about 18% error.

Reference file: `trackA_combo3_on_combo2.csv`. Its expected scores are .834 / .863 / .770 / .814, or .820 overall (combo2
scored .817).

## 1. Bottom line

- **Total loss is .180. Reaching .86 means removing 22% of all of it.** On both labelled sets (128 validation rows, 163
  exact stated facts), +.04 corresponds to shrinking every row's log error by about 30% (α = 0.7 in
  pred' = gt·(pred/gt)^α). The leaders score about .87 on the validation videos against our .827, which is consistent
  with roughly 30% smaller errors across the board.
- **The loss is diffuse.**
  - No subset holds more than .031.
  - No bucket of one kind within one subset holds more than .020.
  - The best single bucket, cut by 30%, is worth +.006.
- **Points are not equal per row.**
  - One S3 row weighs .000465 overall per unit of item score, and one S2 row .000452.
  - One D3 row weighs .000268, and one D2 row .000220.
  - **S3 holds 32% of all loss (.058) with 17% of the rows.**
  - Any new answer source should go to S3 first, then S2. Per row, D2 pays half as much.
- **Two coherent mechanism pools hold half of the loss:**
  - **Lab motion and distance rows** (S3 lab speed/distance/accel, D3 lab motion, D3 lab distances; 440 scored rows):
    about .044, estimated item mean about .72.
  - **3D simulation** (S3 sim and D3 sim, 715 scored rows, 238 with no family anchor): about .048.
  - The 2D buckets hold the remaining .088 in small slices of .003 to .020 each.
- **About 30-45% of our validation loss looks unrecoverable for everyone:**
  - label oddities: big bird 0.72 m smaller than the stated small bird 0.94 m; desk 857.9 cm; ball-to-person 0.198 m;
    basketball 9.32 m/s indoors;
  - non-monotone astronaut accelerations;
  - part definitions.

  Extrapolated to test, this is a floor of about .025-.03 overall. The reducible part of our loss is therefore about
  .10-.12, and .86 needs a third to two fifths of it.
- **Every free lever I could test here is below +.002.** Section 6 lists them. This matches path85. The gap is a better
  base predictor on S3 (sim and lab), on D3 simulation sizes and on lab motion, not a missing post-rule.

## 2. Subset loss pools (decoded, adjusted to combo3)

Method:
- Start from the diagE/F subset means on p21.
- Add the category deltas since p21: combo2 as scored, combo3 as expected from the U1-U4 reads.
- Assign each delta to the subsets whose rows changed: p21 to combo2 changed S2 sim 22 rows, D2 rest 69, D3 rest 162;
  combo2 to combo3 changed S2 sim 57, S2 internet 54, S3 lab 36, D3 lab static 41, D3 rest 36.

| Subset | Scored n | Exact fact rows | Item mean p21 | Item mean combo3 | Loss (overall pts) | 30% cut | +.05 per non-fact row |
|---|---|---|---|---|---|---|---|
| S3 lab | 317 | 0 | .782 | .789 | **.0311** | .0093 | .0074 |
| D3 rest (lab motion + sim) | 599 | 79 | .805 | .821 | **.0288** | .0084 | .0070 |
| S3 sim+seg | 221 | 30 | .742 | .742 | **.0265** | .0078 | .0044 |
| S2 sim+seg | 362 | 7 | .828 | .851 | .0244 | .0073 | .0080 |
| D2 sim static | 719 | 15 | .851 | .854 | .0231 | .0069 | .0077 |
| D3 lab static | 334 | 15 | .799 | .802 | .0177 | .0053 | .0043 |
| S2 internet | 191 | 0 | .796 | .802 | .0171 | .0051 | .0043 |
| D2 rest | 418 | 4 | .857 | .879 | .0111 | .0033 | .0045 |
| **Total** | 3161 | 150 | .810 | .820 | **.1799** | .0535 | |

If the fact rows are near 1.0, the non-fact rows sit lower than the subset means:
- S3 sim non-fact (191 rows): about .706.
- D3 rest non-fact (520 rows): about .80.

## 3. Bucket map: subset x question kind (estimated)

How the estimates are built:
- Each bucket gets a prior item mean from labelled evidence:
  - validation rows scored with combo3;
  - stated-fact rows scored with the raw answer;
  - for lab sizes, the Table-6 read, which implies about .94, and the stated ball sizes, which read 1.056x.
- Fact rows are set to .97.
- One additive shift per subset, within ±.05 in every subset, makes each subset reproduce its decoded mean.

The within-subset split carries roughly ±.05 uncertainty per bucket mean. The subset totals in section 2 are exact up to
leaderboard rounding.

Column notes:
- "dgd>40%" counts non-fact rows where Claude's direct answer and the geometry disagree by more than 1.5x.
- On labelled 2D and lab rows that flag predicts item .61 against .92 for agreeing rows.

| Bucket | Scored n | Facts | Est. item mean | Loss (pts) | +.05 per row | 30% cut | dgd>40% | Evidence |
|---|---|---|---|---|---|---|---|---|
| D2 sim-static size | 644 | 15 | .86 | **.0203** | .0069 | .0061 | 28 | val .90 (9); facts 1.00 (16) |
| S3 lab speed | 135 | 0 | .72 | **.0175** | .0031 | .0052 | 25 | val .79 (8): under-read x.64-.76 (0034as, 0061, 0027s) |
| S3 sim size | 104 | 8 | .71 | **.0139** | .0022 | .0041 | 10 | val .745 (11); facts raw .83 (8) |
| D3 lab-static distance | 115 | 0 | .67 | **.0103** | .0015 | .0031 | 13 | val .50 (3, one label oddity); 72 A-B, 40 displacement, 6 to-camera |
| D3 sim size, speed prior | 154 | 28 | .76 | .0098 | .0017 | .0029 | 14 | facts raw .63 (28): eagle/boat/person families, K-corrected in family |
| S2 sim accel | 64 | 0 | .70 | .0087 | .0014 | .0026 | 11 | val .45 (6, astronaut 0171); 12 articulated rows |
| S2 internet speed/accel | 75 | 0 | .77 | .0080 | .0017 | .0024 | 4 | val speed .88 (5), accel .30 (1) |
| D3 lab-static size | 219 | 15 | .87 | .0074 | .0027 | .0022 | 30 | val .88 (10, desk 857.9 oddity); labfacts raw .90 |
| S2 sim speed | 149 | 4 | .89 | .0074 | .0033 | .0022 | 3 | val .90 (6) |
| D3 lab motion | 105 | 0 | .76 | .0068 | .0014 | .0021 | 41 | val 0061 .64; emulator x1.00 on 107/150 |
| S3 lab distance/path | 57 | 0 | .74 | .0068 | .0013 | .0021 | 10 | val .97 (3) |
| S2 sim size | 123 | 3 | .88 | .0067 | .0027 | .0020 | 0 | val .50 (2, one oddity) |
| S3 sim speed | 74 | 19 | .81 | .0066 | .0013 | .0019 | 5 | val .97 (7); facts raw .85 (24) |
| D3 sim size, accel prior | 198 | 24 | .89 | .0059 | .0023 | .0017 | 83 | facts raw .965 (26) |
| S2 internet size | 75 | 0 | .83 | .0059 | .0017 | .0018 | 0 | val .95 (4) |
| D2 internet (all) | 201 | 0 | .88 | .0052 | .0022 | .0016 | 0 | val .92 (17) |
| D2 sim motion speed | 189 | 2 | .88 | .0049 | .0021 | .0015 | 11 | facts .95 (2) |
| S3 lab size | 114 | 0 | .91 | .0047 | .0026 | .0014 | 33 | val .98 (5) |
| D3 sim speed | 104 | 23 | .85 | .0042 | .0011 | .0012 | 14 | facts raw .84 (26) |
| S3 sim accel | 29 | 3 | .70 | .0040 | .0006 | .0012 | 17 | facts raw .57 (3) |

Buckets with 15 rows or fewer, or about .003 of loss or less: S2 internet distance, D2 sim-static distance, S3 lab accel,
S3/D3/S2 sim distance, D2 lab, D2 sim accel, D3 sim accel. Together they hold .016.

### What .86 needs, in these units

- A 30% loss cut in every bucket gives +.054. A 22% cut gives +.040.
- No realistic single fix reaches +.01. The largest single-bucket 30% cuts are:

  | Bucket | Gain at a 30% cut |
  |---|---|
  | D2 sim-static size | +.006 (644 rows) |
  | S3 lab speed | +.005 |
  | S3 sim size | +.004 |
  | D3 lab distance | +.003 |
  | D3 sim size, speed prior | +.003 |

- An example decomposition that reaches .86:

  | Category | From | To | Overall gain |
  |---|---|---|---|
  | S3 | .770 | .85 | +.020 |
  | D3 | .814 | .86 | +.0115 |
  | S2 | .834 | .87 | +.009 |
  | D2 | .863 | .863 | 0 |

  Every step needs a better answer source on 3D content.

## 4. Error classes

Labelled rows with more than about 18% error were classified by hand: `classes.csv`, 37 validation rows and 35 fact rows.
Fact rows are scored with the raw answer, before the facts, K and P rules.

| Class | Val loss items (share of 22.2) | Fact-raw loss items (share of 25.8) | Test rows exposed (scored) | Fixable? |
|---|---|---|---|---|
| ODD: label oddity / inconsistent label | 3.5 (16%) | 0 | unknown; val rate 3.1% of rows, so about 100 test rows (about .025-.03 floor) | no |
| ACCN: acceleration of articulated, mocap or tiny motion (astronaut 0171, billiard decel) | 3.6 (16%) | 0.6 | 29 articulated accel rows (S2 12, S3 13) of 138 accel rows | mostly no |
| LABCONV: lab motion label process (clicked centre + hand-read ToF depth; pendulum along the line of sight) | 3.4 (15%) | 0 | 341 lab speed / accel / displacement / path rows | partly (emulator already in) |
| DEF: part or extent definition (pier deck, pedestal, roof frame, "lane" = whole road) | 2.6 (12%) | 0 | inside 396 non-fact 3D sim size rows | partly: convention prompts (Argon idea 4, under test) |
| MEAS3D: 3D sim extent / speed misjudged (x.68-.82) | 1.6 (7%) | 1.4 | same 396 + 129 3D sim speed rows | yes, with a better predictor |
| VSCALE: whole-clip scale (eagle at the lens read 6.6 m; 0025 person 5.5 m) | 0 | 13.5 (52%) | 238 3D sim rows with no family anchor (S3 117, D3 121) | in families yes (facts/K/P, done); elsewhere no anchor |
| REL3D: 3D distance between two objects | 0.8 | 0 | 221 (lab 175, sim 46) | partly |
| PERSP: 2D single scale with a foreshortened prior (top-down person) | 0.3 | 2.1 | few (0041 family, already facts) | done |
| EVENT / time / window | 0.6 | 1.0 | 57 timed rows within .25 s of a clip end; 12 beyond the end (captured_0018) | small |
| MEAS / RULE (2D measurement; a rule moved a good raw answer) | 0.7 | 0.4 | diffuse | small |
| Errors under ~18% (not classified) | 5.1 (23%) | 6.8 (26%) | every row | the 30%-shrink regime |

Error size, measured on validation (combo3):

| Error band | Rows | Loss items | Share of loss |
|---|---|---|---|
| <5% | 57 | 0 | 0% |
| 5-20% | 39 | 5.9 | 27% |
| 20-50% | 22 | 7.7 | 35% |
| >50% | 10 | 8.6 | 39% |

What-ifs on validation:
- Fixing every >50% miss to a 20% error adds +.046.
- Turning every 5-20% error into under 5% adds +.046.
- The facts give +.052 and +.043 for the same two what-ifs.

Either half alone would be .86, but most >50% misses are ODD or ACCN (section 1).

## 5. Worst cases inspected on frames

Frames were extracted with cv2 to the session scratchpad, outside the repo.

| Clip | Our answer vs label | Class | What the frames show |
|---|---|---|---|
| captured_0027s | speed 130 vs 201.7 cm/s; accel 480 vs 1086 cm/s² (t=0.2 s) | LABCONV | Red ball on a string: a pendulum swinging toward and away from the camera, so most motion is along the line of sight. Geometry gives 120, Claude's direct answer 23. The label (accel ≈ g) comes from ToF depth differences. |
| internet_0013 | bicycle 2.28 vs 3.41 m/s | MEAS | Drone top-down view of a roundabout. The scale comes from a tiny walking pedestrian (prior 1.1 m/s). Claude's direct answer of 3.5 was right; geometry was off by 33%. |
| simulation_0039_segmented | eagle length raw 6.6 vs 0.8 m | VSCALE | The eagle is a blurred blob at the top of the frame, close to the lens. Already fixed by family facts and K (final 0.8 / 1.48). |
| simulation_0311 | car accel raw 0.4 vs 5 m/s² | EVENT | The car enters the frame at about 1 s. Fixed by a fact. |
| simulation_0060 | lane width 6.3 vs 11.8 m | DEF | The road has no lane markings, so the label's "lane" is the whole road. |
| simulation_0015 | pedestal 1.01 vs 0.6 m | DEF / label | Pixels scaled by depth (person at 12.26 m, pedestal at 9.46 m) give about 1.0 m, as Claude answered. |
| simulation_0009 | pier deck height 0.5 vs 0.26 m | DEF | The deck sits close to the water. |
| simulation_0020 | person 9.44 m, ball 1.39 m | sim analogue of PHYSB | A basketball player against a wall. The gravity-prior scale makes the whole clip about 5x too large. It is the only one of 11 canonical-size screen hits that is a real miss: 3 D2 rows. |
| simulation_0010/0011/0014 | door 5.1 / 6.76 / 7.36 m | none | A giant house consistent with the stated bird (1.19 m). There is a 44% spread across cameras of one door; pooling was skipped because of the spread. Coin flip; left alone. |

## 6. Quick checks run here (all free)

| Check | Result | Verdict |
|---|---|---|
| More runs in 2D and lab: median of 3 of the 5 Opus-high validation runs | 2D .820 vs single v1-hires .825; lab .695 vs .695; 3D sim .821 vs .794 (known) | Saturated outside 3D sim. |
| Per-video oracle scale (validation) | macro +.022 oracle; leave-one-row-out −.029 | Scale is not the lever on validation; in 3D-sim families it is already used (K). |
| Cross-render pooling (median of base/s/x final answers; internet twins) | Track A validation: +.033 per changed row (9 lab rows, 6 events); internet +.042 (7 rows). **Track B validation: −.035 per changed row (14 lab rows), and internet and sim also lose.** | Mixed; at most a D3 A/B read (proposal 3). |
| Lab depth convention: 84 ball observations in 17 events (f_audit_clean) | Slope of log f against log cos θ: +0.26 with range, −0.74 with Z; event-level +0.44 / −0.55. Range is closer to flat. The residual fits mild barrel distortion. | Still unresolved; no lever. Lab f scatters 6% (log sd) by event. |
| Canonical-size plausibility screen (persons, cars, balls, doors) | 11 hits; 1 real (simulation_0020) | +.0006 at most (proposal 4). |
| Cross-camera spread of the same object's size in sim families | D2 raw median sd .045, pooled to about 0; D3 raw .08 to 0 | The remaining 2D/3D sim size error is common to every camera (definitional or scale), so consistency checks cannot see it. |
| Third-opinion tiebreak (Astra / second Opus run) where geometry and direct disagree by more than 1.25x | n = 5 (2D) / 11 (lab) | Inconclusive; not pursued. |
| Order-of-magnitude scan (final vs direct beyond 8x) | 9 rows; every raw gross miss is already corrected by K or facts except captured_0018x beyond-clip rows | Nothing left. |

## 7. Track B map (`trackb_map.csv`)

Track B v3 was scored against Track A combo3 as a proxy reference. This is not a label; it only ranks where B's errors
concentrate. The column gives the points B would gain if it matched A's level.

| Bucket | Points | B rows more than 1.5x off A |
|---|---|---|
| D2 sim size | .047 | 28% |
| D3 sim size | .029 | 27% |
| S2 sim speed | .026 | 45% |
| S2 sim size | .021 | 33% |
| D3 lab size | .020 | 23% |
| S2 sim accel | .019 | 67% |
| S3 sim size | .019 | 39% |

On validation, B's macro is .610 against A's .827. By category: S2 .52, D2 .59, S3 .69, D3 .64.

So Track B's top-10 gap (+.046) lives in 2D simulation tracks: S2 sim plus D2 sim size together hold about .11 of
proxy points. That is the open-pointing + SAM-2 track lever already queued from Argon. Track B should not spend effort on
lab or 3D first.

## 8. Fix proposals

See also the workflow's structured output.

Ranked by what they buy:
1. **Kind-level diagnostics, K1 and K2: 2 uploads, gain 0.**
   - They replace this audit's ±.05 bucket estimates with exact means (±.002-.004) for the 8 buckets that decide where
     the paid budget goes.
   - K1 zeroes, on combo3:
     - S2 sim accel (64)
     - D2 sim motion speed (187 non-fact)
     - S3 lab speed (135)
     - D3 lab-static distance (115)
   - K2 zeroes:
     - S2 internet speed/accel (75)
     - D2 internet (201)
     - S3 sim size non-fact (96)
     - D3 sim size non-fact (300)
   - Each bucket mean = (combo3 − diag) × N_cat / n.
   - Do this instead of U8/U9 if slots are tight: U8/U9 split by motion vs static, but the levers are defined by kind.
2. **S3-first deployment rule for every in-flight lever** (Gemini/Argon prompts, Depth Pro, PoT):
   - Gate each lever per bucket. On 3D-sim rows a lever must show at least +.03 per row on validation 3D sim (52 q)
     plus the 106 fact rows (scored raw) to be worth a slot.
   - Then deploy S3 (190 non-fact sim + 317 lab) before D3, and D3 before D2.
   - The same per-row gain is worth 1.7x on S3 against D3, and 2.1x against D2.
3. **Lab cross-render median as an A/B read in a D3 slot** (102 D3 rows move by a median of 4.6%):
   - Expected +.0005 to +.001.
   - Evidence is mixed (section 6); kill it if the D3 read is below +.001.
4. **Micro-fixes, about +.001 together:**
   - simulation_0020 clip rescale to a 1.8 m person: 3 D2 rows.
   - S2 sim constant-acceleration pooling: 0223/0224(+seg)/0253/0254/0255(+seg)/0256/0234/0235, about 30 rows, to the
     clip median when the per-time estimates sit within ±20%.

None of these closes the gap. The audit's main recommendation is where to point the remaining $50 Claude, $34 OpenAI
and the 96 GB GPU: S3 lab speed/distance, S3 sim size, and D3 sim size with speed priors. Those buckets are where a
better predictor pays most per row.

### Gates for in-flight levers: per-row gain needed for +.002 overall (one readable upload)

Formula: g = .002 × 4 × N_cat / rows. Use these as kill thresholds on validation plus facts before any test-wide spend.

| Target rows | Rows | g needed per row |
|---|---|---|
| S2 sim non-fact | 355 | .012 |
| D2 sim static non-fact | 704 | .013 |
| S3 lab non-size (speed / distance / accel) | 203 | .021 |
| D2 rest | 414 | .022 |
| S3 sim non-fact | 191 | .023 |
| S2 internet | 191 | .023 |
| D3 sim size non-fact | 300 | .025 |
| D3 lab motion + distances | 220 | .034 |
| S3 sim size non-fact | 96 | .045 |

For .86, the in-flight levers together need about +.04. For example, +.08 per row on all 538 S3 rows plus +.05 on 520
D3 non-fact rows gives about +.027. The rest would have to come from 2D.

Micro-fix numbers:
- **Constant-acceleration pooling:** 33 rows qualify (non-articulated object, at least 2 timed accelerations within
  ±20% of the clip median). 23 of them move by more than 1%, with a median move of 5.3%. That is about +.0003 if the
  labels are keyframed constants. 0253 and 0254 show monotone trends (5.97 to 4.86), which may be real, so the
  confidence is low.
- **simulation_0020:** rows 8 (person 9.44), 9 (ball velocity 5.26) and 10 (ball 1.39). Multiply all three by
  1.8 / 9.44. If the labels follow the asset scale, as PHYSB found for internet clips, that is about +.0006.
