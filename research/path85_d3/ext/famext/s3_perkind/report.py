from expect import *
lofo=pd.read_pickle(OUT+'/lofo_rows.pkl')
res,allch=pickle.load(open(OUT+'/build_res.pkl','rb'))
summ=json.load(open(OUT+'/expect_summary.json'))
names=['raw','Kall','Kkind','Ksize','Kspd','P','P_Kall','P_Kkind','P_Kd3all_s3kind','P_Kd3all_s3none']
L={c:{k:round(float(v),3) for k,v in lofo[lofo.cat==c][names].mean().items()} for c in ['S3','D3']}
LK={f'{c}/{k}':{n:round(float(v),3) for n,v in g[names].mean().items()}|{'n':len(g)} for (c,k),g in lofo.groupby(['cat','kind'])}
new,why=build(rule_P=True,s3mode='kind',rule_DS=True)
tab=[]
for q in allch['S3_PK_DS']:
    r=ti.loc[q]; V,src=proxy(q)
    tab.append(dict(qid=int(q),video=r.video_id,q=r.question[:90],p5=round(p5[q],4),new=round(new[q],4),rule=why.get(q),proxy=V,proxy_src=src))
kn=[q for q in known if ti.loc[q,'category']=='S3']
known_s3={'n':len(kn),'p5':round(np.mean([m1(p5[q],known[q]) for q in kn]),4),'S3_PK_DS':round(np.mean([m1(new[q],known[q]) for q in kn]),4)}
rep=dict(key='s3_perkind',workdir=OUT,
 build_script=OUT+'/build_s3.py (imports s3pool.py, lofo_kind.py, common.py; reads big/scenegraph/work TS.pkl, eq3.pkl, transfers3.pkl and merge/S3,D3 decisions.csv)',
 eval_scripts=[OUT+'/lofo_kind.py',OUT+'/eval_pool.py',OUT+'/eval_famknown.py',OUT+'/eval2.py',OUT+'/eval3.py',OUT+'/expect.py',OUT+'/twin_avg.py'],
 lofo_row_mean=L, lofo_by_kind=LK, known_S3_40rows=known_s3, variants={k:res[k]|summ[k] for k in res}, main_changed_rows=tab)
json.dump(rep,open(OUT+'/report.json','w'),indent=1,default=str)
print(json.dumps({k:rep[k] for k in ['lofo_row_mean','known_S3_40rows']},indent=1))
print(pd.DataFrame(tab).to_string())
