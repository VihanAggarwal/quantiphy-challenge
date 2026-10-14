# Track B next Colab run: context-aware open annotation (RUN_PRESET "ctx")

Status: PRE-REGISTRATION (written 2026-10-14 before any code for the new run existed and before any output of it).
The diagnosis below (sections 1-2) was run before this kill test was fixed; it chose the run, it is not the test.

## Pre-registered kill test (applies to the outputs of the Colab run; fixed now, before the run)

Held-out data: validation (159 q, 24 clips), answered by the new run on the FULL-RESOLUTION copies (split
`val_hires`, the configuration of the test run); clip bootstrap 2000 x over the 24 clips, 90% CI. Test stated-fact
rows (research/trackb_dense/out/fact_labels.csv, 136 exact values) scored on raw answers (before the facts rule).
Reference member: `cvq_geo` (SAM 2 prompted by Qwen3-VL boxes + CaW fallback) of trackb_v1, scored on the same
validation questions through the full-resolution test run where they match (131 q, `diag_hires.py`) and on the
480p validation run otherwise.

Pre-declared new methods (all with the CaW fallback of run_open_vlm.run_geometry, nothing tuned on validation):
- `ta_geo`   : Qwen3.6-27B Track-A-style annotation (spec + tracks), our geometry.
- `tacx_geo` : ta tracks, size extents / distance points replaced by the context-extent (cx) stage (zoom-refined).
- `samcx_geo`: SAM 2 tracks prompted by the ta boxes for motion, cx extents for sizes / distances.
- `ta_direct`: the model's own answer from the same request.

