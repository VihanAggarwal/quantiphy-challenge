"""Lab motion rows (S3/D3, lab clips) with their values in every relevant submission and the emulator factors.
Writes research/next/labmot/out/labmot_rows.pkl. No labels used (master.pkl 'val' only carried for validation-overlap rows,
which are unscored; used for measuring only)."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research/labnoise"))
from qp.data import load_test
from common import motion_kind

OUT = Path(__file__).resolve().parent / "out"; OUT.mkdir(exist_ok=True)
S = ROOT / "submissions"
t = load_test().set_index("qid")


def read(name):
    d = pd.read_csv(S / name)
    return d.rename(columns={d.columns[0]: "id"}).set_index("id").parsed_value.astype(float).reindex(t.index)


subs = {
    "p8": "trackA_probe8_p7b_d2fixes_d3labphys.csv",
    "sz1": "trackA_cand_labnoise_sz0.01_on_p8.csv",
    "sz2": "trackA_cand_labnoise_on_p8.csv",
    "sz3": "trackA_cand_labnoise_sz0.03_on_p8.csv",
    "sz4": "trackA_cand_labnoise_sz0.04_on_p8.csv",
    "p11": "trackA_probe11_p8_emu_labnoise.csv",
    "p13": "trackA_probe13_p8_s3sz3_d3x140.csv",
    "p14": "trackA_probe14_p8_s3sz4_d3x115.csv",
    "p15": "trackA_probe15_p8_s3sz1_d3x125.csv",
    "p16": "trackA_best_p16_p8_labnoiseS3D3.csv",
    "p17": "trackA_probe17_p16_stack.csv",
    "p18": "trackA_probe18_p16_physb_sizeenv_sim3d.csv",
    "p19": "trackA_probe19_p16_s3nopath_d3sz3.csv",
    "p20": "trackA_probe20_p16_s3nomid_d3sz4.csv",
    "p21": "trackA_best_p21.csv",
    "physb2": "trackA_cand_physb2_on_p21.csv",
    "u1": "trackA_u1_p22s2d2_s3sz4_d3emu3.csv",
    "u2": "trackA_u2_p23s2d2_s3nopath_d3emu4.csv",
    "u3": "trackA_u3_s3nomid_d3labdirect.csv",
    "u4": "trackA_u4_s3labdirect_d3labgm.csv",
    "combo2": "trackA_cand_combo2.csv",
    "combo3": "trackA_combo3_on_combo2.csv",
    "C1": "trackA_cand_C1_on_combo3.csv",
    "C1sol": "trackA_cand_C1_solS2S3.csv",
    "best": "trackA_probe_agent_sim2agent.csv",
}
V = pd.DataFrame({k: read(v) for k, v in subs.items()})
m = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
lab = t[(t.video_source == "lab") & t.category.isin(["S3", "D3"])].copy()
lab["kind"] = [motion_kind(q) for q in lab.question]
lab = lab[lab.kind.notna()]
R = lab[["video_id", "category", "kind", "question", "prior", "depth_info", "target_unit"]].join(V)
R = R.join(m[["scored", "overlap", "val", "fact", "fact_rule", "r_direct_value", "r_parsed_value", "r_method", "prov"]])
fr = {}
for tag, fn in (("1", "test_rows_cap1.6_sz0.01.csv"), ("2", "test_rows_cap1.6.csv"), ("3", "test_rows_cap1.6_sz0.03.csv"),
                ("4", "test_rows_cap1.6_sz0.04.csv")):
    x = pd.read_csv(ROOT / "research/labnoise/out" / fn).set_index("qid")
    fr["f" + tag] = x.factor
    if tag == "2":
        for c in ("cls", "sin_psi", "kind_eff", "stated_fact", "speed_si", "med_ratio", "exp_ratio"):
            fr[c] = x[c]
R = R.join(pd.DataFrame(fr))
R["event"] = R.video_id.str.extract(r"(captured_\d{4}[ab]?)")[0]
R.to_pickle(OUT / "labmot_rows.pkl")
pd.set_option("display.width", 250)
print(len(R), R.groupby(["category", "kind"]).size().to_dict())
print(R.groupby(["category", "kind", "cls"], dropna=False).size())
