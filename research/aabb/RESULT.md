# World-AABB / yaw / origin-depth convention prompt for 3D simulation (Argon Idea 4)

## Pre-registered kill test (written 2026-10-14 before the paid pilot was run)

Pilot: the 6 validation 3D non-lab videos (52 questions), one new Claude run with the exact v1 request of
`runs/val_hr_v1_high` (`ca.build_request(rows, n_uniform=16, max_frames=32, effort="high", prompt_version="v1",
max_side=2576)`, claude-opus-5-5) plus a short convention block appended to the system prompt (world-axis
bounding-box sizes, yaw formula, depth = range to the object origin). Streaming, sync, via `qp.budget`
(reserve worst case + record). Hard cap for this lever: $5.00 (enforced in the script on this run's ledger total).

**PASS** iff BOTH:
1. direct-answer MRA of the new run >= MRA of `runs/val_hr_v1_high` + 0.015 on the 52 questions, and
2. the new run is better on more than half of the clips whose clip-mean score changes.

Reported alongside (not part of the bar): clip-bootstrap 90% CI of the delta; the 3-run log-median with the new
run replacing v1 (new, `val_hr_v2_high`, `val_opus_high`) vs the current 3-run median (v1, v2, opus); size rows
only (30) and motion rows only (22).

Mechanism guard (pre-registered, decides whether a PASS is worth a test run): validation 3D sizes are read low
across ALL dimensions (Step 1: median log(pred/gt) -0.116, heights -0.037), while exact stated test facts show no
overall bias (-0.006). A prompt that simply inflates every size could therefore pass on validation and lose on
test. A PASS counts as the AABB mechanism only if the size-row gain comes mainly from horizontal dimensions
(length/width): mean log-ratio shift on length/width rows > shift on height rows. Otherwise it is reported as
"PASS, mechanism not confirmed" and the recommendation is a stated-facts check before any test run.

If PASS: estimate the cost of a run on all test 3D simulation clips with size questions and STOP (no test run).

## Step 1 (free): bias of the current direct answers by dimension and object type
(filled in after Step 1 and before the pilot)

Command: `.venv/bin/python research/aabb/step1_bias.py > research/aabb/step1_bias.txt` (no API; labels used only
to score). Direct answers = log-median of the 3 cached runs (validation: val_hr_v1_high, val_hr_v2_high,
val_opus_high; test facts: the 3 test runs as tabulated in research/simfov/out/table.csv). "Elongated" = a noun
list (car, boat, bench, pier, bus, ...). Full row listings are in `step1_bias.txt`.

**(a) Validation, 3D non-lab size rows (30 rows, 5 clips).** All dimensions are read low.

| dimension | n | median log(pred/gt) | share under | MRA |
|---|---|---|---|---|
| all | 30 | -0.116 | .77 | .763 |
| height | 11 | -0.037 | .73 | .764 |
| length | 6 | -0.189 | .67 | .800 |
| width | 11 | -0.160 | .91 | .755 |
| elongated object, length/width | 13 | -0.148 (mean -0.171, clip-bootstrap 90% [-0.274, -0.054]) | .85 | .815 |
| other object, length/width | 4 | -0.417 | .75 | .625 |

Within-clip contrast (mean log ratio of length/width rows minus height rows of the same clip, which removes a
clip-wide scale error): 0009 +0.152, 0015 -0.368, 0034 -0.017, 0060 -0.155, 0300 -0.037. Mean -0.085;
horizontal is lower in 4 of 5 clips. But the largest misses are not yaw-shaped. simulation_0009 reads every
dimension of the boat about 0.6x, including its height (-0.51), which is a clip-wide scale error. The bench in
0015 (2.23 x 0.706 m label vs 1.55 x 0.55 read) cannot be a yawed box of the read object: the most a yaw can
inflate a 1.55 x 0.55 m footprint's long side is sqrt(1.55^2 + 0.55^2) = 1.64 m. Its height is read high (+0.32),
so this is foreshortening or depth confusion. The worst row, lane width 11.8 m read 5.8, is an ambiguous object.
The one clean case is the 0300 car: length 4.45 read 4.60 (+0.03), height 1.15 read 1.12, and width "from the
left wheel to the right wheel" 2.23 read 1.90 (-0.16). That fits a few degrees of yaw or mirrors in the box, but
it is a single row.

**(b) Test: exact stated size facts on 3D simulation (61 rows, 27 clips, but only ~6 distinct objects).**

| subset | n | median log(pred/gt) | mean | share under | MRA |
|---|---|---|---|---|---|
| all | 61 | -0.006 | +0.102 | .51 | .797 |
| length (boat 10 m, white car 6.0 m, turning yellow car 5.44 m, eagle 0.8 m) | 47 | -0.026 | +0.063 | .60 | .826 |
| height (person 1.75/1.87 m, forklift 2.47 m, car 1.15 m) | 14 | +0.047 | +0.234 | .21 | .700 |
| elongated (car/boat) lengths | 34 | -0.040 (mean -0.048, 90% [-0.085, -0.010]) | | .74 | .918 |

There are no width facts. Vehicle and boat lengths read about 4-5% low, and the 3 scenes behind the 34 rows are
not independent. Two explanations fit equally well: a world-box inflation of a few % (a yawed 5 x 2 m car gains
at most +7.7% in length), or Claude's tight extents missing protruding parts. The large test misses are gross
scale errors in both directions (person 1.75 m read 2.9-5.5 m in 0025/0031, eagle 0.8 m read 1.6-6.6 m) and do
not depend on the dimension.

**(c) Validation, 2D simulation size rows (18 rows, 4 clips; the same Blender label pipeline).** No horizontal
under-bias. Widths are read HIGH (big bird 2.04 read 2.56-2.90, small bird 1.30 read 1.72), and diameters are
unbiased except for 4 moon models that the labels give as equal at 0.137 m.

**Step 1 verdict: weak or partial support.** Horizontal dimensions are read somewhat lower than heights on
validation (-0.085 within clip, 4/5 clips, 5 clips only). Vehicle and boat lengths on test facts read about 5%
low. Nothing shows the 1.15-1.41x inflation that Idea 4 claimed. Most of the size loss is clip-wide scale error
and gross misses, in both directions. The largest gain the AABB mechanism could deliver is roughly a 5% shift on
horizontal dimensions of vehicles and furniture.

## Step 2 (paid pilot, $2.71 of the $5 cap)

Commands:
```
.venv/bin/python research/aabb/run_pilot.py --dry   # token estimates, no API call
.venv/bin/python research/aabb/run_pilot.py > research/aabb/run.log 2>&1
.venv/bin/python research/aabb/null_check.py > research/aabb/null_check.txt   # free: same statistic between existing runs
```
The request is the exact v1 request of val_hr_v1_high with `CONVENTION` (in `run_pilot.py`) appended to the system
prompt. That block says: sizes are world-axis bounding-box extents enclosing the whole mesh; height is the full
vertical extent; length/width = L|cos a| + W|sin a| and W|cos a| + L|sin a| for yaw a relative to the scene's layout
lines; priors follow the same convention; depth info = Euclidean range to the object origin (pelvis, rig root).
All 6 clips ran with stop `end_turn` and 52/52 answers. Spend: 0060 $0.649, 0015 $0.249, 0009 $0.430,
0170 $0.448, 0034 $0.227, 0300 $0.708; ledger run `aabb_pilot` total $2.71 (6 usage lines). Raw responses are in
`research/aabb/out/*.json`.

Direct-answer MRA on the 52 questions (`run.log`):

| run | all 52 | size rows (30) | other rows (22) |
|---|---|---|---|
| val_hr_v1_high (comparator) | .7942 | .750 | .855 |
| val_hr_v2_high | .7981 | .743 | .873 |
| val_opus_high (v1 prompt) | .8019 | .777 | .836 |
| **aabb (new)** | **.8269** | **.830** | **.823** |
| 3-run median v1+v2+opus (current) | .8096 | .763 | .873 |
| 3-run median aabb+v2+opus | .8231 | .783 | .877 |
| 4-run median v1+v2+opus+aabb | .8154 | .783 | .859 |

**Kill test: aabb - val_hr_v1_high = +.0327 (clip-bootstrap 90% [-.037, +.106]), but better on only 3 of the 6
clips that change** (0009 +.222, 0060 +.062, 0034 +.033; 0170 -.113, 0015 -.027, 0300 -.020). Condition 2 needs more
than half, so the result is **FAIL**.
3-run median with aabb replacing v1: +.0135 [-.009, +.048], better on 1 of 4 changed clips (0009 +.111; 0015
-.009, 0060 -.008, 0300 -.020). 4-run median: +.0058 [.000, +.012], about one more run's worth (the earlier
finding that more runs saturate).

