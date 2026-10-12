"""Print rows whose geometry answer changes under the forward-difference emulation (test replay)."""
import sys
import pandas as pd
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 70); pd.set_option('display.max_rows', 300)
tag = sys.argv[1]
off = pd.read_csv(f'research/internet/out/{tag}_off.csv'); on = pd.read_csv(f'research/internet/out/{tag}_on.csv')
d = pd.read_csv('submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv')[['id', 'video_id', 'inference_type', 'question', 'parsed_value']]
m = d.merge(off[['id', 'geo_value']].rename(columns={'geo_value': 'g0'}), on='id') \
     .merge(on[['id', 'geo_value', 'flags']].rename(columns={'geo_value': 'g1'}), on='id')
m['r'] = m.g1 / m.g0
x = m[(m.r - 1).abs() > 0.003]
print(len(x), 'changed of', len(m))
print(x[['id', 'video_id', 'inference_type', 'question', 'parsed_value', 'g0', 'g1', 'r']].to_string())
