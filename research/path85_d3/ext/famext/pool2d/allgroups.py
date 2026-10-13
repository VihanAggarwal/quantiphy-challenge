import sys
sys.path.insert(0,'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ext/pool2d/rebuild')
from rule import *
t=pd.read_pickle(W+'/T.pkl'); ti=t.set_index('qid')
votes3d = sys.argv[1]=='3d'
cats=('S2','D2','S3','D3') if votes3d else ('S2','D2')
G=build_groups(t,unit='cam',cats=cats)
J=json.load(open(W+('/fam2d_P2D3D_T.json' if votes3d else '/fam2d_P2D_T.json')))
ch={int(k):v for k,v in J['changes'].items()}
n=0
for gr in G:
    qs=[q for mem in gr['members'].values() for q,_ in mem]
    cq=[q for q in qs if q in ch and ch[q]['why'] and ch[q]['why'].startswith('P')]
    if not cq: continue
    n+=1
    g=ti.loc[qs]
    qtexts=sorted(set(re.sub(r'simulation_\d+','',x) for x in g.question))
    units=sorted(set(map(str,g.target_unit)))
    vids=sorted(set(v.replace('simulation_','') for v in g.video_id))
    cats_=g.category.value_counts().to_dict()
    vals={u.replace('simulation_',''):round(float(np.exp(v)),3) for u,v in gr['ul'].items()}
    newv=round(ch[cq[0]]['new'],3)
    print(f"[{n}] {gr['kind']} cats={cats_} units={units} n_changed={len(cq)} votes={vals} -> {newv}")
    print('    vids', vids)
    for q in qtexts: print('    Q:',q)
    print('    objs', sorted(set(g.tobj)), 'dims', sorted(set(map(str,g.tdim))), 'times', sorted(set(map(str,g.ttime))), 'priors', sorted(set(g.prior))[:4])
