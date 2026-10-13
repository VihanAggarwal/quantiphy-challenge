#!/bin/sh
# Rebuild the D3 extension variants (no API calls; test inputs only).
E=/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ext/d3rest
PY=/home/user/quantiphy-challenge/.venv/bin/python
cd /tmp
nice -n 10 $PY -c "import sys; sys.path.insert(0,'$E'); sys.path.insert(0,'/home/user/quantiphy-challenge'); import extfam; t,a,r=extfam.build(); t.to_pickle('$E/work/TS_ext.pkl')"
nice -n 10 $PY $E/s03_transfers.py > $E/work/s03.log 2>&1      # transfers_ext.pkl, eq_ext.pkl
nice -n 10 $PY $E/build_d3ext.py                                 # D3ext_*.csv, decisions_ext.csv, build_summary.json
# evaluation (measurement only): s04_lofo.py, s06_kobj.py, s07_single_fact_k.py, s08_lofo_spread.py, s09_famk.py
