# Track B probe B2route and candidate B1clamp: build log (2026-10-15)

Two files, both read per category against B1 (leaderboard .638 / .676 / .639 / .652 = .651):

| file | what it is | rows changed vs B1 (all / scored) |
|---|---|---|
| `submissions/trackB_probe_B2route.csv` | B1 + the pseudo-label routing extended from S2 to D2, S3 and D3 (same table, same min-support 25 / k <= 2, same fallback rule), B1 components kept as below, family rules after | S2 17 / 16 (spill-over only), D2 856 / 836, S3 462 / 430, D3 832 / 798 |
| `submissions/trackB_cand_B1clamp.csv` | B1 with the car-width clamp regex widened to "width of the ... car" (up to 4 modifier words), "toy" still excluded | S2 5 / 5, D2 6 / 6, S3 1 / 1, D3 7 / 7 (the 19 rows of B1_VERIFY issue 2) |

Both have 3289 rows in template order, every value finite and > 0, and pass `scripts/make_submission.py` (round trip
unchanged). Inputs are open-weight outputs, model-free code and test inputs only. No Track A value is in any answer
(checks below). I did not modify `qp/`, `scripts/`, `build_b1.py` or any other existing file, and committed nothing.

## Files

| file | content |
|---|---|
| `research/trackb_v5/build_b2.py` | builder. Imports every B1 component from `build_b1.py` unchanged; generalises the routing to `--route <cats>` and the clamp to `--clamp b1/wide`. `--route S2 --clamp b1` rebuilds `trackB_cand_B1.csv` byte for byte (asserted in `--decompose`). Options: `--no-l2q-route`, `--keep`, `--keep-ref`, `--rows`, `--decompose`, `--val` |
| `research/trackb_v5/check_b2.py` | audit hook, value check, stated facts, clamp row check, submission check |
| `research/trackb_v5/B2_rows.csv` | every B2route row that differs from B1 (2167) plus spill-flagged rows: cell, B1 / new value, raw changed, pool spill flag, B1 and new raw source (member set), B1 and new **winning component**, `spill_from_<cat>` flags, leave-one-out `attribution` |
| `research/trackb_v5/B2_spillover.csv` | the 419 changed rows that are spill-over in any sense (pool spill with raw unchanged, or attributed to another category's routing), with `kind` and `other_route` |
| `research/trackb_v5/B1clamp_rows.csv` | the 19 B1clamp rows |
| `B2_build.log`, `B1clamp_build.log`, `B2_checks.log` | console output |

## B2route recipe

**Routing (identical procedure to B1's S2 routing, now for D2, S3, D3 as well).**
- Cell = category | video source | unit kind (A / V / L), as in `pseudo_tb.py`.
- Each cell in `routing_base8_min25_k2.csv` takes the log-median of its 1-2 member set. The table holds cells with at
  least 25 fit rows, and each set is the best of all 1- and 2-member sets of the 8 base members by agreement with the
  Track A combo2 test predictions on test rows of non-validation videos.
- Every other row of the category takes the category fallback set (`fallback_category_sets.json`, chosen by the same
  agreement criterion over 1-4 member sets). This is the same rule as B1 used for S2.
- A routed row with no finite member takes the fallback set, then the B1 set. On test this happened to 0 rows.

| category | cell: set (test rows) | fallback set (rows) | B1 set it replaces |
|---|---|---|---|
| D2 | internet L: cvq_geo+qwen35 (169); internet V: cvq_geo (47); segmentation L: cvq_geo (138); segmentation V: cvq_geo+qwen_geo (32); simulation L: cvq_geo (590); simulation V: cvq_geo (158) | cv_geo_only+cvq_geo+gemma4 (29: lab L 9, lab V 6, simulation A 10, segmentation A 3, internet A 1) | caw+cv_geo+qwen_direct+qwen_geo |
| S3 | lab L: cvq_geo+qwen_fov* (179); lab V: cv_geo_only+qwen_fov* (143); segmentation L: cvq_geo+qwen35 (38); simulation L: qwen_direct+gemma4 (91); simulation V: cv_geo_only (55) | cv_geo+qwen_fov*+gemma4 (72: segmentation V 27, simulation A 23, lab A 12, segmentation A 10) | cv_geo+qwen_fov+qwen_direct |
| D3 | lab L: cvq_geo+qwen35 (350); lab V: cv_geo+gemma4 (101); segmentation L: gemma4 (72); simulation L: qwen35+gemma4 (330); simulation V: cvq_geo+qwen_geo (90) | caw+cvq_geo+gemma4 (26: segmentation V 14, lab A 6, simulation A 5, segmentation A 1) | caw+qwen_fov+qwen_direct |
| S2 | as B1 (552 routed + 27 fallback) | cvq_geo+qwen_geo+qwen35 | (unchanged vs B1) |

\* The table says qwen_geo. L2' substitutes qwen_fov, which differs from qwen_geo on lab rows only (see below).

Pipeline order, as in B1: raw (routing, L2' substitution, L6s), then preset "trackb" on the whole test table, then L1,
then L4, then the clamp (B1 regexes), then `--keep`, then `make_submission.py`.

## Which component wins, per row, and why

The steps are listed in pipeline order. A later step overrides an earlier one on the rows it touches.

| B1 component | rows in B2route | outcome | why |
|---|---|---|---|
| **v3 member set** (D2/S3/D3) | all 2710 rows of D2, S3, D3 | **replaced by the routing** | This replacement is what the probe reads. |
| **L2'** (qwen_geo -> qwen_fov, S3/D3) | 757 rows where qwen_fov differs from qwen_geo (all lab) | **Kept on 319 S3 lab rows**: the routed sets S3 lab L / lab V and the S3 fallback set contain qwen_geo, so the substitution applies inside them (S3 lab L 170, lab V 143, lab A 6). **Gone on 438 D3 lab rows** (the routing wins): the D3 lab sets (cvq_geo+qwen35, cv_geo+gemma4, fallback caw+cvq_geo+gemma4) have no Qwen-geometry member to substitute. | L2' is not a member choice. It fixes how the Qwen geometry member is solved: the same track, re-solved with the known fixed lab camera. The routing chooses which members are used, and L2' fixes that member wherever it is used. Where the routing drops the member, L2' has nothing to act on. |
| **L6s** (D2 snapped twin-mask cvq geometry) | 276 D2 rows | **L6s wins** over the routed median, as it overrode the v3 median in B1. In 253 of the rows the routed set is cvq_geo alone (segmentation L 118, simulation L 113, simulation V 22), so L6s is the routed member re-measured on the snapped twin mask. In 23 D2 segmentation V rows, the routed log-median of cvq_geo and qwen_geo is replaced by L6s alone. | L6s is a per-row re-measurement, not a member set. Keeping it means D2 reads the routing on the rows without twin geometry. L6s itself was already read in B1. |
| **stated-fact rules** (facts, motionfam, freefall, labfacts) | 166 rows (same set as B1) | win; final values identical to B1 | stated values |
| **pool rule** (preset "trackb", one vote per base clip, 1.6x guard) | recomputed on the routed raw values | applies as in B1; this is the source of the spill-over | family rules after, as in B1 |
| **L1** (S3 lab motion emulator) | 143 rows: 142 also in B1. 3 B1 rows (2379, 2540, 2666) now have a factor within 3% of 1, and 1 new row (2624) gets a factor. | kept, as a factor on the routed post-rule value | It is a post-rule step that takes whatever answer the row has. The factor depends on that answer, so it is recomputed. |
| **L4** (D2 free fall) | 21 D2 rows | wins; values identical to B1 | closed form from the stated acceleration |
| **clamp** (B1 regexes, unchanged) | 30 rows (car width 18, person height 12) | wins | a-priori range. 21 rows are clamped in both files. 26 B1 clamp rows now sit in range (routed car widths 1.80-2.21 m), so they keep the routed value. 9 rows are newly clamped because the routing pushed them out of range: person heights 8, 2266, 2271, 2276, 2293, 2312, 2331, 2973, 3151; for example, the D2 lab fallback gives 310 cm for captured_0015. |

The new value of each changed row comes from one of these components (`new_winner` in B2_rows.csv):

| | D2 | S3 | D3 | S2 |
|---|---|---|---|---|
| routed cell set | 441 | 246 | 589 | 5 (B1 pooled; now own value) |
| category fallback set | 20 | 24 | 8 | |
| pool rule on routed / L6s raw | 381 (88 on L6s rows) | 59 | 232 | 12 |
| L1 x routed value | | 133 | | |
| L6s (raw unchanged, pooling changed) | 8 | | | |
| clamp | 6 | | 3 | |
| **total changed** | **856** | **462** | **832** | **17** |

Alternatives I did not upload. Each one changes only the rows named here; set the matching flag to build it:
- **Routed sets verbatim**, with no L2' inside them (`--no-l2q-route`): 319 S3 lab rows differ and nothing else. The
  validation score is identical.
- **Routing wins over L6s** (`--comps l2q,route,l1,l4,clamp`): the raw value differs on 275 D2 rows. The final value
  differs on D2 337, S2 11, S3 1 and D3 41 rows. Validation .6381 vs .6371; D3 .6255 vs .6213, which is the L6s
  spill-over into D3 already seen in B1.

## Reading B2route per category vs B1 (spill-over)

The pool rule pools a question across all clips of a base family, and the 2D and 3D clips of the same simulation scene
are in one family. So the routing of one category moves rows of the others.

Each changed row is attributed by leave-one-out: drop one category from `--route` and see which rows change. Scored rows:

| category | changed | own routing only | own + other | other only (pure spill-over) | interaction only | of which raw unchanged (pool spill) |
|---|---|---|---|---|---|---|
| S2 | 16 | | | 14 | 2 | 16 |
| D2 | 836 | 722 | 102 | 12 | | 98 |
| S3 | 430 | 384 | 43 | 3 | | 2 |
| D3 | 798 | 637 | 153 | 8 | | 12 |

Rows touched by another category's routing (scored, leave-one-out; a row can count for two sources):

| category | from route D2 | from route S3 | from route D3 |
|---|---|---|---|
| S2 | 6 | 6 | 7 |
| D2 | | 8 | 113 |
| S3 | 2 | | 45 |
| D3 | 85 | 81 | |

What this means for the reads:
- **The D2 read** is mostly D2 routing (824 rows). It also includes 113 rows moved by the D3 routing. The families
  involved are sim 0216, 0213, 0210, 0068, 0179, 0214, 0217, 0054, 0057, 0185, 0248 and 0158.
- **The D3 read** includes 85 rows from D2 routing and 81 from S3 routing.
- **The S3 read** includes 45 rows from D3 routing. The families involved are 0074, 0034, 0021, 0028, 0310, 0022,
  0043, 0311 and 0027.
- **S2 changes only through spill-over**, on 17 rows (16 scored), all listed here:
  - 12 and 1746 (sim 0041): B1 pooled them to 8.13; they now keep their own values (12.59 and 8.99). This needs two
    routed categories together.
  - 42, 45, 58 (turning yellow car width): pooled with the D3 0062-0067 rows, they move from 3.57 to 5.19-5.31 m.
  - 60, 62, 63, 66 (sim 0075).
  - 89, 90, 96, 97 (sim 0082/0083, black and white car).
  - 339 and 1849 (sim 0145), 385 (sim 0163), 1744 (sim 0041 segmented).
- `B2_spillover.csv` lists all 419 rows. `B2_rows.csv` has the `spill_from_<cat>` and `attribution` columns.

Each routed category added to B1 on its own, all / scored rows:

| alone | S2 | D2 | S3 | D3 |
|---|---|---|---|---|
| route D2 | 4/4 | 838/818 | 0 | 73/73 |
| route S3 | 10/9 | 3/3 | 456/424 | 76/72 |
| route D3 | 9/9 | 136/136 | 42/40 | 824/790 |

## Validation (combined table; labels read only to score, nothing set or selected by them)

| build | MRA | S2 | D2 | S3 | D3 | clip bootstrap delta vs B1 [90%] | validation rows changed |
|---|---|---|---|---|---|---|---|
| B1 | .6458 | .6187 | .5946 | .7209 | .6489 | | |
| B1 + route D2 | .6424 | .6187 | .5811 | .7209 | .6489 | -.0034 [-.009, +.006] | 26 |
| B1 + route S3 | .6491 | .6250 | .5946 | .7279 | .6489 | +.0033 [-.008, +.012] | 39 |
| B1 + route D3 | .6366 | .6187 | .5946 | .7116 | .6213 | -.0092 [-.031, +.019] | 43 |
| **B2route** | **.6371** | .6250 | .5811 | .7209 | .6213 | **-.0087 [-.036, +.023]** | 102 |
| B1clamp | .6458 | = | = | = | = | 0 | 0 |

- This agrees with the PLAN.md finding that 4-category routing loses D2 and D3 on validation.
- Validation also under-read the S2 routing: +.044 there, +.080 on the leaderboard. That is why this is uploaded as a
  probe and not judged on validation.

**Stated-fact rows** (test priors, scored on the raw values before the facts rule; the final values do not change):

| routing | fact rows changed | item before -> after |
|---|---|---|
| D2 | 8 | .787 -> .950 |
| S3 | 12 | .692 -> .817 |
| D3 | 50 | .788 -> .762 |

These reads are partly in-sample. The routing fit used Track A answers on test rows outside the validation videos, and
those rows include the fact rows, where Track A gives the stated value. D3 reads negative even so, which counts against
the D3 routing.

## B2route: expectation and kill test (pre-registered here, before the upload)

- **Prior:** none that is confident. Validation and the D3 fact rows point down for D3. The D2/S3 fact rows and the S2
  leaderboard precedent point up. The upload is the read.
- **Kill test, per category:** keep a category's routing only if its read is >= B1 + .001, that is D2 >= .677,
  S3 >= .640, D3 >= .653.
- **S2** moves only through spill-over (16 rows). I expect at most +-.003. If it drops by more than .001, the spill
  source is in the tables above.
- **Reverting failed categories:** `build_b2.py --out <f> --keep <S2 + passing cats>`. The other categories then take
  the B1 values row by row (tested: `--keep S2,D2,S3` gives D3 equal to B1 and everything else equal to B2route).
  - This keeps exactly what each kept category was read with, cross-category spill-over included, as in the B1 revert
    rule.
  - `--route S2,<passing cats>` instead gives a self-consistent pooling, but the kept categories then differ from
    what was read on their spill rows. For example, D2 has 113 D3-touched rows. That file would need its own read.
- **Mixed result:** if one category passes and its biggest spill source fails (D2 passes, D3 fails), the next probe is
  a single-category build, `--route S2,D2` or `--route S2,S3` (the "alone" rows above).

## B1clamp (a-priori plausibility fix)

**What changed.** `build_b1.py` matches a car width with `width of the (?:\w+ )?car`, which allows one modifier word.
B1clamp adds a second alternative, so it matches a superset of the B1 rows:

```
\bwidth of the (?:(?!(?:the|a|an|that|which|where|of)\b)[\w'-]+ ){0,4}car\b(?!['’]s\b)(?! (?:park|door|window|wheel|tire|tyre|seat|roof|lane|mirror|light|bumper|hood|trunk|space|spot)s?\b)
```

- Up to 4 modifier words are allowed between "the" and "car".
- None of them may be a determiner, a relative pronoun or "of", so "car" is the head of the same noun phrase. This
  excludes "width of the road that the bike and the car are on".
- "car's ..." and "car park / door / ..." are excluded.
- The clamp still skips rows whose question or prior contains "toy", and rows set by a stated-fact rule. 0 rows are
  skipped this way.
- The range is unchanged: [1.5, 2.3] m.

**The 19 rows.** All are scored and all go down to 2.3 m:
- turning yellow car at 3.573 m: 35, 42, 45, 58, 1286, 1299, 1312, 1324, 1337, 1354, 1366, 1769, 1781;
- black and white car at 5.461 m: 90, 97, 105;
- grey and red car at 4.126 m: 273, 1840;
- dark green car at 5.823 m: 293.

By category: S2 5, D2 6, S3 1, D3 7. Nothing else changes, and since the clamp runs after the rules there is no
spill-over (`check_b2.py` step 4).

**Not matched, by design.** The spec is "width of the ... car":
- road widths 400 and 1396;
- the in-range "width (from the left wheel to the right wheel) of the car", rows 1456, 1466, 1496 (1.85 m);
- the lettering row 1533;
- "width, in meters, of the blue car", rows 1536 (1.43 m), 1541 (1.79 m) and 2011 (0.90 m). Two of these are out of
  range. Adding that phrasing would be a further a-priori extension (2 S3 rows), and it is not in this file.

**Expected gain.** For a true car width of 1.8-2.2 m (validation labels are 1.86-2.21 m), the gain is +.004 overall:
S2 +.006, D2 +.004, S3 +.001, D3 +.005. At 2.5 m it would be +.003. Validation changes 0 rows.

**Kill test.** Keep it if overall >= B1 + .001 and no category is below its B1 score - .001. The S3 read covers one
row (at most +.002).

**Composite note.** B2route uses the B1 clamp, so each file reads one change. In B2route these 19 rows are
1.95-7.48 m. A later composite should use `--clamp wide`, plus `--keep-ref` set to the composite base when it reverts
categories.

## Checks run (all pass; `B2_checks.log`)

1. **Reproduction.**
   - `build_b2.py --route S2` rebuilds `trackB_cand_B1.csv` byte for byte.
   - Rebuilds of both new files are byte-identical.
   - The audited rebuilds equal the files.
2. **Clean inputs.** Under an audit hook the two builds open 639 data files:
   - the same directories and files as the B1 audit (636 files);
   - the B1 submission, read for the comparison and `--keep`;
   - the second build's temporary CSV and output.

   The only subprocess is `scripts/make_submission.py`. No Track A or closed-model file is opened (same FORBIDDEN
   pattern as check_b1). The routing table and the fallback sets are member names only.
3. **Values vs 99 Track A files.**
   - B2route: 12 of its 2167 changed rows equal a Track A value. Every one is an open member's own value, a round
     direct answer of qwen35 / gemma4 / qwen_direct / caw: 1.75, 0.15, 3.5, 1.8, 0.45, 0.6 or 3.2. None is unexplained.
   - B1clamp: 0 rows equal a Track A value.
4. **Stated facts.** 0 of 129 fact rows change their final value vs B1, in either file.
5. **Submission.** `make_submission.py` passes on both files, with values unchanged.

## FAQ disclosure note (replaces the B1 note in the technical report, Open-Weight Track)

> **Use of Main Track outputs during Open-Weight development (FAQ section 09).** Our Open-Weight answers in each
> category (2D/3D, static/dynamic) are log-medians of open-weight members. Which members to combine in each cell
> (category x video source x unit kind) was decided during development by comparing the open-weight members with our
> own Main Track (closed-API, Claude Opus) test predictions, which served as pseudo-labels. The comparison used test
> questions outside the validation videos, cells with at least 25 such questions and one- or two-member sets; the rest
> of each category used a category-level set chosen the same way. The resulting tables (`routing_base8_min25_k2.csv`,
> `fallback_category_sets.json`) contain member names only. Which categories use this routing was decided from
> leaderboard reads of the Open-Weight submissions. A development script for the canonical-size clamp printed a
> comparison against Main Track predictions. The clamp classes and ranges in the submission are fixed world-knowledge
> ranges (car width 1.5-2.3 m, person height 1.50-2.00 m), checked against stated test priors and validation labels;
> the widening of the car-width phrase matching was decided from the question text alone. At inference time the
> Open-Weight pipeline uses only publicly available weights (Qwen3-VL-32B-Instruct-FP8, Qwen3.5-27B, Gemma-4-31B-it,
> CaW, Grounding DINO, SAM 2.1) and model-free code on the test inputs. No closed-model output, parameter or answer
> value enters any Open-Weight answer. Validation labels were used only to score candidates, never to set an individual
> answer.

## Commands

```
.venv/bin/python research/trackb_v5/build_b2.py --out submissions/trackB_probe_B2route.csv \
    --rows research/trackb_v5/B2_rows.csv --decompose --val                         > research/trackb_v5/B2_build.log
.venv/bin/python research/trackb_v5/build_b2.py --out submissions/trackB_cand_B1clamp.csv --route S2 --clamp wide \
    --rows research/trackb_v5/B1clamp_rows.csv --decompose --val                    > research/trackb_v5/B1clamp_build.log
.venv/bin/python research/trackb_v5/check_b2.py submissions/trackB_probe_B2route.csv submissions/trackB_cand_B1clamp.csv \
                                                                                    > research/trackb_v5/B2_checks.log
```

`B2_spillover.csv` was derived from `B2_rows.csv` (the `spill`, `attribution` and category columns).
