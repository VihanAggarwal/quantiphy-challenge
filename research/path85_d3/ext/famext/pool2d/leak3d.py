import sys, pickle
sys.path.insert(0,'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ext/pool2d/rebuild')
from rule import *
t=pd.read_pickle(W+'/T.pkl'); ti=t.set_index('qid')
eq3=pickle.load(open(SP+'/big/scenegraph/work/eq3.pkl','rb'))
dec=pd.read_csv(SP+'/merge/D3/decisions.csv').set_index('qid')
J=json.load(open(W+'/fam2d_P2D3D_T.json')); ch={int(k):v for k,v in J['changes'].items() if v['why'] and v['why'].startswith('P')}
J2=json.load(open(W+'/fam2d_P2D_T.json')); ch2={int(k):v for k,v in J2['changes'].items() if v['why'] and v['why'].startswith('P')}
G=build_groups(t,unit='cam',cats=('S2','D2','S3','D3'))
n_g=0;n_leak=0;rows_leak=0;rows_3donly=0; dup=0
for gr in G:
    qs=[q for m in gr['members'].values() for q,_ in m]
    d2=[q for q in qs if q in ch and ti.loc[q,'category']=='D2']
    if not d2: continue
    n_g+=1
    q2d=set(q for q in qs if ti.loc[q,'category'] in ('S2','D2'))
    leak=False; vals3=[]
    for u,m in gr['members'].items():
        for q,lv in m:
            if ti.loc[q,'category'] in ('S3','D3'):
                src=dec.chosen_source.get(q,'?') if q in dec.index else 'S3'
                if q in eq3 and (set(eq3[q])&q2d) and 'SIM_P' in str(src): leak=True
                vals3.append(round(lv,6))
    if len(vals3)!=len(set(vals3)): dup+=1
    if leak: n_leak+=1; rows_leak+=len(d2)
    rows_3donly+=sum(1 for q in d2 if q not in ch2)
print('groups with changed D2 rows',n_g,'groups whose 3D votes are SIM_P pools that include the group\'s own 2D answers',n_leak,'D2 rows in them',rows_leak)
print('groups with duplicated identical 3D votes',dup,'; D2 rows changed only because of 3D votes',rows_3donly)
