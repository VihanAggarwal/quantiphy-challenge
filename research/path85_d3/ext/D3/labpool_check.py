import sys, os, pickle
MD='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/merge/D3'
sys.path.insert(0,'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/big/scene_graph')
import fix_build as FB
import numpy as np, pandas as pd
pd.set_option('display.width',320); pd.set_option('display.max_colwidth',60); pd.set_option('display.max_rows',500)
ti=FB.ti; v3=dict(FB.v3)
p4=pd.read_csv('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/hyp/final/D3_main_transfer_fixed.csv'); p4=dict(zip(p4.id,p4.parsed_value))
s3p4=pd.read_csv('/home/user/quantiphy-challenge/submissions/trackA_probe4_s2twin_d2refineoff_s3split_d3fixes.csv'); s3p4=dict(zip(s3p4.id,s3p4.parsed_value))
def run(base):
    FB.v3=base
    import labpool2; labpool2.v3=base
    log=[]
    LP,lw=FB.lab_pool_fixed(FB.t,cats=('S3','D3','D2'),log=log)
    FB.v3=v3; labpool2.v3=v3
    return LP,lw,log
LP0,lw0,log0=run(v3)
# base with P4 lab D3 values
b1=dict(v3)
for q in ti.index:
    if ti.loc[q,'category']=='D3' and ti.loc[q,'video_source']=='lab': b1[q]=p4[q]
LP1,lw1,log1=run(b1)
# + S3 evidence from probe 4 S3 (lab sizes geometry)
b2=dict(b1)
for q in ti.index:
    if ti.loc[q,'category']=='S3': b2[q]=s3p4[q]
LP2,lw2,log2=run(b2)
rows=[]
for q in sorted(set(LP0)|set(LP1)|set(LP2)):
    if ti.loc[q,'category']!='D3': continue
    rows.append(dict(qid=q,vid=ti.loc[q,'video_id'],obj=ti.loc[q,'tobj'],dim=ti.loc[q,'tdim'],v3=v3[q],p4=p4[q],lp0=LP0.get(q),w0=lw0.get(q),lp1=LP1.get(q),w1=lw1.get(q),lp2=LP2.get(q)))
X=pd.DataFrame(rows)
X['d01']=X.lp1/X.lp0; X['d12']=X.lp2/X.lp1
print(X.round(3).to_string())
print('log0',log0); print('log1',log1)
X.to_pickle(MD+'/labpool_check.pkl')
pickle.dump(dict(LP1=LP1,lw1=lw1,LP0=LP0,lw0=lw0,LP2=LP2,lw2=lw2),open(MD+'/labpool_runs.pkl','wb'))
