# Prompt for Gemini Argon: take QuantiPhy Track A from .817 to above .85

Paste everything below the line into Gemini Argon. Give it repo access if it can take it:
https://github.com/VihanAggarwal/quantiphy-challenge

---

You are the lead engineer and researcher on our team for the **QuantiPhy Challenge (NeurIPS 2026), Track A**. Any
model is allowed in Track A.

**Goal: move our leaderboard score from .817 to at least .855. First place is .8536.** The deadline is
**Oct 23, 2026, 23:59 AoE**.
- Small tweaks of +.001 to +.003 no longer matter.
- We need changes worth **+.01 or more each**, or one change to the base predictor worth +.03.

You are a newer, stronger model than the ones we have tried, so one of your jobs is to **test yourself as the answerer**
(Phase 1).

## 0. How to work (read this twice)

- **Report only what you actually ran.** For every result, give the exact command, the key output lines and the
  commit hash.
  - A previous AI helper claimed it had pushed a branch that did not exist.
  - It also "improved" answers by reverting rows to raw values.
  - We check everything.
- If you cannot run code, say so plainly. Then deliver scripts plus exact run instructions, and label every number
  "expected, not measured".
- Fix a pass bar **before** running each experiment (a kill test). If it fails, log it and move on. Don't re-tune until
  it passes.
- Work on a branch `argon/<topic>`. Never push to `main`. Never upload to the leaderboard; Vihan uploads.

## 1. The task

Each test question gives you:
- a short video (1 to 10 s);
- one exactly-true **prior** about one object, e.g. `speed of the bird = 6 m/s`, `height of the table = 0.75 m`, or
  `gravity acc = 9.8 m/s^2`;
- for 3D videos, a `depth_info` text giving object-to-camera distances at one or two times;
- a question asking for a **size, distance, speed at time t, or acceleration at time t** of an object, in a stated unit.

The scoring metric is **MRA (mean relative accuracy).**
- An answer scores the fraction of tolerances {<90%, <80%, ..., <10%, <5%} relative error it meets.
  - Under 5% = 1.0, 5 to 10% = .9, 10 to 20% = .8. A 50% error scores .4.
- Answers are averaged within 4 categories, then over the 4. S = size prior, D = motion prior; 2 = 2D video, 3 = 3D.
- Scored questions: **S2 553, D2 1137, S3 538, D3 933.**
- What a fix is worth overall: `rows x average gain per row / (4 x N_category)`.

The data:
- **Test:** 3,289 questions, 568 videos. Sources: Blender simulation 1,633, real lab 806, internet 420, segmented
  copies 430.
- **Validation:** 159 labelled questions from 24 videos, all 24 also in test. Validation gains under .03 are noise.

## 2. Where we stand

| File | S2 | D2 | S3 | D3 | Overall |
|---|---|---|---|---|---|
| `submissions/trackA_cand_combo2.csv` (best scored) | .827 | .863 | .767 | .811 | **.817** |
| `submissions/trackA_combo3_on_combo2.csv` (uploaded Oct 14) | ~.834 | .863 | ~.770 | ~.814 | ~.820 expected |

- **Leaderboard:**
  1. ~.8536
  2. Cogworks RSI .8498
  3. Blindfolded .8293
  4. iMak .8231
  5. szerlok .8195
- **Key fact:** on the validation videos the top two teams score about **.87** and we score **.828**.
  - Their lead is *slightly better answers on almost every question*, not one trick.
  - So the biggest remaining lever is **the base predictor**.
- **Where we lose points (average score per question, by subset):**

  | Category | Subset (scored rows): mean score | Subset (scored rows): mean score |
  |---|---|---|
  | S2 | simulation (362): .828 | internet (191): .796 |
  | D2 | simulation, static target (719): .851 | everything else (418): .857 |
  | S3 | **simulation (221): .742**, the weakest subset | lab (317): .782 |
  | D3 | lab, static target (334): .799 | lab motion + simulation (599): .805 |

  - Under-10% errors cost almost nothing. **The loss is in 20 to 50% errors and >1.5x misses.**

## 3. Our pipeline

