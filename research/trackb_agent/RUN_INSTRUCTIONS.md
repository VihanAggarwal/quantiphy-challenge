# Track B Colab run: `RUN_PRESET = "agent"` (open-weight agentic measurement)

What it does (details and the pre-registered routing: `research/trackb_agent/RESULT.md`): the Track A agentic recipe
(one measuring agent per clip with a blind workspace, a frame viewer and a Python/OpenCV sandbox, pinhole geometry in
code) with an OPEN-WEIGHT model only: Qwen3.6-27B (Apache-2.0, FP8) on vLLM. Every reply of the model is one action:
a Python block (run on the CPU in the clip's workspace, 60 s limit, no network), `FRAME t [x0 y0 x1 y1] [scale]` (full
frame or zoomed crop with a pixel grid) or the final `ANSWERS {...}`. 32 clips run at once and their turns are batched
on the GPU. No closed model is involved anywhere. GPU only: no API keys needed.

## 0. Before Colab: put the new code on GitHub (`main`)
Already done if you pulled the commit "Track B: agent preset ..." (it is on `main`). Otherwise:

    git add qp/open/agent_loop.py qp/open/run_agent.py tests/test_agent_loop.py requirements-colab.txt \
            notebooks/_build_notebook.py notebooks/colab_pipeline.ipynb research/trackb_agent
    git commit -m "Track B: agent preset (open-weight agentic measurement)"
    git push origin main

## 1. Start the run
1. Open `notebooks/colab_pipeline.ipynb` in Colab (File > Open notebook > GitHub, or upload the file).
2. Runtime > Change runtime type: the **96 GB GPU** (RTX PRO 6000 / H100 class), **High-RAM** (the Python sandboxes run
   on the CPU). The stage needs >= 44 GB (`AGENT_MIN_GB`); on a smaller GPU it is skipped.
3. Colab secrets as for the earlier runs: `GH_TOKEN` (required), `HF_TOKEN` optional (Qwen3.6 is ungated). The
   sandboxed Python never sees them (it gets a minimal environment).
4. In the configuration cell (section 1) change ONE line:

       RUN_PRESET = "agent"

   Leave everything else as it is. The preset sets `RUN_NAME = "trackb_agent"`, `SPLIT = "val+test"` (validation
   first, then test), turns every other stage off, `MAX_HOURS = 8` (hard cap: the runtime is released after 8 h at
   the latest; per split no new clip starts after `AGENT_HOURS` = val 1 h / test 6 h, the running ones are asked for
   their answers) and pushes the val + test records. Use the same Google Drive as the trackb_v1 run: the stage reads
   `outputs/trackb_v1/{val,test}/caw/caw.csv` only to fill `agent_filled.csv` where the agent gave no answer (if
   missing, the run still works; the submission builder uses B2route as the fallback anyway).
   Between the two splits the notebook runs the **validation gate** (`research/trackb_agent/evaluate.py --gate`, CPU,
   seconds): if every clip type routes to `base` on validation, the test split is skipped and the cell prints
   `[agent/gate] TEST SKIPPED: ...` with the per-type scores (that is a result, not an error); otherwise test runs
   only on the clips of the types that use the agent (`AGENT_TEST_ROUTED_ONLY`; plus the originals of their twins).
5. **Smoke test first** (recommended; an estimate of 40-50 min including install, two model loads and 2 + 2 clips).
   In section 1 also set

       LIMIT_VIDEOS = 2
       AUTO_TERMINATE = False     # keep the runtime up to look at the results

   and Run all. It processes **2 validation clips and 2 test clips** (the gate only prints its decision in a smoke
   run; it never skips or restricts test there). Check in the section 13e output (also in
   `MyDrive/quantiphy/logs/trackb_agent.log`):
   - `loaded Qwen/Qwen3.6-27B-FP8 (vllm)` (or the bf16 fallback) for both splits;
   - a vLLM startup line confirming prefix caching, e.g. `enable_prefix_caching=True` in the engine config line and,
     for this hybrid (Gated DeltaNet + attention) model, a line about the Mamba / linear-attention cache in `align`
     mode or similar. If the engine refuses prefix caching for this model, or the load fails with an error that names
     it, set `AGENT_PREFIX_CACHING = "off"` in section 1 and Run all again (`--prefix-caching off`; slower, see 2.);
   - `agent run: {"clips": 2, "finished": 2, ...}` and `[agent/val] ok`, then the `[agent/gate] ...` lines, then
     the same two lines for test and `[agent/test] ok`.

   Then open the 4 transcripts (`outputs/trackb_agent/{val,test}/transcripts/*.json` on Drive, or on the
   `colab-outputs` branch after the interim pushes) and check:
   - real actions: most assistant turns have `"action": "python"` or `"frame"` and the next user turn holds a real
     result (`Python result: exit code 0 ...` with printed numbers, or `FRAME shown above.` with an image caption);
   - few `"No action found"` user turns (at most one or two per clip);
   - no storm of `"Your reply was cut off before an action (too long)"` turns (`"action": "cut"`); one now and then
     is fine, several in a row or on every clip means the thinking budget is too small for this model;
   - no `"generation failed"` turns and no answers record with `"end": "generation_failed"`
     (`outputs/trackb_agent/{val,test}/answers/*.json`); `"end": "done"` is the normal end, `"forced"` is acceptable;
   - the answers records have numbers for (nearly) every qid.

   Send back: the section 13e output (from `loaded ...` to `[agent/test] ok`, including the prefix-caching line) or
   the log file, plus a note whether the transcripts look as above (they are pushed to `colab-outputs`; if the push
   failed, zip `MyDrive/quantiphy/outputs/trackb_agent`). Then release the runtime yourself (Runtime > Disconnect and
   delete runtime): with `AUTO_TERMINATE = False` it keeps using compute units.
