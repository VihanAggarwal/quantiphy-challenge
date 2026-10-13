import sys, pickle
sys.path.insert(0,'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/merge/D3')
from load_cands import *
MD=SP+'/merge/D3'
C={k:load(k) for k in CANDS}
sg=pickle.load(open(MD+'/sg_why.pkl','rb'))
ti=sg['ti']
# P4 step labels
st=pickle.load(open(SP+'/hyp/D3/review_code/steplog.pkl','rb')); L=st['L']
p4why=L[L.changed].groupby('qid').step.agg(lambda s:'+'.join(s)).to_dict()
sib=pd.read_pickle(SP+'/big/priors_as_labels/transfer_rebuilt.pkl'); sib=sib[sib.category=='D3']
sibsrc=dict(zip(sib.qid,sib.src))
A=sg['A']; Tsrc=dict(zip(A.qid,A.src+' | '+A.line.astype(str)+' | '+A.why.astype(str)))
run=pd.read_csv(R+'/runs/test_v1_high_854/test.csv').set_index('id')
V=V3.set_index('id')
d3=list(V3.id[V3.cat=='D3'])
def ch(k,q): return not np.isclose(C[k][q],v3[q],rtol=1e-9)
rows=[]
for q in d3:
    who=[k for k in ['P4','TKP','TP','T','sib','cam','lm'] if ch(k,q)]
    if not who: continue
    r=dict(qid=q,vid=V.loc[q,'video_id'],src=V.loc[q,'video_source'],kind=ti.loc[q,'tkind'],v3=v3[q],
           geo=run.loc[q,'geo_value'],direct=run.loc[q,'direct_value'],method=run.loc[q,'method'],
           who='+'.join(who))
    for k in CANDS: r[k]=C[k][q]
    r['p4why']=p4why.get(q,'')
    r['tkpwhy']=sg['TKP'][1].get(q,'') if ch('TKP',q) else ''
    r['tpwhy']=sg['TP'][1].get(q,'') if ch('TP',q) else ''
    r['twhy']=sg['T'][1].get(q,'') if ch('T',q) else ''
    r['sibsrc']=sibsrc.get(q,'')
    r['Tsrc']=Tsrc.get(q,'')
    r['question']=V.loc[q,'question']; r['prior']=V.loc[q,'ground_truth_prior']; r['depth']=V.loc[q,'depth_info']
    rows.append(r)
M=pd.DataFrame(rows)
M.to_pickle(MD+'/master.pkl')
print(len(M)); print(M.who.value_counts().to_string())
