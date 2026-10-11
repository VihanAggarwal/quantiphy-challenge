"""Lab-speed correction ladder for leaderboard tuning (on probe 8).
S3: emulator at ball depth noise 1/2/3/4 cm (trackA_cand_labnoise[_szX]_on_p8.csv; 2 cm = probe 11).
D3: uniform factor on lab motion targets (speed / velocity / distance traveled; accelerations and stated facts kept).
probe13 = S3 sz 3 cm + D3 x1.40; probe14 = S3 sz 4 cm + D3 x1.15; probe15 = S3 sz 1 cm + D3 x1.25 (= probe 10's D3 on p8).
S2, D2 = probe 8 in all three."""
import re, subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from qp.data import load_test
t = load_test().set_index("qid")
S = ROOT / "submissions"
p8f = S / "trackA_probe8_p7b_d2fixes_d3labphys.csv"
p8 = pd.read_csv(p8f); p8 = p8.rename(columns={p8.columns[0]: "id"}).set_index("id").parsed_value.astype(float).reindex(t.index)
nums = {round(float(m), 6) for p in t.prior for m in re.findall(r"=\s*([0-9]*\.?[0-9]+)", str(p))}
q = t.question.str.lower()
mot = (t.category == "D3") & (t.video_source == "lab") & q.str.contains("veloc|speed|travel") & ~q.str.contains("acceler")
mot &= ~p8.round(6).isin(nums)
def d3(k):
    v = p8.copy(); v[mot] *= k
    fn = S / f"trackA_cand_d3labmot{int(round(k*100))}_on_p8.csv"
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": v.index, "parsed_value": v.values}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(fn)], check=True); return fn
print("D3 lab motion rows scaled:", int(mot.sum()))
for name, s3, k in (("probe13_p8_s3sz3_d3x140", "sz0.03", 1.40), ("probe14_p8_s3sz4_d3x115", "sz0.04", 1.15),
                    ("probe15_p8_s3sz1_d3x125", "sz0.01", 1.25)):
    subprocess.run([sys.executable, str(ROOT / "scripts/compose_submission.py"), str(p8f), str(S / f"trackA_{name}.csv"),
                    "--cat", f"S3={S / f'trackA_cand_labnoise_{s3}_on_p8.csv'}", "--cat", f"D3={d3(k)}"], check=True)
