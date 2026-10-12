"""Load post-processed annotations (refine off, dense motion; the D2 setting of probe 8) for some test videos."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
import run_claude as rc  # noqa: E402
from qp.data import load_split  # noqa: E402


def load(videos, split="test", run="test_v1_high_854", refine=False):
    df = load_split(split)
    df = df[df.video_id.isin(videos)].copy()
    rec = rc.load_records(ROOT / "runs" / run / split / "records")
    rec = {k: v for k, v in rec.items() if k in set(videos)}
    return df, rec, rc.annotations(df, rec, refine_priors=refine, dense="motion",
                                   dense_cache=ROOT / "runs" / "_dense_cache" / split, dense_workers=1)
