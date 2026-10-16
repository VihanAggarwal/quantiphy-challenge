# Track B open-weight agentic measurement (RUN_PRESET "agent")

Status: PRE-REGISTRATION, written 2026-10-16 before the Colab run. No validation or test answer of the agent exists
yet; the routing rule below is fixed now and is applied unchanged to whatever the run produces.

## What runs
One measuring agent per clip, the Track A recipe that gave the large jump there (research/blind/annotate_v3.workflow.js),
but every answer is produced by an OPEN-WEIGHT model: Qwen/Qwen3.6-27B-FP8 (Apache-2.0; fallback bf16
Qwen/Qwen3.6-27B) on vLLM, `qp/open/agent_loop.py` + `qp/open/run_agent.py`. The model gets a blind workspace (the
video, inputs.json with the clip's questions, no labels), a frame viewer (`FRAME t [x0 y0 x1 y1] [scale]`, pixel grid
in original coordinates) and a Python/OpenCV/scipy sandbox (subprocess, cwd = workspace, 60 s, no network, reads
outside the workspace refused, no tokens in its environment), and ends with `ANSWERS {qid: value}`. Caps: 30 actions,
8 min of the clip's own time, then one forced ANSWERS turn. The system prompt carries the v3 label conventions (prior
is the scale; Blender: depth_info = range to the object origin, verify range vs Z, world AABB sizes, backward
difference speed at the dataset fps, acceleration = d|v|/dt; internet: check camera motion; lab: FOV ~84 deg,
f ~711 px at 1280 px, forward differences at 25 fps; segmented = background removed). Segmented twins reuse the
original clip's answer to the same normalised question. No closed model is called anywhere (`run_agent.check_open`
refuses Claude / GPT / Gemini ids); nothing from Track A enters an answer.

## Base and its validation equivalent
- Test base: `submissions/trackB_probe_B2route.csv` (current best Track B file, leaderboard .671).
- Validation base: `make_base.py` runs the B2route pipeline (`research/trackb_v5/build_b2.py`, routing S2,D2,S3,D3,
  clamp b1, all components) in its "combined" table, i.e. the same pipeline on the 159 validation questions
  (macro MRA .6371, as in B2_BUILD.md). -> `base_val.csv` (one validation row, qid 2607 captured_0027s, has no value
  and scores 0, as in build_b2 --val). The test-table rebuild equals the B2route file on 3289/3289 rows ->
  `base_test.csv`. Both mark the rows set by a stated-fact rule (`stated`: 8 validation, 166 test rows).

## Pre-registered routing rule (fixed now)
Clip type from the question inputs (`common.clip_type`, the research/blind/build_agent_sub.py logic): `internet`,
`lab` by video_source; every other source (simulation, segmentation) is a simulation, `sim3` / `sim2` by
video_type[1]. Validation: sim3 52 q / 6 clips, sim2 40 / 6, internet 29 / 6, lab 38 / 6 (test: 756 / 123,
1307 / 256, 420 / 74, 806 / 115).

Held-out data: the validation questions, answered by the agent on the full-resolution copies (split `val_hires`, the
test configuration). For each type t:
- `base(t)` = mean item MRA (qp.mra.item_scores, missing = 0) of base_val over the type's validation questions;
- `agent(t)` = the same with the agent's answer wherever the agent answered and the row is not stated (else base),
  i.e. exactly what the build would submit with decision "agent".

Decision per type: **agent** if agent(t) >= base(t) + 0.02; **gm(agent, base)** (geometric mean) if
|agent(t) - base(t)| < 0.02; **base** if agent(t) <= base(t) - 0.02, and base when the agent answered no validation
row of the type. `evaluate.py --root <outputs/trackb_agent> --write` computes it and writes `routing.json`;
`build_sub.py` applies it to the test answers: stated-fact rows and rows without an agent answer keep B2route ->
`submissions/trackB_cand_agent.csv`.

Not part of the rule (printed for information only): the clip-bootstrap interval of agent - base per type, the gm
score, the routed composite's validation macro MRA (scored on the questions that chose the routing: optimistic), the
stated-fact check on test rows (values a sibling clip states as its prior).

## Caveats known before the run
- 6 clips per type: the clip-level noise of agent - base is several hundredths, larger than the 0.02 margin, so a
  routing decision can be wrong by chance; the gm band limits the damage of a near-tie.
- The open model is far weaker than Claude at agentic coding; on Track A the Claude agent scored .964 (3D sim) and
  .996 (2D sim) on stated-fact rows (research/PROBES.md). The main risks are protocol following (one action per reply), coordinate reading on images,
  and measurement code quality, not the label conventions (they are in the prompt).

## Result
(to be filled after the run: evaluate.py output, routing.json, build_sub.py output)
