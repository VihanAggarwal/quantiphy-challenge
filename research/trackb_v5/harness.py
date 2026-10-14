"""Track B v5 evaluation harness (open-weight outputs only; validation labels read only in `score*`).

Builds per-category log-median member sets over the open-model methods (research/trackb_dense/select_sets.all_methods:
the 7 Colab methods + re-solved geometry variants with CaW fallback), puts the validation questions back into the test
question table (research/trackb_v4/eval_sets.table), applies qp.postprocess preset "trackb" and optional post-steps.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "research" / "trackb_dense"))
from qp import postprocess as pp  # noqa: E402
from qp.mra import item_scores  # noqa: E402
from select_sets import all_methods  # noqa: E402
from tbcommon import questions  # noqa: E402

VAL_OFFSET = 100000
CATS = ("S2", "D2", "S3", "D3")
V3 = {"S2": ["caw", "cv_geo", "qwen_direct"], "D2": ["caw", "cv_geo", "qwen_direct", "qwen_geo"],
      "S3": ["cv_geo", "qwen_geo", "qwen_direct"], "D3": ["caw", "qwen_geo", "qwen_direct"]}


def src_of(v: str) -> str:
    return "seg" if v.endswith("_segmented") else v.split("_")[0]


class Data:
    def __init__(self):
        self.test, self.val = questions("test"), questions("val")
        vkey = set(zip(self.val.video_id, self.val.question.map(pp.norm_question)))
        self.dup = np.array([(v, pp.norm_question(q)) in vkey for v, q in zip(self.test.video_id, self.test.question)])
        paths = dict(zip(self.test.video_id, self.test.video_path))
        v2 = self.val.drop(columns=["answer"]).copy()
        v2["qid"] = v2.qid + VAL_OFFSET
        v2["video_path"] = v2.video_id.map(paths).fillna(v2.video_path)
        cols = [c for c in self.test.columns if c in v2.columns]
        self.df = pd.concat([self.test[~self.dup][cols], v2[cols]], ignore_index=True)
        self.lab = pd.Series(self.val.answer.to_numpy(float), index=self.val.qid + VAL_OFFSET)
        self.vcat = pd.Series(self.val.category.to_numpy(), index=self.lab.index)
        self.vvid = pd.Series(self.val.video_id.to_numpy(), index=self.lab.index)
        self.P = {"test": all_methods("test", self.test), "val": all_methods("val", self.val)}

    def add_method(self, name: str, test: pd.Series, val: pd.Series):
        """test / val: Series indexed by qid (val qids NOT offset)."""
        self.P["test"][name] = test.reindex(self.test.qid).set_axis(self.test.index)
        self.P["val"][name] = val.reindex(self.val.qid).set_axis(self.val.index)

    def raw(self, sets: dict, split: str) -> pd.Series:
        frame = self.test if split == "test" else self.val
        out = np.full(len(frame), np.nan)
        for c, ms in sets.items():
            m = (frame.category == c).to_numpy()
            L = np.log(np.vstack([self.P[split][x].to_numpy(float) for x in ms]))
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                out[m] = np.exp(np.nanmedian(L, 0))[m]
        return pd.Series(out, index=frame.qid.to_numpy())

    def combined(self, sets: dict) -> pd.Series:
        rt, rv = self.raw(sets, "test"), self.raw(sets, "val")
        return pd.concat([rt.reindex(self.test.qid[~self.dup]),
                          pd.Series(rv.to_numpy(), index=self.val.qid.to_numpy() + VAL_OFFSET)])

    def rules(self, pred: pd.Series, preset="trackb", df=None):
        pr = pp.PRESETS[preset]
        return pp.apply_rules(pred, self.df if df is None else df, rules=pr["rules"], speed_guard=pr["speed_guard"],
                              options=pr["options"])

    def items(self, pred: pd.Series) -> pd.Series:
        it = pd.Series(item_scores(pred.reindex(self.lab.index).to_numpy(float), self.lab.to_numpy()),
                       index=self.lab.index)
        return it.fillna(0.0)

    def score(self, pred: pd.Series) -> dict:
        it = self.items(pred)
        per = {c: float(it[self.vcat == c].mean()) for c in CATS}
        return dict(MRA=float(np.mean(list(per.values()))), **per)

    def boot(self, a: pd.Series, b: pd.Series, n=2000, seed=0) -> dict:
        """Clip-bootstrap of the macro-MRA delta b - a on validation (resample videos)."""
        ia, ib = self.items(a), self.items(b)
        vids = self.vvid.unique()
        rng = np.random.default_rng(seed)
        idx = {v: np.where(self.vvid.to_numpy() == v)[0] for v in vids}
        cat = self.vcat.to_numpy()
        da, db = ia.to_numpy(), ib.to_numpy()
        out = []
        for _ in range(n):
            s = np.concatenate([idx[v] for v in rng.choice(vids, len(vids))])
            per = []
            for c in CATS:
                m = s[cat[s] == c]
                if len(m):
                    per.append(db[m].mean() - da[m].mean())
            out.append(np.mean(per))
        out = np.array(out)
        ch = int((~np.isclose(a.reindex(self.lab.index), b.reindex(self.lab.index), rtol=1e-9, equal_nan=True)).sum())
        return dict(delta=float(np.mean([db[cat == c].mean() - da[cat == c].mean() for c in CATS])),
                    lo=float(np.quantile(out, .05)), hi=float(np.quantile(out, .95)), changed=ch)


def fmt(d: dict) -> str:
    return " ".join(f"{k} {v:.4f}" if isinstance(v, float) else f"{k} {v}" for k, v in d.items())
