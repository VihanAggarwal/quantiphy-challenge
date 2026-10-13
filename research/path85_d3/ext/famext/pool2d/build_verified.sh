#!/bin/bash
# Verifier rebuild of the fam2d variants (no API calls, repo read-only) + the corrected D2 variant.
set -e
P=/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ext/pool2d
PY="nice -n 10 /home/user/quantiphy-challenge/.venv/bin/python"
bash $P/rebuild/build_all.sh                     # investigator pipeline, W pointed at $P/rebuild (reproduces fam2d CSVs byte-identically)
cd $P/rebuild
# corrected D2 variant: 2D votes only + D2 T, plus question-wording guard (drops the mismatched road group 387/390/400)
$PY build_verified.py --name pool2d_D2_2dvotes_T_qtext --d2T --cap2 0.25 --smax 0.35 --qtext --outdir $P/verified
rm -f $P/verified/pool2d_D2_2dvotes_T_qtext_S2.csv
cp fam2d_S2_pool2d.csv $P/verified/pool2d_S2_2dvotes.csv
cd $P
$PY fmt.py verified/pool2d_D2_2dvotes_T_qtext_D2.csv verified/pool2d_S2_2dvotes.csv
