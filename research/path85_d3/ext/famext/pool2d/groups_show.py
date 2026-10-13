import sys
sys.path.insert(0,'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ext/pool2d/rebuild')
from rule import *
from qp.parse import canonical_unit,_UNITS
pd.set_option('display.width',260); pd.set_option('display.max_colwidth',60)
t=pd.read_pickle(W+'/T.pkl'); ti=t.set_index('qid')
votes3d = sys.argv[1]=='3d'
cats=('S2','D2','S3','D3') if votes3d else ('S2','D2')
G=build_groups(t,unit='cam',cats=cats)
J=json.load(open(W+('/fam2d_P2D3D_T.json' if votes3d else '/fam2d_P2D_T.json')))
ch={int(k):v for k,v in J['changes'].items()}
want=[int(x) for x in sys.argv[2:]]
for gr in G:
    qs=[q for mem in gr['members'].values() for q,_ in mem]
    if not any(q in want for q in qs): continue
    print('=== group',gr['grp'],gr['kind'],'units',len(gr['ul']),'spread %.3f'%gr['spread'])
    rows=[]
    for u,mem in gr['members'].items():
        for q,lv in mem:
            r=ti.loc[q]
            rows.append(dict(qid=q,cam=u.replace('simulation_','s'),vid=r.video_id.replace('simulation_','s'),cat=r.category,q=r.question[:60],prior=str(r.prior)[:45],unit=r.target_unit,obj=r.tobj,p5=round(r.p5,4),si=round(np.exp(lv),4),camv=round(np.exp(gr['ul'][u]),4),new=round(ch[q]['new'],4) if q in ch else None))
    print(pd.DataFrame(rows).sort_values(['cam','vid']).to_string(index=False))
