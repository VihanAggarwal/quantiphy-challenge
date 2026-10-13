#!/bin/bash
# Rebuild the 2D scene-family pooling variants on probe 5 (no API calls; reads the repo read-only).
set -e
W=/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ext/fam2d
PY="nice -n 10 /home/user/quantiphy-challenge/.venv/bin/python"
cd $W
$PY tab.py            # question table: test inputs + Claude specs + v2/v3/p4/p5 answers
$PY fam.py            # scene families / scenarios from big/scenegraph/families.json
$PY cams.py           # thumbnail similarity (qp.postprocess FrameCache, cache copied to ./ppcache)
$PY edges.py          # lighting-robust high-pass edge similarity of family clips
$PY camclust.py       # camera-view clusters (vote units)
$PY build.py --name fam2d_P2D --cap2 0.25 --smax 0.35                     # S2 deliverable (2D votes)
$PY build.py --name fam2d_P2D3D_T --votes3d --d2T --cap2 0.25 --smax 0.35 # D2 deliverable (2D+3D votes, + D2 T)
$PY build.py --name fam2d_P2D_T --d2T --cap2 0.25 --smax 0.35             # D2 conservative alternative (2D votes, + D2 T)
cp fam2d_P2D_S2.csv fam2d_S2_pool2d.csv
cp fam2d_P2D3D_T_D2.csv fam2d_D2_pool3dvotes_T.csv
cp fam2d_P2D_T_D2.csv fam2d_D2_pool2d_T.csv
$PY evalknown.py fam2d_P2D fam2d_P2D3D_T fam2d_P2D_T
$PY final_eval.py > final_eval.log
