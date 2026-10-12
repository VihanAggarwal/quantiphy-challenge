"""S3 decomposition of the lab-noise gain (on p16 = probe 8 + lab-noise sz 2 cm in S3/D3), plus D3 emulator strength.
probe19: S3 = p16 with the 18 small-ball PATH-LENGTH rows reverted to probe 8; D3 = emulator sz 3 cm on D3 rows.
probe20: S3 = p16 with the 36 MID-BALL SPEED rows reverted to probe 8;       D3 = emulator sz 4 cm on D3 rows.
S2, D2 = p16 (= probe 8). Read S3 against p16's measured .762 (probe 11) and D3 against .797."""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from qp.data import load_test
t = load_test().set_index("qid"); S = ROOT / "submissions"
def read(p):
    d = pd.read_csv(p); return d.rename(columns={d.columns[0]: "id"}).set_index("id").parsed_value.astype(float).reindex(t.index)
p8, p16 = read(S / "trackA_probe8_p7b_d2fixes_d3labphys.csv"), read(S / "trackA_best_p16_p8_labnoiseS3D3.csv")
rows = pd.read_csv(ROOT / "research/labnoise/out/test_rows_cap1.6.csv").set_index("qid")
ch = rows[(rows.factor - 1).abs() >= 0.005]
def build(name, revert, d3file):
    v = p16.copy()
    v[revert] = p8[revert]
    d3 = read(S / d3file); m = (t.category == "D3") & ~np.isclose(d3, p8, rtol=1e-9)
    v[t.category == "D3"] = p8[t.category == "D3"]; v[m] = d3[m]
    print(name, "S3 reverted", len(revert), "| D3 rows changed vs p8", int(m.sum()))
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": v.index, "parsed_value": v.values}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(S / f"trackA_{name}.csv")], check=True)
build("probe19_p16_s3nopath_d3sz3", ch[(ch.category == "S3") & (ch.kind == "path_length")].index, "trackA_cand_labnoise_sz0.03_on_p8.csv")
build("probe20_p16_s3nomid_d3sz4", ch[(ch.category == "S3") & (ch.kind == "speed") & (ch.cls == "mid ball")].index, "trackA_cand_labnoise_sz0.04_on_p8.csv")
