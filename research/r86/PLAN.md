# r86 plan: Track A toward .86, Track B toward .667 (written 2026-10-14 ~23:45 UTC)

Lead synthesis of the r86 proposals, their two skeptic verdicts each, and the pilots that finished tonight.
No test labels were used. Validation labels were used only to score finished pilots, never to pick a row.
No repo code was changed and nothing was committed. Notes and scripts are in `research/r86/plan86/`.
The Gemini share link (https://share.gemini.google/3raSAhUem3uK) does not resolve from here (ENOTFOUND). Its items as
relayed to us (Depth Pro FOV, program-of-thought, global spline fits, uncertainty router) are covered in section 4 from
the test results on disk.

---------------------------------------------------------------------------------------------------------------------

## 1. Executive summary

**Is .86 reachable by Oct 23? No, not with anything we have or can afford. I put P(>= .86) below 2%.**

- **Where we are:** best scored .817 (combo2). combo3 is expected at about .820 (.834 / .863 / .770 / .814).
- **What .86 needs:** +.040, which means cutting about 30% of the log error on every row (loss_audit section 1). No
  subset holds more than .031 of loss, and no free lever tested here is worth more than +.002.
- **Every in-flight Track A lever finished tonight and failed its pre-registered kill test.** Each was verified by an
  independent agent:
  - global spline derivatives (`research/splinefit`): FAIL;
  - fixed uncertainty gates / router (`research/gates`): FAIL;
  - Depth Pro FOV (`research/depthpro`): FAIL at stage 1, median focal error .33;
  - world-AABB prompt, Argon Idea 4 (`research/aabb`, $2.71): FAIL on 3 of 6 clips.
- **The two new frontier models tie Claude.** Direct-answer MRA on the 159 validation questions:

  | Model | Direct MRA |
  |---|---|
  | Claude v1 | .765 |
  | Gemini 4 Argon | .762 |
  | GPT-6.1 Sol | .762 |

  No available model is a better base predictor. The leaders score about .87 on the validation videos, against our
  .828; their edge is something we have not identified.

**The single result it hinges on:** a new answer source whose direct answers score at least about .84 on the 159
validation questions, about 30% less log error than Claude, Sol or Argon.
- The only untested frontier candidate from the window when the leaders jumped is Meta Muse Wonder (released Oct 12,
  video input, $4/$20 per M tokens).
- A validation pilot costs about $4-6 of new money and needs an OpenRouter key.
- Even if it passes, the test run (about 370 non-lab videos, about $60) is in no budget.
- So the hinge is a user decision about money, not a research step. Section 2, item A4.

**Realistic Track A target: about .825 (90% range .818-.832).** That means holding roughly 7th-9th, since the field is
still rising (5th place was .8348 on Oct 14 and is forecast at .845-.855).
- The one live lever with a positive signal is a cross-family blend with GPT-6.1 Sol on non-lab S2/D2/S3 rows. Its
  test run is going now, under the existing OpenAI budget.
- On validation, a 0.25 log-weight Sol blend gains +.015 (S2), +.012 (D2 non-lab) and +.013 (S3 sim) per row, every
  90% CI above 0. That is only 3-6 clips per subset, so shrink it: expected +.004 overall (0 to +.008).

**Track B:** .621 now. Free levers already built (v5, the clamp, S2 re-routing, L6s) take it to about .636.
- Reaching .667 depends on one Colab result: the open model, given the Track A context, passes the pre-registered ctx
  kill test.
- The ctx run is already pushed to `main` (preset "ctx"). TB-1 is folded into it by switching the model to Qwen3.8-27B.
- P(Track B >= .667) is about 0.25-0.3. Top 10 (.7128 now, forecast .74-.76) is out of reach.

**Two user actions that cost nothing and protect what we have:**
1. Make the GitHub repo private now. It publishes our .817 test predictions and every rule (intel.md section 0).
2. Email quantiphybench@gmail.com to ask whether the final rank uses the best or the last submission. The schedule
   below assumes the worst case: it ends with the best composite as the last upload.

---------------------------------------------------------------------------------------------------------------------

## 2. Ranked list (survivors, plus levers from tonight's pilots), with schedule

Adjusted gains are overall MRA on the track named. Two skeptic-verified proposals survived: TB-1 (+.03 Track B) and
the canonical-class clamp (+.004 Track B). Items marked [lead] come from data that arrived after the proposals were
written. They are reproducible with `research/r86/plan86/{sol_sub,ens3}.py` but have not been skeptic-verified.
Overall gain = rows x item gain / (4 x N_cat).

### Track A

| # | Lever | Adjusted gain | Kill test (pre-registered here, before test outputs are read) | Cost | Owner |
|---|---|---|---|---|---|
| A1 | [lead] **Sol cross-family blend.** pred = exp(.75 ln base + .25 ln Sol) on non-fact, non-validation-overlap rows of S2 (all sources), D2 (simulation and internet) and S3 (simulation and segmented). Segmented rows take the original clip's Sol answer when the normalised question matches. D3, lab rows and rows with no Sol answer are unchanged. | +.004 (0 to +.008). Unshrunk +.0078: S2 ~546 rows x .015 x .000452 + D2 ~1100 x .012 x .000220 + S3 191 x .013 x .000465. | (1) Sol answered at least 95% of the covered test questions. (2) Free: on the test stated-fact rows of these subsets (about 56 rows, scored on the raw routed answer before the facts rule), mean item change >= 0 and no category with a net negative item sum. (3) Leaderboard: keep a category only if its decoded delta vs C1 is >= +.001. Caveat: the 0.25 weight was picked among 4 blends on validation. | $0 extra. The test run is already running, about $10-25 on the OpenAI ledger (cap $45; $14.10 spent at 23:37). | Run: sibling (running). Build, gate and file: Claude here. Upload: user. |
| A2 | **C1 micro bundle.** combo3 plus only the stated-fact transfers from `r86/dsc`: B_fact 7 rows (0012 bird 1.19 m, dragon 0.75 m), C_readme 3 (small bird 0.94 m), D_depthid 2 (0026 person 1.3 m/s). Also the audit micro-fixes: simulation_0020 rescale (3 D2 rows) and S2 constant-acceleration pooling (~30 rows). **No A_qpool rows and no E_kin rows.** | +.001 (0 to +.002) | Read per category vs combo3. Revert a category if it drops. Each category has under 10 changed rows except S2, so only a drop is readable. | $0, CPU | Claude here (rebuild without A_qpool/E_kin), user upload |
| A3 | [lead] **Argon as third family.** Median of (base, Sol, Argon) on the same rows as A1. Validation, non-lab: +.0167 [+.003, +.029] vs +.0094 for Sol alone; S3 sim +.030, D2 +.027, D3 −.005 (D3 excluded). | +.0015 over A1 (0 to +.003) | Before any test spend, the median must beat A1 by >= +.005 on validation non-lab rows (true now: +.0073), and on test facts must not be below A1. Leaderboard: keep a category if it reads >= +.001 vs A1. | Needs a **Gemini top-up of about $12-15** (batch, medium thinking cap, ~368 sim+internet videos; only ~$3 is left). User decision. | User approves. Claude here runs `research/newmodels/gemini_batch_direct.py`. |
| A4 | [lead] **Meta Muse Wonder validation pilot.** The hinge test. Same frames and questions as the Sol and Argon pilots. | EV about +.001. Only route to a step change, and only if it passes and the user then funds about $60 for test. | PASS only if direct MRA on 159 is >= .80 (Claude .765), OR median (base, Sol, Muse) on non-lab is >= the A1 blend +.010 with clip-bootstrap lower bound > 0. Otherwise stop. | About $4-6 of new money plus an OpenRouter key. About 1 h of work to point `run_openai_direct.py` at OpenRouter. | User approves. Claude here. |

Nothing else for Track A survived. Do not spend the remaining Claude budget (about $50) unless a new lever passes a
pre-registered gate. Every Claude-side variant (more runs, xhigh, re-asks, per-question, sibling views, AABB prompt)
has lost or saturated.

### Track B (detail in section 3)

| # | Lever | Adjusted gain | Kill test | Cost | Owner |
|---|---|---|---|---|---|
| B1 | **One bundled upload, read per category.** S3 = v5 MAIN L1 (lab emulator). D3 = v5 MAIN L2' (fixed lab camera, Qwen member). D2 = v5plus L6s + L4 (post-hoc, so read on its own). S2 = pseudo-label routing for S2 only (the salvage both skeptics agree on). Plus the **clamp: car width 1.5-2.3 m and person height 1.50-2.00 m only; exclude "toy"; drop car length and car height.** | +.015 central (+.007 to +.025): v5 MAIN ~+.008, S2 routing ~+.005, L6s/L4 D2 ~+.003, clamp ~+.004, minus overlap. | Keep each category whose read is >= its v3 score + .001 (S2 .558, D2 .663, S3 .620, D3 .641). Otherwise revert that category to v3. | $0, CPU; 1 slot | Claude here builds (`trackb_v5/build_v5.py` + routing table + `guard_tb.py` restricted), user uploads |
| B2 | **TB-1 folded into the ctx Colab run.** Preset "ctx", already on `main` (commit f4f7341), with `CTX_MODEL = "Qwen/Qwen3.8-27B-FP8"` and `CTX_FALLBACK = "Qwen/Qwen3.6-27B-FP8"`. The ta stage is TB-1's mechanism: one thinking request per video with all questions, returning spec, tracks and its own answer, run through our geometry. It adds context re-measurement (cx) and SAM 2 on its boxes (Argon Idea 3). | Conditional on PASS: +.04 (+.02 to +.07) over B1. P(PASS) about .35, so EV about +.014. | The pre-registered ctx kill test (`research/trackb_next/RESULT.md`): validation macro >= cvq_geo + .03 with CI lower bound > 0; size/distance rows >= +.05; facts not worse; LOVO re-selection >= +.010. Model choice is label-free: keep Qwen3.8 if the 2-video smoke loads, writes 2/2 videos and retries at most 1; otherwise revert to Qwen3.6. Amendment (model id only) is made here, before any output exists. | $0. GPU about 3.5 h (cap 7 h). | User on Colab; Claude here runs `evaluate_ctx.py --lovo` |
| B3 | If B2 passes: 2 more ta passes on test, for 3-run medians of ta_direct / ta_geo. | +.005 to +.01 over B2 | LOVO with rules >= B2 + .005 | GPU about 4 h | User on Colab; Claude here |

### Day-by-day schedule (UTC days; 5 uploads per day shared by both tracks; "spare" means do not invent an upload)

| Day | Uploads | Work |
|---|---|---|
| **Oct 15** | 1: A combo3 (only if it has no score yet; it is the base for every read). 2: A C1 (A2). 3: A C1 + Sol blend (A1), only after the free fact gate passes; read as upload 3 minus upload 2 per category. 4: B B1. 5: spare. | Sol test run finishes (~00:30). Claude here builds C1 and A1 and runs the gate. User starts the ctx smoke (2 videos), then the full ctx run. **User decides on the Argon top-up (A3) and the Muse pilot (A4) by evening.** User makes the repo private and emails the organizers. |
| **Oct 16** | 1: A, only if A1 read mixed within a category: split it (S2 sim vs S2 internet; D2 sim vs D2 internet). 2: B B2, if ctx PASSed and the candidate is built. 3-5: spare. | Claude here runs the ctx kill test. If funded: Argon batch submitted (can take up to 24 h) and the Muse validation pilot run. |
| **Oct 17** | 1: A C2 = combo3 + adopted categories (C1, A1). 2: A A3 (median with Argon), only if its validation gate passed and test answers are in. 3: B B2 if not uploaded on Oct 16. 4-5: spare. | If B2 passed, user starts B3 (2 ta test passes). If Muse passed, ask the user about funding the test run (~$60). |
| **Oct 18** | 1: A, Muse candidate only if funded and gated. 2-5: spare. | If ctx failed for a technical reason (parse rate < 90% or mostly truncated thinking), fix and rerun once. If it failed on quality, stop Track B model work. |
| **Oct 19** | 1: B B3 (medians), if run. 2-5: spare. | |
| **Oct 20** | 1: A C3 = all adopted levers (last day for new mechanisms). 2-5: spare. | Freeze code paths. |
| **Oct 21** | Up to 3: A single-category precision reads, only for a lever whose adoption is within ±.001. 4: B FB = best per category. 5: spare. | |
| **Oct 22** | 1: A F (final composite). 2: A F minus its riskiest bundle (both observed). 3: A re-upload whichever of the two scored higher, so it is the latest. 4: B re-upload FB. 5: spare. | |
| **Oct 23** | Re-upload F / FB only if anything changed. Nothing after F. | |
| **Oct 24 00:00-11:59 UTC** | Emergency only, and only if the organizers confirm the server honours AoE. | |

Planned uploads: about 15-20 of the ~45 available. The rest stay unused on purpose. Diagnostic zeroing uploads (K1/K2)
have no gain and no paid lever left to gate, so they are not scheduled.

---------------------------------------------------------------------------------------------------------------------

## 3. Track B plan to >= .667

**Arithmetic.** From .621, .667 needs +.046.
- B1 (free) gives about +.015, to about .636.
- The remaining ~+.03 can come only from better open-model measurements. trackb_v5 RESULT.md and loss_audit section 7
  show the gap is target-segment measurement on 2D simulation, not post-processing.
- B2 must therefore pass its kill test **and** add at least +.03 over B1. With P(PASS) about .35 and a conditional
  +.02 to +.07, P(>= .667) is about .25-.3.
- Note: .667 is now about rank 18. Top-10 is .7128 (snapshot Oct 14 21:00Z) and is still rising.

**Steps:**
1. **Oct 15: B1 upload** (one slot, read per category). Built on CPU by Claude here. Notes:
   - Do not use the 4-category pseudo routing. With the family rules it loses in D2 (−.005) and D3 (−.011).
   - Keep the v5 sets in D3 (L2'). Routing has no qwen_geo in the D3 lab cells.
   - The S2 routing spills about 60 rows into other categories through the pool rule. Accept that, but list it in the
     build log.
   - Clamp: car width plus person height only, with a "toy" exclusion. The classes are chosen from a-priori ranges,
     checked against stated test priors and validation labels. Do not choose them from Track A answers (the Track B
     clean-input norm).
   - Disclose the pseudo-label (Track A) selection of the S2 sets in the technical report, as the FAQ requires.
2. **Oct 15 (user, Colab): ctx run with Qwen3.8-27B-FP8.**
   - Steps: `research/trackb_next/RUN_INSTRUCTIONS.md`. Change only `RUN_PRESET`, `CTX_MODEL` and `CTX_FALLBACK`.
   - Run the 2-video smoke first. Apply the label-free model rule from B2: keep Qwen3.8 if the smoke loads, writes 2/2
     videos and retries at most 1; otherwise revert to Qwen3.6.
3. **Oct 16 (Claude here):** `evaluate_ctx.py --root <outputs/trackb_ctx> --lovo`, which applies the pre-registered
   test.
   - PASS: build `trackB_cand_ctx.csv`, re-selecting the per-category sets with the new members under LOVO, on top of
     B1's adopted categories. Upload as B2.
   - Only `ta_direct` is strong: add it as an S3/D3 member under the same LOVO rule.
   - FAIL on quality: stop model work. Track B ends at about .63-.64.
   - FAIL on parsing or truncation: one fixed rerun by Oct 18.
4. **Oct 17-19 (only after a PASS):** B3, 3-run medians.
   - Optional and not counted: a GLM-5.3-Flash hosted single-model pilot (MIT, pinned to an FP8 host,
     reasoning_effort "high"), only if the user funds about $5-10 and confirms the hosted-open-weights reading of the
     rules.
5. **If someone later wants the TB-1 port as written** (`research/r86/trackb_opt`, unchanged `run_claude.py`), first:
   - push it to GitHub (it is untracked);
   - resolve the conflict between "All coordinates you give are pixels" and the appended 0-1000 note;
   - raise max_tokens to about 48k;
   - pass reasoning_effort explicitly.

   Run it only if ctx failed for a reason the v1 prompt avoids. Otherwise it repeats ctx's ta stage.
6. **Oct 21:** FB = best per category among v3/B1/B2/B3. Re-upload it Oct 22 so it is also the latest.

---------------------------------------------------------------------------------------------------------------------

## 4. Do not do (refuted or already failed), one line each

Track B
- **"Track A v1 pipeline on an open frontier VLM (Qwen3.8 / Kimi K3)" as a new item:** duplicate of TB-1 and trackb_opt.
  Its gate goes into B2.
- **Kimi K3 hosted (any use):** about $60-170 per test pass with no budget line; its license is custom, not MIT.
- **4-category pseudo-label routing (v4):** with the family rules it is +.0085 [−.025, +.043] and loses D2/D3, so it
  fails its own check. Only the S2 part is kept (in B1).
- **Slot-policy proposal:** identical to `upload_plan_r86.csv`, so it adds nothing.
- **TTA pointing (keyframes x crops into SAM 2):** the seed-diversity proxy (cv vs cvq) gives 0. Gross misses are
  extents on the right instance, not seeding. About +.002.
- **Swapping the notebook's Qwen3-VL/Qwen3.5 members to Qwen3.8:** qwen35 was already a member (.481). L5 search failed
  LOVO. This is a weaker form of B2.
- **TB-2 larger hosted open models as median members:** qwen3.8-flash is Alibaba's production API, not open weights.
  Wider medians failed LOVO. Needs new money. At most a GLM pilot after a B2 PASS.
- **TB-3 SAM 2 on TB-1 boxes as a second geometry member:** 89-94% of motion tracks carry no box. The analogous
  log-median (qwen_geo + cvq) loses .015.
- **TB-5 LoRA on Blender renders:** this is Argon Idea 2. Simulated-world training (CaW-9B) shows no step change.
  It cannot finish by Oct 22.
- **Scene-consistency pooling on Track B answers (famcons-B):** it overrides the 1.6x own-vote guard. Both validation
  rows it touches lose (1.6 -> 0 items).
- **Twin/render pooling (L3), twin-mask snapping (L6), wider member sets (L5):** all failed in trackb_v5.

Track A
- **Open-model votes in the 3D non-lab median (TA-1):** these votes already exist (qwen/gemma/qwen35). They score
  −.002 to −.010 per row on 3D non-lab facts, too inaccurate.
- **Argon as replacement or 4th vote:** direct .762 = Claude; med4 +.0008 [−.004, +.005]; gm −.033. Done tonight.
  Only its third-family use (A3) is left.
- **Decorrelated-member gate:** duplicates the evaluator's kill test, and its thresholds are looser than the MRA
  simulation supports (enssim.py).
- **Monocular depth for unanchored lab objects:** only about 36-38 scored rows are really unanchored; the rest are
  fixed by labsize/labdist or are name-matching cases. About +.0004.
- **Zoom-hybrid extent re-measure:** validation change on S2 sim / D2 sim is exactly 0. All the gain was on internet
  rows. About +.001.
- **Question-text pooling across cameras (A_qpool, 21 rows):** about 13 rows undo verified decisions (0017 panel,
  rock, door coin flip, TV stand, deer), and one row is a known loss.
- **E_kin scripted-acceleration timing (7 rows):** +.0001, and its sign depends on an untested Blender convention.
- **Lab cross-render median as a D3 read:** +.0006 at best, and the same rule lost .035 per row on Track B validation.
- **Lab label noise conditioned on the depth reading:** research lead only, +.0006, no validation rows.
- **Kind-level diagnostic uploads K1/K2:** gain 0, and no paid lever is left that needs a bucket gate.
- **Failed tonight (Gemini/Argon items, verified):**
  - global spline derivatives: all 4 variants FAIL;
  - fixed uncertainty router: stage 1 and stage 2 FAIL, +.0001;
  - Depth Pro FOV: median focal error .33, FAIL;
  - world-AABB prompt: 3/6 clips, FAIL.
- **Program-of-thought:** no result on disk. Our geometry already does the arithmetic in code, and it is not counted.
- **Earlier failures (summary_for_gemini section 5):** do not revisit them. They include more Claude runs, xhigh,
  re-asks, the agent loop, per-question prompts (−.073), sibling-view context (−.064), MoGe FOV, shading, the asset
  table and routers.

---------------------------------------------------------------------------------------------------------------------

## 5. Combined forecast (no row counted twice)

**Track A** (base combo3, expected .820, range .817-.822; nothing here has a leaderboard read yet)

| Item | Rows it changes | Central | Range | Note on overlap |
|---|---|---|---|---|
| C1 micro bundle (A2) | ~45 (stated-fact transfers + 0020 + constant-acceleration pooling) | +.001 | 0 to +.002 | Fact rows are excluded from A1, so they are disjoint. |
| Sol blend (A1) | ~1,800 non-fact rows S2 / D2 non-lab / S3 sim | +.004 | 0 to +.008 | |
| Argon third family (A3), only if funded | the same rows as A1 | +.0015 | 0 to +.003 | Counted only as the increment over A1. |
| Muse pilot (A4), only if funded | — | 0 | (+.01 only if it passes and the test run is funded) | Not in the central number. |
| **Total** | | **~.825** (.8265 with A3) | **.818-.832** | P(>= .86) < 2%; P(>= .835, today's 5th) about 5-10% |

**Track B** (base .621)

| Item | Central | Range | Note on overlap |
|---|---|---|---|
| B1 bundle (v5 S3/D3 lab, S2 routing, D2 L6s/L4, clamp) | +.015 | +.007 to +.025 | L6s is used in D2 only, because S2 uses routing; the clamp rows are inside B1. |
| B2 ctx/Qwen3.8 (TB-1 + Argon Idea 3) | +.014 EV | 0, or +.02 to +.07 on PASS | B2 re-selects member sets under LOVO on the same 2D rows as B1's S2 routing and L6s, so its gain is incremental over B1. It is not added to them. |
| B3 medians | +.002 EV | 0 to +.01 | Only after a B2 PASS. |
| **Total** | **~.652** | .628-.70 | P(>= .667) about .25-.3; P(top 10) < .05 |

**Budget after this plan:**
- Claude about $50: no planned spend.
- OpenAI: about $10-20 left after the Sol test run.
- Gemini: about $3, plus the $12-15 top-up only if A3 is approved.
- New money only on user approval: Muse pilot $4-6 (test run about $60 if it passes); GLM pilot $5-10.
