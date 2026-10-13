"""Wider 2D-simulation families by object names: clips within +-ID_GAP ids whose questions/priors name the same
(distinctive) objects. Lists stated facts (other clips' priors) that answer a question but that the current facts
rule does not reach. Test INPUTS only (question/prior text) + base predictions for ratio diagnostics."""
from __future__ import annotations
import re, itertools
from collections import defaultdict
from common import *
from qp import postprocess as pp
from qp.open.qwen_vl import parse_question_text, parse_prior_text
from qp.parse import _UNITS

ID_GAP = 3
MIN_SHARED = int(__import__('os').environ.get('MIN_SHARED', '1'))

def num(v):
    m = re.match(r"simulation_(\d+)", v); return int(m.group(1)) if m else None

def objects_of(df):
    out = defaultdict(set)
    for v, q, p in zip(df.base, df.question, df.prior):
        t = parse_question_text(q)
        for o in t["objects"]:
            out[v].add(" ".join(pp._tokens(pp._clean_object(o))))
        pr = parse_prior_text(p)
        for o in pr["objects"]:
            out[v].add(" ".join(pp._tokens(pp._clean_object(o))))
    return out

def main():
    t = test_table()
    df = pp._questions(t.reset_index())
    df["base"] = df.video_id.map(pp.base_id)
    sim2 = df[df.video_id.map(pp.is_simulation)]
    objs = objects_of(sim2)
    bases = sorted(objs, key=lambda b: num(b) or 0)
    uf = pp._UF()
    links = []
    for a, b in itertools.combinations(bases, 2):
        na, nb = num(a), num(b)
        if na is None or nb is None or abs(na - nb) > ID_GAP:
            continue
        shared = {x for x in objs[a] for y in objs[b] if x and y and pp._same_object(x, y) >= 0.8 and len(x) > 2}
        if len(shared) >= MIN_SHARED:
            uf.union(a, b); links.append((a, b, sorted(shared)))
    fam = {b: uf.find(b) for b in bases}
    facts = pp._parse_facts(df)
    accel = pp._accel_objects(df, facts)
    cur = pd.read_csv(Path(__file__).parent / "out_facts_log.csv")
    used = set(cur[cur.applied].qid)
    rows = []
    for r in sim2.itertuples():
        tq = parse_question_text(r.question)
        if tq["kind"] not in pp.FACT_KINDS or len(tq["objects"]) != 1:
            continue
        obj = pp._clean_object(tq["objects"][0])
        unit = pp._row_unit(r, tq["kind"])
        if unit is None:
            continue
        dim = pp._DIM_SYN.get(tq["dimension"], tq["dimension"])
        for f in facts:
            if not pp.is_simulation(f.video_id) or fam.get(pp.base_id(f.video_id)) != fam.get(r.base):
                continue
            if f.video_id == r.video_id and pp.norm_ws(f.line) in {pp.norm_ws(x) for x in str(r.prior).split("\n")}:
                continue
            if f.kind != tq["kind"] or pp._same_object(obj, f.obj) < pp.MIN_NAME:
                continue
            if tq["kind"] == "size" and dim != f.dimension:
                continue
            if tq["kind"] == "speed" and any(pp._same_object(obj, a) >= pp.MIN_NAME for a in accel.get(r.video_id, [])):
                continue
            if tq["kind"] != "size" and f.timed and (tq["time"] is None or f.time is None or abs(tq["time"] - f.time) > 1e-6):
                continue
            rows.append(dict(qid=r.qid, video_id=r.video_id, category=t.category[r.qid], kind=tq["kind"], qtime=tq["time"],
                             window=tq["window"], obj=obj, src=f.video_id, line=f.line, value=f.si / _UNITS[unit][0],
                             base=t.base[r.qid], geo=t.run_geo_value[r.qid], direct=t.run_direct_value[r.qid],
                             used_now=r.qid in used, question=r.question))
    out = pd.DataFrame(rows)
    out["ratio_base"] = out.base / out.value
    out.to_csv(Path(__file__).parent / ("out_namefam_cands_ms%d.csv" % MIN_SHARED), index=False)
    pd.DataFrame(links, columns=["a", "b", "shared"]).to_csv(Path(__file__).parent / ("out_namefam_links_ms%d.csv" % MIN_SHARED), index=False)
    new = out[~out.used_now]
    print(f"links {len(links)}; candidate (question, fact) pairs {len(out)}, not used now {len(new)} on {new.qid.nunique()} qids")
    print(new.groupby(["category", "kind"]).qid.nunique())
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70)
    print(new[["qid", "video_id", "category", "kind", "qtime", "obj", "src", "line", "value", "base", "ratio_base"]].to_string())

if __name__ == "__main__":
    main()
