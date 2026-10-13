"""Lever A enumeration: simulation clips C (2D and 3D) with a directly linked sibling S (|id gap| <= 3 and >= 2 shared
object names, or depth/prior/scenario link) that STATES a speed/acceleration of an object named in C, where that fact
is not C's own prior. Test inputs only (question/prior/depth text)."""
from __future__ import annotations
import itertools, re, sys
from collections import defaultdict
from pathlib import Path
import pandas as pd
HERE = Path(__file__).parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from qp import postprocess as pp
from qp.data import load_test
from qp.open.qwen_vl import parse_question_text, parse_prior_text

def num(v):
    m = re.match(r"simulation_(\d+)", v); return int(m.group(1)) if m else None

def main():
    t = load_test()
    df = pp._questions(t)
    df["base"] = df.video_id.map(pp.base_id)
    sim = df[df.video_id.map(pp.is_simulation)].copy()
    objs = defaultdict(set)
    for v, q, p in zip(sim.base, sim.question, sim.prior):
        for o in parse_question_text(q)["objects"] + parse_prior_text(p)["objects"]:
            n = " ".join(pp._tokens(pp._clean_object(o)))
            if n: objs[v].add(n)
    facts = pp._parse_facts(df)
    links = pp.scene_links(df, facts, None)
    direct = defaultdict(set)
    for k in ("depth", "prior", "scenario"):
        for a, b in links[k]:
            direct[(pp.base_id(a), pp.base_id(b))].add(k); direct[(pp.base_id(b), pp.base_id(a))].add(k)
    bases = sorted(objs, key=lambda b: num(b) or 0)
    for a, b in itertools.combinations(bases, 2):
        if abs(num(a) - num(b)) > 3: continue
        sh = {x for x in objs[a] for y in objs[b] if len(x) > 2 and pp._same_object(x, y) >= 0.8}
        if len(sh) >= 2:
            direct[(a, b)].add(f"names{len(sh)}"); direct[(b, a)].add(f"names{len(sh)}")
    cat = sim.groupby("base").category.agg(lambda s: ",".join(sorted(set(s))))
    prior = sim.groupby("base").prior.first()
    rows = []
    for f in facts:
        if f.kind not in ("speed", "acceleration") or not pp.is_simulation(f.video_id): continue
        S = pp.base_id(f.video_id)
        for C in bases:
            if C == S or (S, C) not in direct: continue
            hit = [x for x in objs[C] if pp._same_object(x, f.obj) >= 0.8]
            if not hit: continue
            own = {pp.norm_ws(x) for x in str(prior[C]).split("\n")}
            if pp.norm_ws(f.line) in own: continue
            rows.append(dict(C=C, cat=cat[C], C_prior=prior[C], S=S, link="+".join(sorted(direct[(S, C)])),
                             fact=f.line, obj=f.obj, kind=f.kind, timed=f.timed, hit=";".join(hit)))
    d = pd.DataFrame(rows).drop_duplicates()
    d.to_csv(HERE / "out_links.csv", index=False)
    pd.set_option("display.width", 260); pd.set_option("display.max_colwidth", 60); pd.set_option("display.max_rows", 500)
    print(len(d), "pairs;", d.C.nunique(), "clips"); print(d.groupby("cat").C.nunique())
    print(d.to_string())

if __name__ == "__main__":
    main()