Run-to-run noise reference (`null_check.txt`; the same statistic between existing runs):

| pair | all 52 | size 30 | other 22 | clips better / changed |
|---|---|---|---|---|
| hr_v2 - hr_v1 | +.0038 | -.0067 | +.0182 | 1/5 |
| opus_v1 - hr_v1 (same v1 prompt) | +.0077 | +.0267 | -.0182 | 2/6 (0009 +.222) |
| aabb - hr_v1 | +.0327 | +.0800 | -.0318 | 3/6 |
| aabb - hr_v2 | +.0288 | +.0867 | -.0500 | 5/6 |
| aabb - opus_v1 | +.0250 | +.0533 | -.0136 | 3/5 |

**Where the size gain comes from. The mechanism guard fails.**
- simulation_0009 (+.222 per clip, the largest single item) is run-to-run noise in a clip-wide scale. The boat's
  length/width/height reads 1.9/0.7/0.3 in hr_v1, 2.2/0.8/0.45 in hr_v2, 4.2/1.2/0.45 in opus (same v1 prompt)
  and 3.9/1.5/0.65 in aabb (gt 3.62/1.23/0.75). opus already gets the same +.222 without the block. The
  scale there comes from a speed prior (1.5 m/s -> focal solve), which is not a yaw effect, and all three
  dimensions move together.
