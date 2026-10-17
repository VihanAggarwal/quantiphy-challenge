import sys, re
sys.path.insert(0, '/home/user/quantiphy-challenge'); sys.path.insert(0, '/home/user/quantiphy-challenge/research/trackb_dense')
import pandas as pd
from tbcommon import questions
t = questions('test')
q = t.question.str.lower()
m = q.str.contains(r'width', regex=True) & q.str.contains(r'\bcars?\b', regex=True)
b1 = q.str.contains(r"\bwidth of the (?:\w+ )?car\b", regex=True)
B1 = pd.read_csv('submissions/trackB_cand_B1.csv').set_index('id').parsed_value
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 120); pd.set_option('display.max_rows', 500)
x = t[m & ~b1][['qid','category','video_id','target_unit','question']].copy()
x['B1'] = x.qid.map(B1)
x['toy'] = q[m & ~b1].str.contains('toy') | t.prior.astype(str).str.lower()[m & ~b1].str.contains('toy')
print(len(x)); print(x.to_string())
