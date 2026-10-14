# QuantiPhy Track A: handoff for Subhi

Hi Subhi. This is everything you need to help push our QuantiPhy Challenge entry from **.817 to first place (.8536)**.
Read sections 1 to 4 before touching code. Section 6 has the work.

- **Repo:** https://github.com/VihanAggarwal/quantiphy-challenge. If you get a 404, ask Vihan to add you as a collaborator.
- **Competition:** https://quantiphy.stanford.edu/competition/index.html. Deadline **Oct 23, 2026, 23:59 AoE**.

---

## 1. The task in one minute

Each test question gives you:
- a short video (1 to 10 s);
- one exactly-true **prior** about one object, e.g. `speed of the bird = 6 m/s`, `height of the table = 0.75 m`, or
  `gravity acc = 9.8 m/s^2`;
- for 3D videos, a `depth_info` text giving object-to-camera distances at one or two times;
- a question asking for a **size, distance, speed at time t, or acceleration at time t** of some object, in a stated unit.

The scoring metric is **MRA (mean relative accuracy).**
- One answer scores the fraction of 10 tolerances it meets: <90%, <80%, ..., <10%, <5% relative error.
  - Under 5% error = 1.0, 5 to 10% = 0.9, 10 to 20% = 0.8, and so on. A 50% error is worth 0.4.
- Answers are averaged within 4 categories, then the 4 averages are averaged. S = size prior, D = motion prior;
  2 = flat 2D video, 3 = 3D video.
- Scored questions per category: **S2 553, D2 1137, S3 538, D3 933.**
- How much a fix is worth overall: `rows changed x average gain per row / (4 x N_category)`.
  - Example: fixing 50 S3 rows by +0.2 each = 50 x 0.2 / (4 x 538) = **+.0046**.

The data has 3,289 test questions over 568 videos. Sources:
- Blender simulation: 1,633
- real lab recordings: 806
- internet clips: 420
- segmented copies (the same video with the background removed): 430

The validation set is 159 labelled questions from 24 videos, and all 24 videos are also in the test set.

## 2. Where we stand (Oct 14)

| File | S2 | D2 | S3 | D3 | Overall |
|---|---|---|---|---|---|
| `submissions/trackA_cand_combo2.csv` (best scored) | .827 | .863 | .767 | .811 | **.817** |
| `submissions/trackA_combo3_on_combo2.csv` (uploaded Oct 14) | ~.834 | .863 | ~.770 | ~.814 | ~.820 expected |
| 1st place target | | | | | **.8536** |

- **Gap: about +.034 overall.** That is roughly +.07 on both S3 and D3, or +.035 in all four categories.
- **Leaderboard (Oct 12):**
  1. Perch AI .8517
  2. Cogworks RSI .8498
  3. Blindfolded .8293 (copied validation answers)
  4. iMak .8231
  5. szerlok .8195
  6. Quantumonster .8191
  7. reasoning_wrt .8121

  Vihan says 1st is now .8536.
- **The key fact:** on the validation videos the top two score about **.87** and we score **.828**. Their lead is *slightly
  better answers on nearly every question*, not one trick. No write-up or code from any top team exists.
- **Where we lose points (average score per question, by subset):**

  | Category | Subset (scored rows): mean score | Subset (scored rows): mean score |
  |---|---|---|
  | S2 | simulation (362): .828 | internet (191): .796 |
  | D2 | simulation, static target (719): .851 | everything else (418): .857 |
  | S3 | **simulation (221): .742**, the weakest subset | lab (317): .782 |
  | D3 | lab, static target (334): .799 | lab motion + simulation (599): .805 |

  - Errors under 10% cost almost nothing.
  - **The loss is in 20 to 50% errors and >1.5x misses.**
  - About 12% of validation rows score under .5.

## 3. Ground rules (hard; breaking these can get us disqualified)

1. **Never use test labels in any form.** Every answer must come from the test inputs (video, prior, depth_info,
   question) plus models and code.