1. **Annotation:** Claude Opus (high reasoning) gets 16 to 32 labelled frames (854 px) and all of a video's questions
   in **one request**. It returns pixel tracks per object plus its own direct numeric answer (`qp/claude_annotate.py`,
   `scripts/run_claude.py`).
2. **Geometry solver** (`qp/geometry.py`):
   - 2D: the prior sets metres per pixel.
   - 3D: pinhole camera with depth_info as Euclidean range; focal length solved from the prior.
   - Lab camera: f ≈ 722 px at 1280 px width.
3. **Routing:**
   - 2D uses geometry.
   - 3D simulation uses Claude's direct answer (median of 3 runs).
   - Lab uses geometry for sizes, and the direct answer plus a label-noise model for motion.
4. **Model-free "scene family" rules** (`qp/postprocess.py`, our biggest win at +.026):
   - copy stated facts across clips of the same scene;
   - fix per-clip scale;
   - pool answers.
5. **How the labels were made** (from the dataset paper):
   - **Simulation:** depth = range to the Blender object origin; sizes = world bounding box; speed = backward
     difference; acceleration = d|v|/dt.
   - **Lab:** hand-clicked centres, depth from a ToF camera, forward differences at 25 fps.

## 4. Hard rules (breaking these can disqualify us)

1. **No test labels in any form.** Every answer must come from test inputs plus models and code.
2. **Never copy validation labels into test answers, and never tune per-row values to match validation labels.**
   Validation only measures *general* methods.
3. Don't use the dataset paper's Table 6 lab prop sizes. We are waiting on organizer approval.
4. **API keys** live only in the gitignored `.env`. Never print, log or commit them.
5. **Paid runs need Vihan's OK first.**
   - Gemini key: about $7.50 left under its $15 ledger cap (`budget/ledger_gemini.jsonl`).
   - Claude: about $50 left.
6. **Never commit large files** (frames, videos, pickles). `.gitignore` already covers the usual folders.

## 5. Already tried. Do not re-propose these unless you show our test was wrong

Details are in `research/consult/summary_for_gemini_2026-10-13.md` and `research/PROBES.md`.

- **Other models:**
  - GPT-6 Astra: .747 vs Claude .757, no ensemble gain.
  - **Gemini 3.1 Pro: .565** on validation (native video), and mixing it in hurt (−.075).
  - Claude Fable: .749 vs .782.
- **More runs or more reasoning:**
  - more than 3 Claude runs: +.005 at 7 runs;
  - xhigh effort: worse.
- **Other ways of asking Claude:**
  - agent loop with measuring tools: no better, 4x cost;
  - verify pass with zoomed crops;
  - re-asks;
  - high-res frames;
  - **one question per request: −.073**;
  - **extra sibling camera views in the prompt: −.064**.
- **Camera and 3D methods:**
  - foundation-model camera FOV (MoGe-2): −.17 to −.30;
  - pooled focal length per camera group;
  - geometry instead of direct on 3D simulation: −.19 per row;
  - lab 3D ballistic fits: fitted g of 9.7 to 16.7;
  - generic lab 3D reconstruction: .60.
- **Tracking:** dense tracking, SAM masks, GrabCut/KLT. Our tracks are already within 0.44% of exact masks.
- **Answer adjustments:**
  - MRA shading (shrinking answers);
  - cross-clip asset tables;
  - learned per-question routers: −.017 to −.047 under leave-one-video-out;
  - kinematic smoothing.
- **Label-convention tweaks:**
  - depth as optical-axis Z;
  - lab near-surface depth;
  - lab timing shifts;
  - uniform lab speed factors;
  - Blender label emulation on S2.

## 6. The mission, in phases

### Phase 0: orient (free)

- Read, in order:
  1. `research/consult/summary_for_gemini_2026-10-13.md`
  2. the bottom third of `research/PROBES.md`
  3. `docs/HANDOFF_SUBHI.md` (setup)
  4. `qp/claude_annotate.py`, `qp/geometry.py`, `qp/postprocess.py`
- Set up the environment:
  ```bash
  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
  .venv/bin/python scripts/download_data.py
  ```
- Replay Claude's past outputs for free (records are committed under `runs/*/*/records/`):
  ```bash
  ANTHROPIC_API_KEY="" ANTHROPIC_BASE_URL="http://127.0.0.1:9" QP_LEDGER=/tmp/x.jsonl
  ```
