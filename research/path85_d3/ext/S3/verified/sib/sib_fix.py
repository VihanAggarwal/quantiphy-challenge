"""Verifier probe: re-run the SIB rule with the question's trailing time span stripped from the object name
('... of the boat from the beginning to the end in m/s' parsed obj='boat from the beginning to the end')."""
import sys, re
sys.dont_write_bytecode = True
import os
os.chdir('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/merge/S3/verified/sib')
sys.path.insert(0, '/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/big/priors_as_labels')
from valcheck import *
import pandas as pd, numpy as np
t_all = pd.read_pickle(SP + 'test.pkl')
v3 = pd.read_csv('/home/user/quantiphy-challenge/submissions/trackA_v3_best_per_category.csv').set_index('id').parsed_value
M = pd.read_csv('../../S3_merged.csv').set_index('id').parsed_value
cat = t_all.set_index('qid').category
qs = t_all.copy()
STRIP = r'\s+from\s+(?:the\s+)?beginning\s+to\s+(?:the\s+)?end\b|\s+from\s+[\d.]+\s*s\s+to\s+[\d.]+\s*s\b'
qs['question'] = qs.question.str.replace(STRIP, '', regex=True, flags=re.I)
R0 = rule(t_all, t_all); R1 = rule(qs, t_all)
R0['cat'] = R0.qid.map(cat); R1['cat'] = R1.qid.map(cat)
new = R1[~R1.qid.isin(R0.qid)]
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 90)
new = new.assign(v3=new.qid.map(v3), merged=new.qid.map(M))
new['ratio'] = new.value / new.v3
print(new[['qid', 'cat', 'video_id', 'question', 'value', 'v3', 'merged', 'ratio', 'src']].to_string())
new.to_pickle('sib_new.pkl')