2. **Never copy validation labels into test answers, and never tune a per-row value to match a validation label.**
   - Validation is only for measuring whether a *general* method helps.
   - A rule chosen by matching labels on specific validation questions was reverted once (qid 1874). Don't repeat that.
3. **Don't use the paper's Table 6 lab prop sizes.** We are waiting on organizer approval.
4. **Uploads:** 5 per UTC day, shared across both tracks. **Vihan uploads.** Send him CSVs; don't upload yourself.
5. **API keys:**
   - Keys live only in a local, gitignored `.env` (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`).
   - Never commit, print or paste them anywhere.
   - Paid runs need Vihan's OK first. About $50 of Claude budget is left, tracked by `qp/budget.py` in `budget/ledger.jsonl`.
6. **Track B** (open-weight models only) is a separate entry, currently .621. This handoff is about **Track A**.

## 4. Setup

```bash
git clone https://github.com/VihanAggarwal/quantiphy-challenge.git && cd quantiphy-challenge
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/download_data.py        # validation + test videos + template into data/ (~0.5 GB)
.venv/bin/python -m pytest -q tests               # optional sanity check
```

- **Free replays (no API calls):** all paid Claude outputs are committed under `runs/*/*/records/*.json`. You can re-run
  every post-processing step for free. To make sure nothing gets billed by accident:
  ```bash
  ANTHROPIC_API_KEY="" ANTHROPIC_BASE_URL="http://127.0.0.1:9" QP_LEDGER=/tmp/scratch_ledger.jsonl .venv/bin/python ...
  ```
- **Score a validation prediction CSV** (columns `id, parsed_value`):
  `.venv/bin/python scripts/score.py runs/<run>/val.csv`
- **Turn predictions into an uploadable file** (checks ids, order and that values are non-zero and finite):
  `.venv/bin/python scripts/make_submission.py preds.csv submissions/out.csv`
- **Apply your change onto the current best:**
  - `research/merge/merge_skip.py OUT BASE REF CAND[:CATS] ...` copies the rows where CAND differs from REF onto BASE.
  - Only the categories you list are touched.
  - Rows already changed in BASE are kept as BASE.

## 5. Read these first (in this order)

1. `research/consult/summary_for_gemini_2026-10-13.md`: the whole pipeline, what worked, and what failed *and why* (15 min).
2. `research/PROBES.md`: the lab notebook. Every leaderboard upload, its per-category score, and every experiment.
   **The bottom third is the most recent.**
3. `docs/TRACK_A.md` and `README.md`: how the pipeline runs. README numbers are older.
4. Code:
   - `qp/claude_annotate.py`: prompt, frames, request.
   - `qp/geometry.py`: pixel to metric solver.
   - `qp/postprocess.py`: scene-family rules, our biggest win.
   - `scripts/run_claude.py`: runner.
5. `research/path85/PLAN.md`: the last big search for +.035 and what came out of it.

**Pipeline in short:**
1. Claude Opus (high reasoning) gets 16 to 32 labelled frames and all of a video's questions in one request. It returns
   pixel tracks per object plus its own direct numeric answer.
2. 2D questions use geometry: the prior sets metres per pixel.
3. 3D simulation uses Claude's direct answer, as a median of 3 runs.
4. Lab uses geometry for sizes and the direct answer plus a label-noise model for motion.
5. Model-free "scene family" rules then copy stated facts across clips of the same scene, fix per-clip scale and pool answers.

**Already tried. Please don't redo these without a specific reason our test was wrong:**
- **Other models:** GPT-6 Astra, Gemini 3.1 Pro, Claude Fable.
- **More runs or more reasoning:** more than 3 Claude runs, xhigh effort.
- **Other ways of asking Claude:**
  - an agent loop with measuring tools;
  - a verify pass on zoomed crops;
  - one question per request (−.073);
  - extra camera views of the same scene in the prompt (−.064);
  - re-asking flagged rows;
  - high-res frames.
- **Camera and 3D methods:**
  - foundation-model camera FOV (MoGe-2), −.17 to −.30;
  - a pooled focal length per camera group;
  - geometry instead of the direct answer on 3D simulation (−.19 per row);
  - lab 3D ballistic fits.
- **Tracking and smoothing:** dense tracking / SAM masks, kinematic smoothing.
- **Answer adjustments:** MRA "shading" (shrinking answers), cross-clip asset tables, learned per-question routers.
- **Label-convention tweaks:**
  - depth as optical-axis Z;
  - lab near-surface depth;
  - lab timing shifts;
  - uniform lab speed factors;
  - Blender label emulation on S2.

## 6. What to work on (ranked)

None of these is proven. Each has a **kill test**, a cheap check with no test labels and a pass bar fixed *before* you
run it. If it fails, log it in `research/PROBES.md` and move on. Don't tune until it passes.

**A. Error audit of the worst subsets (free, do this first).**
- Take the validation rows scoring under .6 and, on test, the rows where the 3 Claude runs disagree most (spread in
  `runs/test_3dnl_*` and `runs/test_v1_high_854`).
- Classify each miss by cause:
  - wrong object;
  - wrong dimension (width vs height vs length);
  - wrong time;
  - wrong scale;
  - bounding box vs visible extent;
  - unit slip;
  - label oddity.
- We only need **one systematic cause covering 100+ rows** to get +.01.
- Kill test: the fix must also raise the score on the **106 exactly-known stated-fact rows** in test scene families.
  These are questions whose answer another clip states as its prior; see `qp/postprocess.py` "facts" and
  `research/simfov/evaluate.py` for a ready-made harness.

**B. A better prompt for 3D simulation sizes (S3 simulation, 221 rows at .742, the biggest hole).**
- Labels here are Blender world bounding-box dimensions. Depth = distance from the camera to the object's origin.
  The camera field of view varies from 8 to 103 degrees.
- Idea: have Claude explicitly compute
  1. the prior object's pixel size and depth;
  2. the implied focal length;
  3. the target's pixel size, then answer;
  4. and sanity-check that answer against real-world object sizes.

  This can be a `prompt_version` "v3" in `qp/claude_annotate.py`.
- Pilot on the 52 validation questions from 3D non-lab clips (about $3, ask Vihan).
- **Kill test:** direct-answer score at least +.015 above `runs/val_hr_v1_high` on those 52, and better on most of the
  6 clips. Scripts to copy: `research/perq/evaluate.py`, `research/ctxpilot/run.py`.

**C. S2 internet (191 rows, .796) and D3 lab (334 static rows, .799).**
- Same recipe as A: find a recurring failure, fix it with a rule or prompt, and check it on held-out stated facts.
- Lab scene background (`research/labsize`, `research/labnoise`, `research/path85_lab`):
  - the camera focal length is known (~722 px at 1280 px width);
  - labels come from hand-clicked centres plus ToF depth plus forward differences at 25 fps.

**D. Bring new ideas.** Anything that makes the *base* answers about 4% better nearly everywhere is what the leaders
have. Whatever you propose, first write down:
- the claim;
- the expected gain using the formula in section 1;
- a kill test with a pass bar.

## 7. How to hand work back

- Work on a branch: `git checkout -b subhi/<topic>`.
- Put your code under `research/<topic>/` and a short result section at the end of `research/PROBES.md`. Include what
  you changed, the rows affected and the kill-test numbers.
- If it passes, build an upload candidate on top of the current best:
  ```bash
  .venv/bin/python research/merge/merge_skip.py submissions/trackA_cand_<topic>.csv \
      submissions/trackA_combo3_on_combo2.csv <file your predictions started from> my_preds.csv:S3
  ```
  The arguments are OUT, BASE (current best), REF (the file you modified) and CAND:CATEGORIES.
  Submissions are gitignored, so add yours with `git add -f`.
- Push the branch and message Vihan. Each day he has about 4 spare uploads for one-change-per-category tests like
  U1 to U4 in `research/PROBES.md`. That's how we tell which change moved the score.

Thank you!
