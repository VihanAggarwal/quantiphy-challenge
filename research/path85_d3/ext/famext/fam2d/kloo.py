from tab import *
t=pd.read_pickle(W+'/T.pkl').set_index('qid')
rows=[]
cur=None
for line in open(SP+'/big/scene_graph/T_list.txt'):
    if line.startswith('====='): cur=line.split()[1]; continue
    if cur not in ('S2','D2'): continue
    q=int(line.split()[0]); val=float(re.search(r'-> ([\d.eE+-]+)',line).group(1))
    rows.append(dict(qid=q,cat=cur,V=val))
F=pd.DataFrame(rows).drop_duplicates('qid')
F['video_id']=t.loc[F.qid,'video_id'].values
F['base_ans']=np.where(F.cat=='S2',t.loc[F.qid,'p4'].values,t.loc[F.qid,'p5'].values)
F['lk']=np.log(F.V/F.base_ans)
print(F.groupby('video_id').lk.agg(['size','mean']).round(3).to_string())
res=[]
for v,g in F.groupby('video_id'):
    if len(g)<2: continue
    for i,r in g.iterrows():
        k=np.median(np.r_[g.drop(i).lk.values,0.0])
        res.append(dict(video_id=v,raw=mra1(r.base_ans,r.V),K=mra1(r.base_ans*np.exp(k),r.V)))
R=pd.DataFrame(res); print(R.to_string()); print(R[['raw','K']].mean())
