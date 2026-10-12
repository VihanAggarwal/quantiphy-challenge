"""scripts/trackb_build.py: the median over the open-model methods present (no GPU, synthetic run)."""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


def _mod():
    spec = importlib.util.spec_from_file_location("trackb_build", ROOT / "scripts" / "trackb_build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _questions(qids, answers=None):
    n = len(qids)
    return pd.DataFrame({"qid": qids, "video_id": [f"v{q % 3}" for q in qids],
                         "category": (["S2", "D2", "S3", "D3"] * n)[:n],
                         "question": ["What is the speed of the ball in m/s?"] * n,
                         "prior": ["diameter of the ball = 5cm"] * n,
                         **({"answer": answers} if answers is not None else {})})


def test_log_median_skips_missing_members():
    mod = _mod()
    idx = pd.Index([1, 2, 3])
    preds = {"a": pd.Series([1.0, 4.0, np.nan], idx), "b": pd.Series([4.0, np.nan, np.nan], idx),
             "c": pd.Series([16.0, 1.0, np.nan], idx)}
    got = mod.log_median(preds, ["a", "b", "c"], idx)
    assert got[1] == pytest.approx(4.0) and got[2] == pytest.approx(2.0) and np.isnan(got[3])
    assert {"cvq_geo", "qwen35", "gemma4"} <= set(mod.METHODS) and set(mod.MEDIAN) <= set(mod.METHODS)
    assert mod.METHODS["cvq_geo"] == "cvq/geometry.csv"


def test_median_over_present_methods(tmp_path, monkeypatch, capsys):
    mod = _mod()
    vq, tq = list(range(1, 41)), list(range(101, 141))
    truth = np.linspace(1.0, 5.0, len(vq))
    monkeypatch.setattr(mod, "load_validation", lambda: _questions(vq, truth))
    monkeypatch.setattr(mod, "load_split", lambda split: _questions(tq))
    rng = np.random.default_rng(0)
    run = tmp_path / "run"
    # three methods near the truth, one 3x off; gemma4 answers too few questions to count
    for name, factor in (("caw/caw.csv", 1.0), ("cvq/geometry.csv", 1.05), ("qwen35/direct.csv", 0.95),
                         ("qwen/direct.csv", 3.0), ("gemma4/direct.csv", 1.0)):
        for split, qids, base in (("val", vq, truth), ("test", tq, np.ones(len(tq)))):
            vals = base * factor * np.exp(rng.normal(0, 0.01, len(qids)))
            if name.startswith("gemma4"):
                vals[5:] = np.nan
            (run / split / Path(name).parent).mkdir(parents=True, exist_ok=True)
            pd.DataFrame({"id": qids, "parsed_value": vals}).to_csv(run / split / name, index=False)
    sent = []

    def fake_run(cmd, **kw):   # make_submission: keep the answers it would submit
        sent.append((cmd, pd.read_csv(cmd[2])))
        return type("R", (), {"returncode": 0})

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    mod.main([str(run), str(tmp_path / "sub.csv"), "--combine", "median", "--no-postprocess"])
    out = capsys.readouterr().out
    assert "median of ['qwen_direct', 'caw', 'cvq_geo', 'qwen35']" in out
    assert "without qwen_direct" in out and "gemma4" not in out.split("median of")[1]
    (cmd, answers), = sent
    assert cmd[1].endswith("make_submission.py") and cmd[3].endswith("sub.csv")
    assert answers.id.tolist() == tq and np.allclose(answers.parsed_value, 1.025, rtol=0.03)   # the outlier is out
    with pytest.raises(SystemExit, match="unknown methods"):
        mod.main([str(run), str(tmp_path / "sub.csv"), "--combine", "median", "--median-of", "caw,nope"])