PASS (the run's outputs may enter a Track B candidate) only if ALL hold for at least one of the four:
1. Validation macro MRA >= cvq_geo + 0.030, and the clip-bootstrap 90% CI of that delta has lower bound > 0.
2. On the validation rows whose target is a size or a distance (the diagnosed failure), item mean >= cvq_geo + 0.05.
3. Stated facts: mean item change over fact rows whose answer the method changes vs cvq_geo is >= 0.
4. Building the candidate: per-category log-median member sets re-selected with the new method(s) available, the
   selection re-run inside leave-one-video-out with the family rules applied, must beat the LOVO macro MRA of v3's
   own selection procedure (old 4 members; .5793 in research/trackb_v5/l5_lovo.log) by >= +0.010 (trackb_v5 rule 4).
Otherwise FAIL: no candidate is built from this run (the outputs are kept for analysis).

Candidate if PASS: `submissions/trackB_cand_ctx.csv` (scripts/make_submission.py), rows changed per category,
expected gain = rows x avg item gain / (4 x N_cat), N = S2 553, D2 1137, S3 538, D3 933.

---------------------------------------------------------------------------------------------------------------------

## 1. Diagnosis: which failure dominates Track B (run before the kill test was fixed)

All on validation (159 q, 24 clips); open-weight outputs of trackb_v1 (/tmp/claude-0/tb3/x/trackb_v1). The Claude
(Track A) annotation of the same questions (runs/val_hr_v1_high) is used ONLY as a diagnostic yardstick inside the
same solver - it never enters a Track B answer, file or parameter.

Commands (outputs in this folder): `diagnose.py` (-> diagnose.log, diag_rows.csv), `diag_px.py` (-> diag_px.log),
`diag_mix_cvq.py` (-> diag_mix_cvq.log), `diag_hires.py` (-> diag_hires.log), `diag_boot.py` (-> diag_boot.log).

### 1a. Members (item MRA; gross = share > 2x off or missing)
| member | MRA | S2 | D2 | S3 | D3 | gross S2 / D2 / S3 / D3 |
|---|---|---|---|---|---|---|
| CaW-9B direct | .545 | .531 | .511 | .558 | .579 | .31 / .38 / .21 / .28 |
| Qwen3.5-27B direct | .481 | .472 | .459 | .419 | .572 | .41 / .38 / .44 / .26 |
| Gemma-4-31B direct | .454 | .403 | .446 | .426 | .543 | .47 / .43 / .49 / .26 |
| Qwen3-VL-32B direct | .397 | .306 | .481 | .344 | .455 | .63 / .43 / .61 / .34 |
| Qwen geometry (raw) | .447 | .375 | .327 | .633 | .453 | .56 / .60 / .19 / .28 |
| cvq geometry (raw: SAM 2 from Qwen boxes) | .510 | .503 | .459 | .637 | .440 | .41 / .46 / .16 / .38 |
| [yardstick] Claude-track geometry | .730 | .709 | .924 | .635 | .653 | .19 / .00 / .23 / .19 |
| [yardstick] Claude direct | .766 | .678 | .911 | .788 | .687 | |
The full-resolution test run scored on the 131 validation questions that are also test questions (`diag_hires.py`):
Qwen geometry raw .556, cvq raw .572, CaW .541 - better than the 480p validation run (.490 / .531), still far from .73.

### 1b. Specs vs tracks: 2 x 2 swap through the same solver (geometry, CaW fallback)
| spec \ tracks | Qwen tracks | Claude tracks (diagnostic) |
|---|---|---|
| Qwen spec | **.507** (S2 .375 D2 .514 S3 .656 D3 .483) | **.733** (.691 / .924 / .674 / .643) |
| Claude spec | .507 | .730 |
- Tracks: +.226 macro, clip-bootstrap 90% CI [+.159, +.305]. Specs: -.000 [-.004, +.003]. Qwen's specs agree with
  Claude's on target kind / prior kind / prior value / time / unit in 97-100% of rows. **The tracks are the failure.**
- Both roles must be fixed: Claude prior track only +.029 [-.025, +.102]; Claude target track only +.053 [+.003, +.109].
- Grounding classes (Qwen vs Claude tracks): wrong object (centre off by more than the object's size) on 17% of prior
  and 14% of target roles; target extents median |log ratio| .27, 74% off by > 15%, 37% by > 50%; motion
  displacements mostly fine (median .02-.03) except the wrong-object rows. Qwen's own extent points are worse than its
  boxes (boxes only: .536 vs .507).
- 3D: S3 is NOT track-limited (Claude tracks .674 vs .656); the Track A S3 lead comes from direct answers (Claude .788
  vs best open .558). D3 gains from tracks (.483 -> .643).

### 1c. With SAM 2 motion (cvq) in place, what is left? (role mixes on the cvq tracks)
| tracks | MRA | S2 | D2 | S3 | D3 |
|---|---|---|---|---|---|
| cvq (SAM 2 prompted by Qwen boxes) | .554 | .606 | .532 | .637 | .440 |
| cvq prior + Claude target (diagnostic) | **.671** | .647 | .743 | .707 | .585 |
| Claude prior + cvq target (diagnostic) | .586 | .609 | .603 | .640 | .494 |
| Claude both (diagnostic) | .733 | .691 | .924 | .674 | .643 |
- Target measurement: +.116 [+.051, +.175]; prior: +.032 [-.007, +.081]. SAM 2 already fixes most prior motion (cvq vs
  Claude prior pixel motion: median |log| .009, 5% > 50% off; Qwen boxes alone: .106, 36%).
- Where the target gain is (item points over cvq): D2 size 6.2 (26 rows), D3 size 6.1 (32), S3 speed 1.5, S2 size 1.1,
  S3 size 1.1, distances 1.9 in total. Largest rows: "side length of the floor tiles" (cvq 10x: a whole floor),
  "orbital diameter of the Io model" (x4: the moon instead of its orbit), slope length, car width / height, lane width,
  pier / steps width, distance between passer and receiver. These are SEMANTIC segments: the open pipeline grounds an
  object NAME on single frames ("the two ends of the width of the {name}"), Claude reads the question in context.
- Clip-level prior failures without a geometry value (14 of 69 2D rows): ruler graduation "calibre = 1 cm"
  (internet_0004), a tiny pedestrian among many (internet_0013, wrong instance), a bubble moving 1.4 mm/s (0196).

**Verdict of the diagnosis**: the dominant Track B failure is the pixel measurement of the asked TARGET segment
(which segment the question means, and its end points), followed by wrong instances; not the specs, and (with SAM 2)
not the prior motion. The direct guesses of open models are weak everywhere (.40-.55) and decide S3.

## 2. Why this run (and not the alternatives)
- `q35` preset (existing, never run): Qwen3.5-27B in the SAME per-frame object-name grounding. It changes the model,
  not the missing context; Qwen3.5/3.6 RefCOCO is ~92 like Qwen3-VL-32B, so the semantic-segment failure stays.
- Stronger pointing / segmentation alone (Molmo2, SAM 3.1): address identity, not "which segment"; SAM 3.1 is a gated
  (manual approval) checkpoint and Molmo2's vLLM path is unverified - risky for an unattended run.
- Chosen: give an open VLM the Track A context. Qwen3.6-27B (Apache-2.0, Apr 2026, `Qwen3_5ForConditionalGeneration`
  = the architecture already run in trackb_v1 with vLLM 0.19.1; RefCOCO 92.5, RefSpatialBench 70.0; FP8 31 GB):
  * **ta**: one request per video, 16 uniform + asked-time frames (max 32, 1024 px, labelled), all questions; the Track A
    annotation recipe adapted to the 0-1000 grounding grid, thinking on; returns spec + tracks + its own answer.
  * **cx**: per size target / size prior / two-object distance, the full question + prior on 3 frames where ta shows the
    object, then on a zoomed full-resolution crop around the two points (Track A's zoom re-measurement idea).
  * **SAM 2 on the ta boxes** (hedge for motion and identity) and hybrids: tacx, samcx, cvqcx (section 13d).
  The prompts contain no example taken from a validation question (generic segment rules only), so validation stays
  a fair held-out measure.

## 3. Implementation and CPU checks (no GPU, no API)
New files only (no existing qp/ or scripts/ file changed): `qp/open/ctx_annot.py` (prompts, multi-image vLLM / HF
backends with per-request thinking, parsing through `qp.claude_annotate.to_annotations` + `qwen_vl.validate_spec`,
cx planning / zoom / mapping), `qp/open/run_ctx.py` (GPU runner, resumable, retry without thinking + JSON schema),
`qp/open/ctx_merge.py` (CPU hybrids + `run_open_vlm.run_geometry`). Notebook: preset "ctx" + section 13d added in
`notebooks/_build_notebook.py` (which also now carries the q35 preset that had been edited into the .ipynb by hand;
the generator test `test_notebook_matches_generator` failed before this change and passes now), regenerated .ipynb.
- `research/trackb_next/test_ctx.py`: 25 tests (grid/pixel/time mapping, unknown frames, outside-grid flags, missing
  questions, unusable replies, JSON inside an unclosed think block, cx items / frames / zoom round trip / choice, prior
  items shared across questions, merge priorities, 480p -> full-res rescaling, real-video request build, run_ctx end to
  end with a mock model incl. resume). All pass.
- `research/trackb_next/dry_run.py` (mock model, 24 real validation videos): **replay** = the mock answers with the
  cached Track A annotation converted to the 0-1000 grid. run_ctx -> ctx_merge -> geometry reproduces the
  Claude-track solve on 157/159 rows (2 tiny differences); ta geometry .715 / ta direct .766 (= Claude direct) - the
  coordinate, frame-time and zoom mappings are exact. **garbage** (None / truncated thinking / prose / malformed JSON
  at random): finishes, caches nothing for failed generations, second pass picks up exactly the rest. `--sam`: the SAM 2
  stage (scripts/run_cv.py --qwen-boxes on the ta records, test-suite fake segmenter) + geometry + samcx run.
  (Replay numbers test our code only; they are not Track B results.)
- Repo suite: see section 5.

## 4. Expected gain (formula: rows x avg item gain / (4 x N_cat), N = S2 553, D2 1137, S3 538, D3 933)
Affected rows = scored test questions whose target is a size or a distance (S2 265, D2 881, S3 289, D3 720). Avg item
gain per row if the open target measurement reached the Claude-track quality on top of cvq (validation, section 1c):
S2 size .122 / dist .033, D2 .238 / .233, S3 .058 / .100, D3 .191 / .160 -> member-level upper bound
S2 +.013, D2 +.046, S3 +.009, D3 +.036 = **+.103 overall** (not reachable: Claude-quality tracks).
Central estimate: the open model recovers ~30% of that gap and ~60% of a member's gain survives the per-category
log-median -> **about +.02 overall on Track B** (range 0 to +.05; 0 = the kill test fails and nothing is submitted).
On S3 the run can only help through `ta_direct` (thinking model with the Track A prompt); the diagnosis gives no
evidence that it will beat CaW (.558), so no S3 gain is counted.

## 5. Commands run (this session; CPU only, no GPU job, no paid API call)
- `.venv/bin/python research/trackb_next/diagnose.py` / `diag_px.py` / `diag_mix_cvq.py` / `diag_hires.py` /
  `diag_boot.py` (numbers in sections 1a-1c; logs in this folder).
- `.venv/bin/python -m pytest -q research/trackb_next/test_ctx.py` -> 25 passed.
- `.venv/bin/python research/trackb_next/dry_run.py` (replay, 24 videos): ta geometry .715, tacx .706, cvqcx .638,
  ta_direct .766; geometry equal to the Claude-track solve on 157/159 rows. `--mode garbage` (5 videos, two passes):
  no crash, failed generations not cached. `--sam` (2 videos): SAM 2 stage + samcx run.
- `.venv/bin/python research/trackb_next/evaluate_ctx.py --root <replay copy>`: plumbing check of the kill-test script
  (replay numbers are not results).
- `.venv/bin/python notebooks/_build_notebook.py` (51 cells, nbformat-valid) and
  `.venv/bin/python -m pytest -q tests/ research/trackb_next/test_ctx.py` -> **682 passed** (incl. the notebook
  generator test that failed before because of the hand-edited q35 preset).

## 6. Verdict
INCONCLUSIVE until the GPU run returns: the diagnosis is done (dominant failure = target segment measurement), the run
is implemented, tested on CPU with mock models and documented (`RUN_INSTRUCTIONS.md`); the pre-registered kill test at
the top of this file decides on its outputs (`evaluate_ctx.py --root ... --lovo`). No candidate file is built now.
Follow-ups after the run: if `ta_geo` / `tacx_geo` pass, route size / distance rows to them inside the median sets;
if only `ta_direct` is strong, add it as a direct member; if nothing passes, the next lever is a per-question
"which segment" pointing model fine-tuned on Blender renders (out of scope for 9 days).
