"""Our MRA must equal the official evaluator.py on the same inputs."""
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from qp.mra import item_scores, score

OFFICIAL = Path(__file__).resolve().parents[1] / "external" / "QuantiPhy" / "evaluator.py"


def test_item_scores_thresholds():
    gt = [10.0] * 6
    pred = [10.0, 10.4, 10.6, 15.0, 0, "abc"]
    np.testing.assert_allclose(item_scores(pred, gt), [1.0, 1.0, 0.9, 0.4, 0.0, 0.0])


def synthetic(n=200, seed=0):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "qid": np.arange(n),
        "video_id": [f"v{i // 4}" for i in range(n)],
        "video_type": rng.choice(["S2MC", "V3SS", "A2MS", "S3MX"], n),
        "inference_type": rng.choice(["SS", "SD", "DS", "DD"], n),
        "question": [f"q{i}" for i in range(n)],
        "answer": rng.uniform(0.1, 50, n),
    })
    df["category"] = df.inference_type.str[0] + df.video_type.str[1]
    df["parsed_value"] = df.answer * rng.lognormal(0, 0.5, n)
    return df


@pytest.mark.skipif(not OFFICIAL.exists(), reason="clone Paulineli/QuantiPhy into external/QuantiPhy")
def test_matches_official(tmp_path):
    df = synthetic()
    gt = df.rename(columns={"answer": "ground_truth_posterior"})[
        ["qid", "video_id", "video_type", "inference_type", "question", "ground_truth_posterior"]]
    gt.to_csv(tmp_path / "gt.csv", index=False)
    (tmp_path / "in").mkdir()
    df[["qid", "video_id", "video_type", "inference_type", "question", "parsed_value"]].to_csv(
        tmp_path / "in" / "m.csv", index=False)
    subprocess.run([sys.executable, str(OFFICIAL), str(tmp_path / "in"), str(tmp_path / "out"),
                    "--gt_file", str(tmp_path / "gt.csv")], check=True, capture_output=True)
    official = pd.read_csv(tmp_path / "out" / "all_model_results.csv").iloc[0]
    ours = score(df)
    assert ours["mra"] == pytest.approx(official["mra_average"], abs=1e-12)
    for c in ("S2", "D2", "S3", "D3"):
        assert ours["per_category"][c] == pytest.approx(official[f"mra_{c}"], abs=1e-12)