- simulation_0060 lane width (11.8 m): 5.9 -> 12.2 (score .4 -> 1.0). The note says "lane taken as the road ahead";
  this is a reinterpretation of an ambiguous object, not a world-box computation.
- Heights rise as well: turning car 1.45 -> 1.60, pedestrian 1.58 -> 1.78 (the "full vertical extent" wording).
  On test facts heights are already read HIGH (+0.047 median), so this kind of general inflation would not carry
  over.
- Without 0009 and the lane row, the log shift (aabb - hr_v1) is **+0.004 on 11 length/width rows and +0.011 on
  10 height rows**. Horizontal dimensions do not move more than heights, so there is no AABB-specific effect. In
  the one clean car (0300) the block made length worse (4.70 -> 4.10, gt 4.45) and height worse (1.12 -> 1.00,
  gt 1.15), with width 2.00 -> 2.10 (gt 2.23).
- Non-size rows lose -.032 (mainly the 0170 astronaut accelerations, a clip known to swing +-0.3 between prompts).

## Verdict: FAIL

- The pre-registered kill test fails on condition 2 (3/6 clips). The +.033 headline delta is within the run-to-run
  spread: one same-prompt run (opus) already reaches +.008 vs hr_v1, with the identical +.222 on 0009.
- The mechanism guard also fails: length/width rows shift no more than heights once the noisy clip and the
  ambiguous lane row are removed.
- Step 1 finds no 1.15-1.41x inflation pattern on validation or on exact test facts. At most a ~5% under-read
  remains on vehicle and boat lengths, which are mostly stated-fact rows our rules already answer.
- No candidate is built and no test run is recommended. Expected overall gain: 0.
- Cost, for reference only: the 3D simulation test clips with size questions are 117 clips / 498 rows (S3 122,
  D3 376). At the test runs' settings (854 px, batch, ~$0.107/clip in test_3dnl_v1_high_b) a run would cost
  ~$12.5. At the pilot's settings (sync, max side 2576) it would cost ~$0.45/clip, i.e. ~$53.

Follow-ups (not done):
1. The aabb run is the best single validation run (.827 vs .794-.802), but its edge sits on 2 rows (0009 boat
   scale, 0060 lane). Isolating any real prompt effect from run noise would take >= 2 more pilot runs (~$5.5),
   and the upside as a median member is about one extra run (+.006 on validation, ~+.001 overall). Not
   recommended.
2. The real S3 simulation losses are clip-wide scale errors (0009-type, from focal solves on motion priors) and
   gross misses in both directions (test facts: person 1.75 m read 2.9-5.5 m, eagle 0.8 m read 1.6-6.6 m).
   Family facts and pooling already address these, and a dimension convention cannot fix them.