6. Full run: set `LIMIT_VIDEOS = 0` and `AUTO_TERMINATE = True` again, then Runtime > Run all. The 4 smoke-test clips
   are reused (finished clips are skipped). You can close the tab; `AUTO_TERMINATE` releases the GPU at the end, on an
   error, or after `MAX_HOURS`. If we change the code after the smoke test, delete
   `MyDrive/quantiphy/outputs/trackb_agent` first so the smoke clips are run again with the new code.

Optional knobs (section 1): `AGENT_THINKING = False` (about 2x faster, weaker code), `AGENT_CONCURRENCY` (32; 48 if
the log shows short rounds and no preemption warnings), `AGENT_MAX_STEPS` (30), `AGENT_CLIP_MINUTES` (8: the clip's own
model + tool time, roughly what one clip would take alone; real elapsed time per clip is longer because 32 clips share
the GPU, and is capped at 4x), `AGENT_PREFIX_CACHING` ("on"; "off" only as the fallback of step 5),
`AGENT_TEST_ROUTED_ONLY` (True: after the gate, test runs only on the clips of the types that use the agent; False:
on every clip unless the gate skips test).

## 2. Expected runtime (96 GB GPU; an ESTIMATE, not measured: no GPU was available when this was written)
Prefix caching is now forced on (`--prefix-caching on`, `AGENT_PREFIX_CACHING`): the earlier version left it to the
engine default, which for this hybrid model may be off, and then every turn re-prefills the whole conversation (up to
tens of thousands of tokens with images). The numbers below assume it is on and working; the smoke test must show the
vLLM line confirming it (section 1, step 5). Assumptions: ~15 actions per clip, ~1.5-2k generated tokens per action
with thinking, ~1.2-1.6k tokens/s aggregate decode for the 27B FP8 model at 32 concurrent sequences, only the new
tokens of each turn prefilled (cache hits for the rest).

| step | val (24 clips) | test (568 clips; 535 run, 33 twins reuse answers; fewer if the gate restricts it) |
|---|---|---|
| install + data sync | ~15 min (once) | |
| model load | ~5 min | ~5 min |
| agent | ~20-40 min | **~3.5-5 h** for all clips (no new clip after 6 h) |
| **total** | | **~5-6.5 h (cap 8 h)**; much less if the gate skips or restricts test |

With `AGENT_PREFIX_CACHING = "off"` (fallback) every turn re-prefills its conversation: expect roughly 1.5-2x the
agent time, i.e. test will not finish within the 6 h budget; Run all again later to continue (finished clips are
skipped).

The log prints a line every 8 finished clips (`agent k/N clips: a/b questions answered, f forced, s steps/clip, m min
(x s/clip)`). Expect ~25-35 s/clip on test once 32 clips run at once (with prefix caching). If test clips are still
left when the 6 h budget ends, Run all again later: finished clips are skipped and the rest continue. If most clips end
"forced" by the time budget, the run is slower than estimated (try `AGENT_THINKING = False` on the re-run, or more
concurrency).

## 3. What gets pushed back
The notebook pushes to the GitHub branch **`colab-outputs`**, folder `outputs/trackb_agent/` (after val, after test,
and a final push):
- `val/` and `test/`: `answers/<clip>.json` (answers, source per qid: agent / forced / workspace_file / twin, end
  reason, steps, time), `transcripts/<clip>.json` (every visible reply, the tail of the thinking, every tool result
  and image caption; no images), `agent.csv` (agent answers only), `agent_filled.csv` (with the CaW fallback),
  `config_agent.json`, `summary_agent.json`;
- `val/gate.json` (the validation gate: per-type decision, whether test ran, the test clips it ran on);
- `val/scores.csv` (validation MRA of `agent` and `agent_filled`, section 14) and `colab.log`.
Just tell us when the run finished (or paste the "failed stages" summary). If the push failed, zip the Drive folder
`MyDrive/quantiphy/outputs/trackb_agent` plus `MyDrive/quantiphy/logs/trackb_agent.log` and send that.

## 4. If something fails
- `could not load Qwen/Qwen3.6-27B-FP8` -> the stage tries the bf16 `Qwen/Qwen3.6-27B` by itself. If both fail, set
  `AGENT_MODEL = AGENT_FALLBACK = "Qwen/Qwen3.5-27B"` (same architecture, already run with this vLLM) and Run all again.
- Out of memory / many "preempted" warnings: lower `AGENT_CONCURRENCY` to 16, or add `--max-model-len 49152` to the
  `run_agent` line of section 13e (images are dropped from the oldest end when a conversation gets long).
- vLLM refuses `limit_mm_per_prompt` with 12 images, or its memory profiling fails on the image encoder: add
  `--max-images 8 --mm-max-pixels 1638400` to the `run_agent` line (our images are at most 1280 px on the long side).
- A disconnect: Run all again; every finished clip is skipped (a clip that was mid-way starts over).

## 5. Afterwards (CPU, us)
    .venv/bin/python research/trackb_agent/evaluate.py --root <pulled outputs/trackb_agent> --write
    .venv/bin/python research/trackb_agent/build_sub.py --root <pulled outputs/trackb_agent>
The first audits the validation transcripts (flagged clips keep the base), applies the pre-registered per-type routing
(RESULT.md) on validation only and writes `routing.json`; the second audits the test transcripts the same way and
builds `submissions/trackB_cand_agent.csv` on top of `submissions/trackB_probe_B2route.csv` (twin rows routed by their
original clip's type).
