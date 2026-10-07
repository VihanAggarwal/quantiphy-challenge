"""Download the public QuantiPhy datasets and the submission template into data/.

    python scripts/download_data.py            # validation + test + template
    python scripts/download_data.py --val-only

Needs network access to huggingface.co and quantiphy.stanford.edu. If the template
download fails, save it by hand from the portal ("submission template" link) to
data/submission_template/quantiphy_submission_template.csv.
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qp.data import TEMPLATE_CSV, TEST_DIR, VAL_DIR  # noqa: E402

TEMPLATE_URL = "https://quantiphy.stanford.edu/competition/eval/quantiphy_submission_template.csv"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--val-only", action="store_true")
    args = ap.parse_args()
    from huggingface_hub import snapshot_download

    targets = [("PaulineLi/QuantiPhy-validation", VAL_DIR)]
    if not args.val_only:
        targets.append(("PaulineLi/QuantiPhy", TEST_DIR))
    for repo, local in targets:
        print(f"downloading {repo} -> {local}")
        snapshot_download(repo_id=repo, repo_type="dataset", local_dir=local)

    if not args.val_only:
        TEMPLATE_CSV.parent.mkdir(parents=True, exist_ok=True)
        try:
            urllib.request.urlretrieve(TEMPLATE_URL, TEMPLATE_CSV)
            print(f"template -> {TEMPLATE_CSV}")
        except Exception as e:  # noqa: BLE001
            print(f"template download failed ({e}); save it by hand to {TEMPLATE_CSV}")


if __name__ == "__main__":
    main()
