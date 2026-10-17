"""Audit round 3 inputs: 2D simulation, internet, and the 3D simulation families the first 3D-sim audit did not cover.

Items group whole scene families (qp.postprocess scene_families) so siblings are audited together; small families are
packed together up to MAX_ROWS scored rows. Current answer = merge5. Provenance = stated fact / audit fix / agent / pipeline.

    .venv/bin/python research/next/audit3/build_inputs.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "research/blind"))
from pool_check import kinds  # noqa: E402
from qp import postprocess as pp  # noqa: E402
from qp.data import load_split  # noqa: E402

OUT = ROOT / "research/next/audit3"
NOTES = ROOT / "research/blind/out/blind_test"
MAX_ROWS = {"sim2": 45, "internet": 30, "sim3": 40}


def main():
    t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
    sn = pd.read_csv(ROOT / "research/next/scored_new.csv").set_index("qid").iloc[:, 0].astype(bool)
    t["sn"] = sn.reindex(t.index).fillna(False).astype(bool)
    t["kind"] = kinds(t)
    sub = pd.read_csv(ROOT / "submissions/trackA_cand_next_merge5.csv").set_index("id").parsed_value
    t["cur"] = sub.reindex(t.index)
    ch = pd.read_csv(ROOT / "research/next/merge/changes_merge5.csv")
    audited = set(ch.qid[ch.src.isin(["labaudit2", "sim3audit", "verify-keep"])])
    test = load_split("test")
    facts = pp._parse_facts(test)
    fam = pp.scene_families(test, pp.scene_links(test, facts, pp.FrameCache()))
    t["fam"] = t.video_id.map(fam)
    done3 = set()
    for f in (ROOT / "research/next/sim3audit/inputs").glob("*.json"):
        done3 |= set(json.loads(f.read_text())["clips"])
    prov = np.where(t.fact.notna() & np.isclose(t.cur, t.fact.fillna(-1), rtol=1e-6), "stated fact (exact; do not change)",
                    np.where(t.index.isin(audited), "earlier audit fix (two measurers agreed)", "agent measurement or pipeline"))
    t["prov"] = prov
    items = {}
    for kind in ("sim2", "internet", "sim3"):
        x = t[t.kind.eq(kind)]
        if kind == "sim3":
            x = x[~x.video_id.isin(done3) & ~x.video_id.map(pp.base_id).isin(done3)]
        fams = x[x.sn].groupby("fam").size().sort_values(ascending=False)
        packs, cur, n = [], [], 0
        for f, k in fams.items():
            if cur and n + k > MAX_ROWS[kind]:
                packs.append(cur)
                cur, n = [], 0
            cur.append(f)
            n += k
        if cur:
            packs.append(cur)
        for i, fs in enumerate(packs, 1):
            name = f"{kind}_{i:02d}"
            rows = x[x.fam.isin(fs)]
            items[name] = dict(item=name, kind=kind, families={f: sorted(set(rows.video_id[rows.fam.eq(f)])) for f in fs},
                               rows=[dict(qid=int(q), video_id=r.video_id, video_path=str(r.video_path), category=r.category,
                                          scored=bool(r.sn), question=r.question, prior=r.prior, depth_info=r.depth_info,
                                          target_unit=r.target_unit, fps=float(r.fps), current_answer=float(r.cur),
                                          provenance=r.prov, agent_notes=str(NOTES / r.video_id / "notes.md"))
                                     for q, r in rows.iterrows()])
    (OUT / "inputs").mkdir(parents=True, exist_ok=True)
    for name, d in items.items():
        (OUT / "inputs" / f"{name}.json").write_text(json.dumps(d, indent=1))
    summ = pd.DataFrame([dict(item=k, families=len(d["families"]), clips=sum(map(len, d["families"].values())),
                              scored=sum(r["scored"] for r in d["rows"])) for k, d in items.items()])
    print(summ.to_string())
    print(summ.groupby(summ.item.str.split("_").str[0])[["clips", "scored"]].sum())
    (OUT / "items.json").write_text(json.dumps(list(items)))


if __name__ == "__main__":
    main()
