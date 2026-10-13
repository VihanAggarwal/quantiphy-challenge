import sys, cv2
sys.path.insert(0,'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ext/pool2d/rebuild')
from rule import *
t=pd.read_pickle(W+'/T.pkl'); ti=t.set_index('qid')
J=json.load(open(W+'/fam2d_P2D_T.json')); ch={int(k) for k,v in J['changes'].items() if v['why'] and v['why'].startswith('P')}
G=build_groups(t,unit='cam',cats=('S2','D2'))
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
cache={}
def nf(v):
    if v not in cache:
        c=cv2.VideoCapture(D+v+'.mp4'); cache[v]=(int(c.get(cv2.CAP_PROP_FRAME_COUNT)),round(c.get(cv2.CAP_PROP_FPS),2))
    return cache[v]
for gr in G:
    qs=[q for m in gr['members'].values() for q,_ in m]
    if gr['kind']=='size' or not (set(qs)&ch): continue
    info=sorted(set((ti.loc[q,'video_id'].replace('simulation_',''),)+nf(ti.loc[q,'video_id'])+(ti.loc[q,'scen'],) for q in qs))
    print(gr['kind'], ti.loc[qs[0],'question'][:55], info)