- Print the baselines you must beat on the 52 validation questions from 3D non-lab clips:
  `.venv/bin/python research/perq/evaluate.py`

### Phase 1: test yourself as the base predictor (highest value)

The base predictor is the only lever big enough to close +.035.

1. **Pilot (about $1.50, ask Vihan first).**
   - Run `scripts/run_gemini_direct.py --split val_hires --model <Argon model id> --input frames` on the **6 videos /
     52 questions of 3D non-lab clips** (`--videos ...`).
   - Repeat with `--input video --fps 12`.
   - Use the same high thinking and high media resolution as the 3.1 Pro pilot.
   - Report:
     - MRA vs the Claude single-run and 3-run-median baselines from Phase 0;
     - the median |log(Argon / Claude)|. Low correlation plus similar accuracy means an ensemble gain.
   - **Kill test:**
     - pass if Argon alone ≥ Claude 3-run median + .015 on the 52;
     - or pass if the median of {3 Claude runs + Argon} ≥ the 3-run median + .015;
     - and in either case, better on at least 4 of 6 clips.
2. If it passes, run all 24 validation videos (about $6) with the same pass bar, per category.
3. If that passes too, write a cost estimate for the 3D non-lab test videos (123 videos) and stop. Vihan decides the
   spend.
4. Optional: also test Argon as the **annotator** that produces pixel tracks for our geometry on 2D clips. Use the
   Claude prompt from `qp/claude_annotate.py` and the same JSON schema, then score the geometry answers. Same style of
   kill test.

### Phase 2: error audit (free, run in parallel with Phase 1)

- Take the validation rows scoring under .6. On test, take the rows where the 3 Claude runs disagree most
  (`runs/test_3dnl_*`, `runs/test_v1_high_854`).
- Classify each miss:
  - wrong object;
  - wrong dimension;
  - wrong time;
  - scale error;
  - bounding box vs visible extent;
  - unit slip;
  - label oddity.
- Look at the frames yourself: you are a vision model.
- We need **one systematic cause covering 100+ rows**.
- Held-out check: **the 106 exactly-known stated-fact rows** in test scene families. These are questions whose answer
  another clip states as its prior. Harness: `research/simfov/evaluate.py`, `qp/postprocess.py` "facts".

### Phase 3: your own ideas (must pass the protocol below)

- The hottest target is **S3 simulation sizes (221 rows, .742)**: labels are world bounding-box dimensions and the
  camera FOV varies 8 to 103 degrees.
- Then S2 internet (191 rows, .796) and D3 lab static (334 rows, .799).

## 7. Fact-check protocol: required for every idea, before any spend

1. **Claim:** one sentence giving the mechanism and the subset it improves.
2. **Evidence:** one of
   - (A) a published result on QuantiPhy or a near-identical task;
   - (B) a published result on a related task;
   - (C) a first-principles argument;
   - (D) speculation.

   For A and B, give the URL and quote the exact number.
3. **Self-refutation:** the strongest reason it won't work. Check it against section 5.
4. **Gain arithmetic:** `rows x item gain / (4 x N_cat)`, realistic not best-case. It must be ≥ +.01.
5. **Kill test:** a cheap check with no test labels and a pass bar fixed in advance.
6. **Cost:** dollars and hours.
7. **Confidence:** 0 to 100% that it passes, with one line of justification.

## 8. Deliverables

- **Code:** under `research/argon_<topic>/`. Add a results section at the end of `research/PROBES.md` with
  numbers, rows affected and the kill-test verdict.
- **Upload candidates:** for anything that passes, build the file on top of the current best:
  ```bash
  .venv/bin/python research/merge/merge_skip.py submissions/trackA_cand_argon_<topic>.csv \
      submissions/trackA_combo3_on_combo2.csv <file your predictions started from> <your preds.csv>:<CATS>
  ```
  `submissions/` is gitignored, so use `git add -f`.
- **Final report:**
  1. a table of every experiment: idea, cost, kill test, result, PASS/FAIL;
  2. the candidate files with their expected gain per category;
  3. the branch name and commit hash;
  4. a plain statement of whether .855 looks reachable, and which single result it depends on.
