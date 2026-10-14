# Colab cells for the open-model port of the Track A v1 pipeline (Track B). Paste after the notebook's
# clone/install/data cells (sections 1-5 of notebooks/colab_pipeline.ipynb); REPO_DIR = /content/quantiphy-challenge.
# GPU: one 96 GB card. Qwen3.8-27B-FP8 (Apache-2.0) ~28 GB weights, rest is KV cache.

# --- cell A: separate venv for the newest vLLM (keeps the notebook's vllm==0.19.1 / SAM 2 stack intact)
# !python -m venv /content/vllm_env && /content/vllm_env/bin/pip -q install -U vllm openai
# (if vllm==0.19.1 already loads Qwen3.8 — same Qwen3_5 architecture class — skip the venv and use `vllm` directly)

# --- cell B: start the server in the background and wait until it answers
import subprocess, time, urllib.request
MODEL_ID = "Qwen/Qwen3.8-27B-FP8"
srv = subprocess.Popen(
    f"/content/vllm_env/bin/vllm serve {MODEL_ID} --port 8000 --max-model-len 131072 "
    f"--reasoning-parser qwen3 --limit-mm-per-prompt '{{\"image\": 40}}' --gpu-memory-utilization 0.92 "
    f"--max-num-seqs 48 > /content/vllm.log 2>&1", shell=True)
for _ in range(180):
    try:
        urllib.request.urlopen("http://localhost:8000/v1/models", timeout=5); print("server up"); break
    except Exception:
        time.sleep(10)

# --- cell C: smoke (2 videos) -> check coordinates on overlays before anything else (kill test 0)
# !cd /content/quantiphy-challenge && OPEN_BASE_URL=http://localhost:8000/v1 OPEN_MODEL=Qwen/Qwen3.8-27B-FP8 \
#   QP_RUNS=/content/drive/MyDrive/quantiphy/runs python research/r86/trackb_opt/run_open_pipeline.py \
#   --split val --name val_q38_smoke --videos internet_0005,simulation_0171 --effort medium --frames 16 \
#   --max-frames 32 --max-side 854 --workers 2
# Compare runs/val_q38_smoke/val.csv with runs/val_opus_high/val.csv rows (same videos) and draw a few boxes.

# --- cell D: validation pilot (24 videos, ~15 min) -> gate
# !cd /content/quantiphy-challenge && OPEN_BASE_URL=http://localhost:8000/v1 OPEN_MODEL=Qwen/Qwen3.8-27B-FP8 \
#   QP_RUNS=/content/drive/MyDrive/quantiphy/runs python research/r86/trackb_opt/run_open_pipeline.py \
#   --split val --name val_q38_a --effort medium --frames 16 --max-frames 32 --max-side 854 --workers 24
# !python scripts/score.py /content/drive/MyDrive/quantiphy/runs/val_q38_a/val.csv
# GATE: raw macro >= .65 and >= .62 on 3 of 4 categories (Track B best single .566, v3 LOVO .612).

# --- cell E: test, three independent runs (each ~2-3 h; resumable per video)
# for r in a b c: same command with --split test --name test_q38_$r (and --split val --name val_q38_$r)

# --- cell F: candidate
# !python research/r86/trackb_opt/build_open.py submissions/trackB_q38.csv \
#   --port runs/val_q38_a/val.csv:runs/test_q38_a/test.csv --port runs/val_q38_b/val.csv:runs/test_q38_b/test.csv \
#   --port runs/val_q38_c/val.csv:runs/test_q38_c/test.csv --tb outputs/trackb_v1 --preset trackb
