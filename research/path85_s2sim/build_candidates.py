"""Candidates on submissions/trackA_cand_physb2_on_p21.csv (no API; test inputs only; validation labels only in
evaluate()).

A  birdfam : bird family simulation_0088-0091 (four cameras of the same two birds). Sky-mask pixel tracks
             (birdfam.py) give a big/small pixel-speed ratio of 1.629-1.669 in all four clips vs the stated
             17.98/11 = 1.635, so the family's stated speeds hold in every clip; the clip scale is anchored on them.
             Speeds -> stated values; body lengths, wingspans (max over the flight, top-down views 0088/0089),
             distances -> mask measurements x anchored scale. 0089's own prior ("small bird length 0.94 m") is
             inconsistent with that scale by 1.77x and is not used.
B  namefam : A + stated facts of directly linked 2D-simulation siblings (|id gap| <= 3, >= 2 shared object names)
             that the facts rule does not reach: same object, speed facts untimed or at the asked time, no
             acceleration of the object in the target clip, value within 0.8-1.25x of the current answer.
Validation-overlap rows are never changed.
"""
from __future__ import annotations
import ast, re, subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from qp import postprocess as pp
from qp.data import load_test, load_validation
from qp.mra import item_scores

BASE = ROOT / "submissions/trackA_cand_physb2_on_p21.csv"

def overlap_mask(t):
    v = load_validation()
    vk = {(a, pp.norm_question(b)) for a, b in zip(v.video_id, v.question)}
    return pd.Series([(a, pp.norm_question(b)) in vk for a, b in zip(t.video_id, t.question)], index=t.index)

def bird_answer(row, M):
    """Answer one bird-family question from the mask measurements M (index video_id)."""
    q = row.question.lower(); v = row.video_id; m = M.loc[v]
    which = "big" if "big bird" in q else ("small" if "small bird" in q else None)
    if "distance" in q:
        t = float(re.search(r"at\s*([\d.]+)\s*s", q).group(1))
        return {0.2: m.d02, 0.3: m.d03, 0.5: m.d05}[t], "mask distance x anchored scale"
    if "speed" in q:
        return {"big": 17.98, "small": 11.0}[which], "stated family speed (constant; pixel ratio check)"
    if "wingspan" in q or "width" in q:
        span = max(M.loc[["simulation_0088", "simulation_0089"], f"span_{which}"])
        return float(span), "max wingspan over the flight (top-down views 0088/0089)"
    if "length" in q:
        return float(m[f"len_{which}"]), "mask body length x anchored scale"
    return None, ""

def build_birdfam(t, base, ov):
    M = pd.read_csv(HERE / "out_birdfam_measure.csv").set_index("video_id")
    rows = t[t.video_id.isin(M.index)]
    new, log = base.copy(), []
    for q, r in rows.iterrows():
        val, why = bird_answer(r, M)
        if val is None or ov[q]:
            continue
        new[q] = val
        log.append(dict(qid=q, video_id=r.video_id, category=r.category, question=r.question, old=base[q], new=val, why=why))
    return new, pd.DataFrame(log)

def build_namefam(t, base, ov, skip):
    c = pd.read_csv(HERE / "out_namefam_cands_ms2.csv")
    links = pd.read_csv(HERE / "out_namefam_links_ms2.csv")
    direct = {}
    for a, b, s in links.itertuples(index=False):
        direct[(a, b)] = direct[(b, a)] = len(ast.literal_eval(s))
    num = lambda v: int(re.search(r"simulation_(\d+)", v).group(1))
    c = c[c.category.isin(["S2", "D2"]) & ~c.used_now]
    c["pair_ok"] = [direct.get((pp.base_id(a), pp.base_id(b)), 0) >= 2 and abs(num(a) - num(b)) <= 3
                    for a, b in zip(c.video_id, c.src)]
    c = c[c.pair_ok]
    new, log = base.copy(), []
    for q, g in c.groupby("qid"):
        vals = np.unique(np.round(g.value.to_numpy(float), 9))
        if len(vals) != 1 or ov[q] or q in skip:
            continue
        val = float(vals[0]); r = base[q] / val
        if not (0.8 <= r <= 1.25):
            continue
        new[q] = val
        log.append(dict(qid=q, video_id=g.video_id.iloc[0], category=g.category.iloc[0], question=g.question.iloc[0],
                        old=base[q], new=val, why=f"stated by {','.join(sorted(set(g.src)))}: {g.line.iloc[0]}"))
    return new, pd.DataFrame(log)

def write(new, out):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": new.index, "parsed_value": new.to_numpy()}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(out)], check=True)

def evaluate_val():
    """Validation (labels for evaluation only): the bird method on 0089's validation questions vs the pipeline."""
    v = load_validation(); v = v[v.video_id == "simulation_0089"].copy()
    M = pd.read_csv(HERE / "out_birdfam_measure.csv").set_index("video_id")
    pred = []
    for r in v.itertuples():
        q = r.question.lower()
        if "average speed" in q:
            pred.append(17.98 if "big" in q else 11.0)
        elif "distance" in q:
            pred.append(M.loc["simulation_0089", "d05"])
        elif "width" in q:
            w = "big" if "big" in q else "small"
            pred.append(max(M.loc[["simulation_0088", "simulation_0089"], f"span_{w}"]))
        else:
            pred.append(M.loc["simulation_0089", "len_big" if "big" in q else "len_small"])
    v["method"] = pred
    for run in ("val_hr_v1_high/val_hires.csv", "val_hr_v2_high/val_hires.csv", "val_opus_high/val.csv"):
        rr = pd.read_csv(ROOT / "runs" / run).set_index("id").parsed_value
        v[run.split("/")[0]] = rr.reindex(v.qid).to_numpy()
    cols = ["method", "val_hr_v1_high", "val_hr_v2_high", "val_opus_high"]
    for c in cols:
        v["it_" + c] = item_scores(v[c], v.answer)
    pd.set_option("display.width", 220)
    print(v[["qid", "question", "answer"] + cols + ["it_" + c for c in cols]].round(3).to_string())
    print("item sums:", {c: round(float(v["it_" + c].sum()), 2) for c in cols}, "n =", len(v), "(1 clip)")

def main():
    t = load_test().set_index("qid")
    b = pd.read_csv(BASE).set_index("id").parsed_value.astype(float).reindex(t.index)
    ov = overlap_mask(t)
    A, la = build_birdfam(t, b, ov)
    B, lb = build_namefam(t, A, ov, skip=set(la.qid))
    pd.set_option("display.width", 220); pd.set_option("display.max_colwidth", 70)
    for name, log in (("birdfam", la), ("namefam extra", lb)):
        print(f"== {name}: {len(log)} rows {log.category.value_counts().to_dict() if len(log) else {}}")
        if len(log):
            print(log.assign(ratio=log.new / log.old).round(4).to_string(index=False))
    la.to_csv(HERE / "out_changes_birdfam.csv", index=False)
    pd.concat([la, lb]).to_csv(HERE / "out_changes_namefam.csv", index=False)
    write(A, ROOT / "submissions/trackA_cand_s2birdfam_on_physb2.csv")
    write(B, ROOT / "submissions/trackA_cand_s2namefam_on_physb2.csv")
    evaluate_val()

if __name__ == "__main__":
    main()
